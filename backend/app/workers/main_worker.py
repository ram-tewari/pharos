"""
Pharos Unified Edge Worker

Single long-running process that:
  - Loads the local embedding model (RTX 4070).
  - Serves the FastAPI /embed endpoint on port EDGE_EMBED_PORT (default 8001).
  - Blocks on BOTH Redis queues with one connection:
        BLPOP pharos:tasks ingest_queue 30
    Routing by source queue:
        pharos:tasks   -> resource-level ingestion (process_ingestion)
        ingest_queue   -> repo-level clone/parse/embed/store

Upstash quota note: timeout=30s caps idle commands at ~2,880/day, well under
the 100,000/month free tier. DO NOT lower the timeout without re-doing the math.

Usage:
    python worker.py            # via dispatcher
    python -m app.workers.main_worker
    bash start_worker.sh        # bulletproof launcher
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Queue keys are exported so the dispatch banner in start_worker.sh stays in sync.
RESOURCE_QUEUE = "pharos:tasks"
REPO_QUEUE = "ingest_queue"
QUEUES = [RESOURCE_QUEUE, REPO_QUEUE]
BLPOP_TIMEOUT_SECONDS = 30


# ---------------------------------------------------------------------------
# Boot checks
# ---------------------------------------------------------------------------

def check_environment() -> None:
    """Validate required environment variables for EDGE mode."""
    required = [
        "MODE",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN",
        "DATABASE_URL",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        logger.error(f"Missing required env vars: {', '.join(missing)}")
        sys.exit(1)

    if os.getenv("MODE") != "EDGE":
        logger.error(f"MODE must be 'EDGE', got: {os.getenv('MODE')!r}")
        sys.exit(1)

    logger.info("Environment validated (MODE=EDGE)")


def check_gpu() -> str:
    """Log GPU status; never abort if CUDA is missing."""
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            mem = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"GPU: {name} ({mem:.1f} GB), CUDA {torch.version.cuda}")
            return "cuda"
        logger.warning("CUDA unavailable — falling back to CPU")
        return "cpu"
    except ImportError:
        logger.error("PyTorch not installed; install requirements-edge.txt")
        sys.exit(1)


def load_embedding_model():
    from app.shared.embeddings import EmbeddingService

    logger.info("Loading embedding model...")
    t0 = time.time()
    svc = EmbeddingService()
    if not svc.warmup():
        logger.error("Embedding warmup failed")
        sys.exit(1)
    logger.info(f"Embedding model ready in {time.time() - t0:.1f}s")
    return svc


async def connect_to_redis():
    from app.shared.upstash_redis import UpstashRedisClient

    client = UpstashRedisClient()
    if not await client.ping():
        logger.error("Upstash PING failed")
        sys.exit(1)
    logger.info("Upstash Redis connected")
    return client


async def connect_to_database():
    from app.config.settings import get_settings
    from app.shared.database import get_db, init_database

    settings = get_settings()
    db_url = settings.get_database_url()
    init_database(db_url, env=settings.ENV)
    logger.info("Database connected")
    return get_db


# ---------------------------------------------------------------------------
# Resource-level handler (formerly edge.py / process_task)
# ---------------------------------------------------------------------------

async def handle_resource_task(task: Dict[str, Any]) -> bool:
    """Run the full single-resource ingestion pipeline in a worker thread."""
    task_id = task.get("task_id")
    resource_id = task.get("resource_id")
    if resource_id is None:
        logger.error(f"resource task {task_id} missing resource_id; payload={task}")
        return False

    logger.info(f"[RESOURCE] task={task_id} resource_id={resource_id}")

    def _run_sync() -> bool:
        from app.modules.resources.service import process_ingestion
        try:
            t0 = time.time()
            process_ingestion(resource_id=resource_id)
            logger.info(
                f"[RESOURCE] resource_id={resource_id} done in {time.time() - t0:.1f}s"
            )
            return True
        except Exception as exc:
            logger.error(
                f"[RESOURCE] resource_id={resource_id} failed: {exc}",
                exc_info=True,
            )
            return False

    return await asyncio.get_event_loop().run_in_executor(None, _run_sync)


# ---------------------------------------------------------------------------
# Repository handler (formerly RepositoryWorker in repo.py)
# ---------------------------------------------------------------------------

class RepositoryIngestor:
    """Thin worker-side wrapper around HybridIngestionPipeline.

    The pipeline does the actual work (multi-language clone + chunk + embed +
    persist with proper vector CAST). We just hand it the worker's GPU-loaded
    EmbeddingService so we don't load a second model.
    """

    # Languages we walk into. Linux is C/C++/headers; the rest cover the
    # common cases the search backend already knows how to render.
    _DEFAULT_EXTENSIONS: tuple[str, ...] = (
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".go", ".rs", ".java", ".kt", ".scala",
        ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx",
        ".rb", ".php", ".swift",
    )

    def __init__(self, embedding_service):
        self.embedding_service = embedding_service

    async def ingest(self, task: Dict[str, Any]) -> bool:
        repo_url = task.get("repo_url") or task.get("payload")
        if not repo_url:
            logger.error(f"[REPO] task missing repo_url: {task}")
            return False

        # Pipeline requires an https:// clone URL; normalize bare github.com/x/y.
        if not repo_url.startswith(("http://", "https://")):
            repo_url = f"https://{repo_url}"

        # Branch is optional — when absent we let git pick the default
        # (Linux uses `master`, modern repos use `main`).
        branch = task.get("branch") or None
        extensions = tuple(task.get("file_extensions") or self._DEFAULT_EXTENSIONS)

        started = datetime.now()
        logger.info(f"[REPO] ingest {repo_url} (branch={branch or 'default'})")

        from app.modules.ingestion.ast_pipeline import HybridIngestionPipeline
        from app.shared.database import get_db

        try:
            async for session in get_db():
                pipeline = HybridIngestionPipeline(
                    db=session,
                    embedding_service=self.embedding_service,
                )
                result = await pipeline.ingest_github_repo(
                    git_url=repo_url,
                    branch=branch,
                    file_extensions=extensions,
                )
                duration = (datetime.now() - started).total_seconds()
                logger.info(
                    f"[REPO] {repo_url} done | "
                    f"resources={result.resources_created} "
                    f"chunks={result.chunks_created} "
                    f"failed={result.files_failed} "
                    f"duration={duration:.1f}s"
                )
                return result.resources_created > 0
            return False
        except Exception as exc:
            logger.error(f"[REPO] {repo_url} failed: {exc}", exc_info=True)
            return False

# ---------------------------------------------------------------------------
# FastAPI /embed server (kept from edge.py)
# ---------------------------------------------------------------------------

async def run_embed_server(embedding_service) -> None:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Body

    app = FastAPI(title="Pharos Edge Embed Server", docs_url=None, redoc_url=None)

    # Use Body() instead of a Pydantic model defined in this local scope.
    # Locally-scoped Pydantic models break FastAPI's body-parameter inference
    # and the parameter falls back to a query param — causing every Render
    # call to /embed to 422 with `loc:["query","req"]`.
    @app.post("/embed")
    def embed(text: str = Body(..., embed=True)) -> dict:
        text = (text or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="text must be non-empty")
        vec = embedding_service.generate_embedding(text)
        if not vec:
            raise HTTPException(status_code=503, detail="model unavailable")
        return {"embedding": vec}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "model": embedding_service.embedding_generator.model_name}

    port = int(os.getenv("EDGE_EMBED_PORT", "8001"))
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info", access_log=False)
    logger.info(f"FastAPI /embed listening on 127.0.0.1:{port}")
    await uvicorn.Server(config).serve()


# ---------------------------------------------------------------------------
# Unified poll/dispatch loop
# ---------------------------------------------------------------------------

async def poll_and_dispatch(redis_client, embedding_service) -> None:
    """One BLPOP, two queues. Route by source queue, never crash on a poison pill."""
    repo_ingestor = RepositoryIngestor(embedding_service)
    processed = 0
    failed = 0

    logger.info(
        f"Polling {QUEUES} with BLPOP timeout={BLPOP_TIMEOUT_SECONDS}s "
        f"(~{86400 // BLPOP_TIMEOUT_SECONDS} idle cmds/day)"
    )

    while True:
        try:
            popped = await redis_client.pop_from_queues(
                QUEUES, timeout=BLPOP_TIMEOUT_SECONDS
            )
            if popped is None:
                continue  # idle, just re-block

            queue_key, task = popped
            task_id = task.get("task_id")
            try:
                if queue_key == REPO_QUEUE:
                    success = await repo_ingestor.ingest(task)
                elif queue_key == RESOURCE_QUEUE:
                    success = await handle_resource_task(task)
                else:
                    logger.warning(f"Unknown queue {queue_key!r}; dropping task")
                    success = False

                if task_id:
                    await redis_client.update_task_status(
                        task_id, "completed" if success else "failed"
                    )
                processed += int(success)
                failed += int(not success)
                logger.info(f"Totals: processed={processed} failed={failed}")
            except Exception as exc:
                # Poison-pill containment: log + mark failed, keep the loop alive.
                failed += 1
                logger.error(
                    f"Handler crash on queue={queue_key} task={task_id}: {exc}",
                    exc_info=True,
                )
                if task_id:
                    try:
                        await redis_client.update_task_status(task_id, "failed")
                    except Exception:
                        logger.exception("Failed to mark task as failed")
        except KeyboardInterrupt:
            logger.info("Shutdown requested; exiting dispatch loop")
            return
        except Exception as exc:
            # Outer guard: never let a transport blip kill the worker.
            logger.error(f"Dispatch loop error: {exc}", exc_info=True)
            await asyncio.sleep(2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.info("=" * 64)
    logger.info("Pharos Unified Edge Worker")
    logger.info(f"Queues : {QUEUES}")
    logger.info(f"BLPOP  : {BLPOP_TIMEOUT_SECONDS}s timeout (Upstash quota-safe)")
    logger.info("=" * 64)

    check_environment()
    check_gpu()
    embedding_service = load_embedding_model()
    redis_client = await connect_to_redis()
    await connect_to_database()

    logger.info("Boot complete; serving /embed and dispatching tasks")

    await asyncio.gather(
        run_embed_server(embedding_service),
        poll_and_dispatch(redis_client, embedding_service),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        sys.exit(1)
