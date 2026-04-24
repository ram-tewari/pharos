"""
Queue existing pending resources to pharos:tasks for processing.

This script finds all resources with ingestion_status="pending" and queues them
to the pharos:tasks queue for the edge worker to process.

Usage:
    python backend/scripts/queue_pending_resources.py
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.models import Resource
from app.shared.upstash_redis import UpstashRedisClient


async def main():
    """Queue all pending resources to pharos:tasks."""
    
    # Connect to database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    
    print(f"Connecting to database...")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Get all pending resources
    print("Fetching pending resources...")
    resources = db.execute(
        select(Resource).filter(Resource.ingestion_status == "pending")
    ).scalars().all()
    
    print(f"Found {len(resources)} pending resources")
    
    if len(resources) == 0:
        print("No pending resources to queue")
        return
    
    # Show sample
    print("\nSample resources:")
    for i, resource in enumerate(resources[:5]):
        print(f"  {i+1}. {resource.title} (ID: {resource.id})")
    if len(resources) > 5:
        print(f"  ... and {len(resources) - 5} more")
    
    # Confirm
    response = input(f"\nQueue {len(resources)} resources to pharos:tasks? (y/n): ")
    if response.lower() != 'y':
        print("Aborted")
        return
    
    # Queue to pharos:tasks
    print("\nQueuing resources...")
    redis = UpstashRedisClient()
    
    queued = 0
    failed = 0
    
    try:
        for i, resource in enumerate(resources):
            try:
                task = {
                    "task_id": str(uuid.uuid4()),
                    "resource_id": str(resource.id)
                }
                await redis.push_task(task)
                queued += 1
                
                if (i + 1) % 100 == 0:
                    print(f"  Queued {i + 1}/{len(resources)}...")
            
            except Exception as e:
                print(f"  ERROR queuing resource {resource.id}: {e}")
                failed += 1
        
        print(f"\nDone!")
        print(f"  Queued: {queued}")
        print(f"  Failed: {failed}")
        print(f"\nEdge worker will process these tasks automatically.")
        print(f"Monitor progress with: tail -f backend/edge_worker.log")
    
    finally:
        await redis.close()
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
