# Chunking Diagnosis - April 17, 2026

## Problem Statement

Resources are being ingested successfully (status=completed), but NO chunks are being created even though:
- `CHUNK_ON_RESOURCE_CREATE=true` (verified in Render environment)
- `GRAPH_EXTRACT_ON_CHUNK=true` (verified in Render environment)
- Settings are loading correctly (verified locally)

## Evidence

### Configuration ✅
```
MODE: CLOUD
CHUNK_ON_RESOURCE_CREATE: True
CHUNKING_STRATEGY: semantic
CHUNK_SIZE: 500
CHUNK_OVERLAP: 50
GRAPH_EXTRACT_ON_CHUNK: True
```

### Resource Status ✅
```
Resource ID: 0811a2fc-b05d-4b0d-91ad-91c44e2ed4df
Title: FastAPI - Modern Python Web Framework
Ingestion Status: completed
Created: 2026-04-17T06:51:54.109018Z
Updated: 2026-04-17T06:55:36.441755Z
```

### Chunks Status ❌
```
Chunk Count: 0
```

## Root Cause Analysis

Looking at `backend/app/modules/resources/service.py` lines 651-714:

```python
try:
    from ...config.settings import get_settings
    settings = get_settings()
    chunk_on_create = getattr(settings, "CHUNK_ON_RESOURCE_CREATE", True)

    if chunk_on_create and text_clean:
        logger.info(f"[INGESTION] {resource_id} - Starting chunking ({len(text_clean)} chars)")
        
        # Create chunking service
        chunking_service = ChunkingService(
            db=session,
            strategy=chunking_strategy,
            chunk_size=chunk_size,
            overlap=chunk_overlap,
            parser_type="text",
            embedding_service=ai_core,
        )
        
        # Chunk the content
        chunks = chunking_service.chunk_resource(
            resource_id=str(resource.id),
            content=text_clean,
            chunk_metadata=base_chunk_metadata,
        )
        logger.info(f"[INGESTION] {resource_id} - Successfully chunked: {len(chunks)} chunks created")
except Exception as chunk_error:
    # Log error but don't fail ingestion - chunking is optional
    logger.error(f"Chunking failed for resource {resource_id}: {chunk_error}", exc_info=True)
    logger.warning(f"Resource {resource_id} will be created without chunks")
```

**The chunking code is wrapped in a try-except that catches ALL exceptions and continues.**

## Possible Causes

### 1. ChunkingService Import Failure
- ChunkingService is defined in the same file (line 1408)
- Import should work, but could fail if there are circular dependencies

### 2. Content Too Short
- Chunking requires `text_clean` to have content
- If `text_clean` is empty or too short, chunking is skipped
- But we should see a log message: "Starting chunking (X chars)"

### 3. Database Session Issues
- ChunkingService needs a valid database session
- If session is invalid or closed, chunk creation will fail
- Chunks might be created but not committed

### 4. Embedding Service Failure
- ChunkingService uses `ai_core` for embeddings
- If embedding generation fails, chunking might fail
- But this should be logged

### 5. Silent Exception
- Exception is caught and logged, but we're not seeing the logs
- Need to check Render logs or edge worker logs

## Verification Steps

### Step 1: Check Edge Worker Logs
The edge worker should show:
```
[INGESTION] {resource_id} - Starting chunking (X chars)
```

If we DON'T see this message, then:
- Either `chunk_on_create` is False (but we verified it's True)
- Or `text_clean` is empty/None

If we DO see this message but no "Successfully chunked" message, then:
- ChunkingService.chunk_resource() is failing
- Exception is being caught and logged

### Step 2: Test Chunking Locally
Create a minimal test to verify ChunkingService works:

```python
from app.modules.resources.service import ChunkingService
from app.shared.database import SessionLocal, init_database
from app.shared.ai_core import AICore

init_database()
db = SessionLocal()
ai_core = AICore()

chunking_service = ChunkingService(
    db=db,
    strategy="semantic",
    chunk_size=500,
    overlap=50,
    parser_type="text",
    embedding_service=ai_core,
)

test_content = "This is a test document. " * 100  # 500+ chars

chunks = chunking_service.chunk_resource(
    resource_id="test-resource-id",
    content=test_content,
    chunk_metadata={"source": "test"},
)

print(f"Created {len(chunks)} chunks")
```

### Step 3: Check Render Logs
Go to Render dashboard → pharos-cloud-api → Logs
Search for:
- "Starting chunking"
- "Chunking failed"
- "ChunkingService"
- Any exceptions during ingestion

## Hypothesis

**Most Likely**: The edge worker is processing the resource, but the chunking code is failing silently due to:
1. Database session issues (async vs sync)
2. Missing dependencies (spaCy, sentence-transformers)
3. Memory/resource constraints on edge worker

**Evidence Needed**: Edge worker logs showing the actual error

## Solution Path

### Option A: Fix Chunking in Edge Worker
1. Check edge worker logs for errors
2. Fix the root cause (likely database or dependencies)
3. Re-ingest resource to test

### Option B: Move Chunking to Cloud API
1. Chunk immediately after resource creation in Cloud API
2. Don't rely on edge worker for chunking
3. Edge worker only does embedding generation

### Option C: Separate Chunking Task
1. Create separate task queue for chunking
2. Cloud API queues chunking task after ingestion completes
3. Edge worker processes chunking tasks separately

## Recommended Action

**Immediate**: Check edge worker logs to see the actual error

**Short-term**: Add more detailed logging to chunking code:
```python
logger.info(f"Chunking config: chunk_on_create={chunk_on_create}, text_length={len(text_clean)}")
logger.info(f"Creating ChunkingService...")
logger.info(f"Calling chunk_resource...")
```

**Long-term**: Move chunking to Cloud API to avoid edge worker complexity

## Status

- ⏳ Waiting for edge worker logs
- 📋 Need to verify ChunkingService works locally
- 🔍 Need to identify root cause of silent failure

---

**Last Updated**: 2026-04-17 03:40 UTC
**Reporter**: Kiro AI Assistant
**Priority**: High (blocks graph extraction)
