"""
Edge Worker for Hybrid Edge-Cloud Architecture

This worker runs locally on GPU-enabled hardware and processes resource
ingestion tasks from the Upstash Redis queue. It performs:
1. Content fetching and extraction
2. AI summarization and tagging (GPU-accelerated)
3. Embedding generation (GPU-accelerated)
4. Semantic chunking with embeddings
5. Database storage (NeonDB PostgreSQL)

Requirements: MODE=EDGE in .env
"""

import os
import sys
import time
import json
import asyncio
import signal
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify MODE is set to EDGE
if os.getenv("MODE") != "EDGE":
    print("[ERROR] Configuration Error: MODE must be set to 'EDGE' in .env")
    print("   Current MODE:", os.getenv("MODE"))
    sys.exit(1)

# Import services
try:
    import requests
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.shared.database import get_db
    from app.shared.embeddings import EmbeddingGenerator
    from app.shared.ai_core import AICore
    from app.config.settings import get_settings
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("Make sure you've installed all requirements")
    sys.exit(1)


class EdgeWorker:
    """
    Edge Worker that processes resource ingestion tasks.

    Polls Redis queue for tasks, processes them using GPU acceleration,
    and stores results in PostgreSQL.
    """

    def __init__(self):
        """Initialize the edge worker with credential validation."""
        print("[INIT] Initializing edge worker...")
        sys.stdout.flush()
        
        # Validate Redis credentials
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

        print(f"[INIT] Redis URL: {redis_url[:50]}..." if redis_url else "[ERROR] No Redis URL")
        sys.stdout.flush()

        if not redis_url:
            print("[ERROR] Configuration Error: UPSTASH_REDIS_REST_URL not set")
            sys.exit(1)

        if not redis_token:
            print("[ERROR] Configuration Error: UPSTASH_REDIS_REST_TOKEN not set")
            sys.exit(1)

        self.redis_url = redis_url
        self.redis_token = redis_token
        self.queue_key = "pharos:tasks"

        # Test Redis connection
        print("[INIT] Testing Redis connection...")
        sys.stdout.flush()
        
        try:
            response = requests.post(
                self.redis_url,
                headers={"Authorization": f"Bearer {self.redis_token}"},
                json=["PING"],
                timeout=5,
            )
            if response.status_code == 200:
                print("[OK] Connected to Upstash Redis")
                sys.stdout.flush()
            else:
                print(f"[ERROR] Redis connection failed: {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Redis connection error: {e}")
            sys.exit(1)

        # Initialize database
        print("[INIT] Initializing database...")
        sys.stdout.flush()
        
        from app.shared.database import init_database
        # Initialize with simpler pooling for edge worker
        os.environ["DB_POOL_SIZE"] = "1"
        os.environ["DB_MAX_OVERFLOW"] = "2"
        init_database()
        print("[OK] Database initialized")
        sys.stdout.flush()

        # Initialize services
        print("[INIT] Initializing services...")
        sys.stdout.flush()
        
        self.settings = get_settings()
        print("[OK] Settings loaded")
        sys.stdout.flush()
        
        self.ai_core = AICore()
        print("[OK] AI Core initialized")
        sys.stdout.flush()
        
        self.embedding_generator = EmbeddingGenerator()
        print("[OK] Embedding generator created")
        sys.stdout.flush()

        # Load embedding model on GPU
        print("[INIT] Loading embedding model on GPU...")
        sys.stdout.flush()
        
        try:
            # Warm up the model
            test_embedding = self.embedding_generator.generate_embedding("test")
            if test_embedding is not None:
                print(f"[OK] Loaded embedding model: {self.embedding_generator.model_name} ({len(test_embedding)}d)")
                sys.stdout.flush()
            else:
                print("[WARN] Warning: Embedding model loaded but returned None")
                sys.stdout.flush()
        except Exception as e:
            print(f"[ERROR] Failed to load embedding model: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Shutdown flag
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        print("[OK] Edge worker initialized")
        print()
        sys.stdout.flush()

    def _handle_shutdown(self, signum, frame):
        """Handle SIGINT/SIGTERM for graceful shutdown."""
        print("\n[SHUTDOWN] Shutdown signal received. Finishing current job...")
        self.shutdown_requested = True

    def _redis_command(self, command: list) -> Optional[any]:
        """Execute a Redis command via REST API."""
        try:
            response = requests.post(
                self.redis_url,
                headers={"Authorization": f"Bearer {self.redis_token}"},
                json=command,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("result")
            else:
                print(f"[WARN] Redis command failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[WARN] Redis error: {e}")
            return None

    async def process_ingestion(self, task_data: Dict) -> None:
        """
        Process a resource ingestion task.

        Args:
            task_data: Task metadata containing resource_id
        """
        job_start = datetime.now()
        resource_id = task_data.get("resource_id")

        print(f"[TASK] Received task: {task_data.get('operation')} resource {resource_id}")

        try:
            # Get database session
            async for session in get_db():
                # Import here to avoid circular imports
                from app.modules.resources.model import Resource
                from sqlalchemy import select

                # Fetch resource
                result = await session.execute(
                    select(Resource).where(Resource.id == resource_id)
                )
                resource = result.scalar_one_or_none()

                if not resource:
                    print(f"[ERROR] Resource not found: {resource_id}")
                    return

                print(f"[TASK] Processing: {resource.title}")
                print(f"[TASK] URL: {resource.source}")

                # Run ingestion pipeline
                from app.modules.resources.service import process_ingestion as run_ingestion

                # Call the ingestion function (it's synchronous, not async)
                run_ingestion(
                    resource_id=str(resource.id),
                    archive_root=None,  # Use default
                )

                # Commit changes
                await session.commit()

                job_end = datetime.now()
                duration = (job_end - job_start).total_seconds()

                print(f"[OK] Ingestion completed in {duration:.2f}s")
                print()

                # Break after first session
                break

        except Exception as e:
            print(f"[ERROR] Error processing task: {e}")
            import traceback
            traceback.print_exc()
            print()

    def run(self) -> None:
        """Main worker loop that polls queue every 2 seconds."""
        print("[WORKER] Polling Redis queue every 2 seconds...")
        print("[WORKER] Press Ctrl+C to stop")
        print()

        while not self.shutdown_requested:
            try:
                # Poll for tasks (BLPOP with 2 second timeout)
                result = self._redis_command(["BLPOP", self.queue_key, "2"])

                if result and len(result) == 2:
                    # BLPOP returns [key, value]
                    task_json = result[1]

                    # Parse task data
                    try:
                        task_data = json.loads(task_json)
                    except json.JSONDecodeError:
                        print(f"[WARN] Invalid task JSON: {task_json}")
                        continue

                    # Process task
                    asyncio.run(self.process_ingestion(task_data))

            except KeyboardInterrupt:
                print("\n[SHUTDOWN] Shutting down gracefully...")
                break

            except Exception as e:
                print(f"[ERROR] Worker error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)

        print("[SHUTDOWN] Edge worker stopped")


def main():
    """Main entry point for the edge worker."""
    print("=" * 60)
    print("Pharos Edge Worker")
    print("=" * 60)
    print()

    # Create and run worker
    worker = EdgeWorker()
    worker.run()


if __name__ == "__main__":
    main()
