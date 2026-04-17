"""
Diagnostic script to check why chunking isn't working.
"""
import asyncio
import logging
from app.config.settings import get_settings
from app.shared.database import SessionLocal
from app.database.models import Resource, DocumentChunk
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def diagnose():
    """Check chunking configuration and database state."""
    
    # Check settings
    settings = get_settings()
    logger.info("=== CHUNKING CONFIGURATION ===")
    logger.info(f"MODE: {settings.MODE}")
    logger.info(f"CHUNK_ON_RESOURCE_CREATE: {settings.CHUNK_ON_RESOURCE_CREATE}")
    logger.info(f"CHUNKING_STRATEGY: {settings.CHUNKING_STRATEGY}")
    logger.info(f"CHUNK_SIZE: {settings.CHUNK_SIZE}")
    logger.info(f"CHUNK_OVERLAP: {settings.CHUNK_OVERLAP}")
    logger.info(f"GRAPH_EXTRACT_ON_CHUNK: {settings.GRAPH_EXTRACT_ON_CHUNK}")
    
    # Initialize database
    from app.shared.database import init_database
    init_database()
    
    # Check database
    from app.shared.database import SessionLocal as SL
    db = SL()
    try:
        logger.info("\n=== DATABASE STATE ===")
        
        # Count resources
        result = db.execute(select(Resource))
        resources = result.scalars().all()
        logger.info(f"Total resources: {len(resources)}")
        
        # Count chunks
        result = db.execute(select(DocumentChunk))
        chunks = result.scalars().all()
        logger.info(f"Total chunks: {len(chunks)}")
        
        # Show recent resources
        logger.info("\n=== RECENT RESOURCES ===")
        for resource in resources[-3:]:
            logger.info(f"Resource {resource.id}:")
            logger.info(f"  Title: {resource.title}")
            logger.info(f"  Status: {resource.ingestion_status}")
            logger.info(f"  Created: {resource.created_at}")
            logger.info(f"  Description length: {len(resource.description or '')}")
            
            # Count chunks for this resource
            result = db.execute(
                select(DocumentChunk).filter(DocumentChunk.resource_id == resource.id)
            )
            resource_chunks = result.scalars().all()
            logger.info(f"  Chunks: {len(resource_chunks)}")
            
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(diagnose())
