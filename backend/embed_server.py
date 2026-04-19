"""
Pharos Edge Embedding Server

Standalone FastAPI service that exposes POST /embed for on-demand query
embedding. Render's cloud API calls this endpoint via Tailscale Funnel
when MODE=CLOUD, instead of loading sentence-transformers locally.

Run via NSSM service (PharosEmbedServer) or manually:
    uvicorn embed_server:app --host 127.0.0.1 --port 8001

Environment:
    MODE=EDGE                        (required — prevents cloud-mode guard in EmbeddingGenerator)
    EDGE_EMBED_PORT=8001             (optional, used by start command only)
    EMBEDDING_MODEL_NAME             (optional, default: nomic-ai/nomic-embed-text-v1)

Note on nomic-embed-text-v1 prefixes:
    The model supports search_document: / search_query: prefixes for improved
    retrieval performance, but documents in NeonDB were ingested WITHOUT any
    prefix. This endpoint therefore passes raw text to the model so that query
    embeddings land in the same embedding space as stored document vectors.
    See ADR-013 in docs/architecture/decisions.md.
"""

import os
import logging
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pharos Edge Embedding Server", docs_url=None, redoc_url=None)

# Single model instance shared across all requests — loaded once at startup.
_generator = None


@app.on_event("startup")
def _startup() -> None:
    global _generator
    from app.shared.embeddings import EmbeddingGenerator

    model_name = os.getenv("EMBEDDING_MODEL_NAME", "nomic-ai/nomic-embed-text-v1")
    logger.info(f"Loading embedding model: {model_name}")
    _generator = EmbeddingGenerator(model_name=model_name)
    _generator._ensure_loaded()
    if _generator._model is None:
        logger.error("Embedding model failed to load — aborting startup")
        sys.exit(1)
    logger.info(f"Embedding model ready on {_generator.device}")


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest) -> EmbedResponse:
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must be non-empty")

    vec = _generator.generate_embedding(text)
    if not vec:
        raise HTTPException(status_code=503, detail="model unavailable")

    return EmbedResponse(embedding=vec)


@app.get("/health")
def health() -> dict:
    ready = _generator is not None and _generator._model is not None
    if not ready:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ok", "model": _generator.model_name}
