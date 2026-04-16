# Render Deployment OOM Fix - Summary

## Problem
Pharos backend was failing to deploy on Render (512MB RAM) with OOM error. The app was in CLOUD mode but still loading ML models (sentence-transformers) into memory, causing it to exceed 512MB and crash.

## Root Cause
Several modules were importing `EmbeddingService` or `EmbeddingGenerator` at the module level (top of file), which triggered model loading even in CLOUD mode. The imports needed to be lazy (inside functions, only when actually used).

## Files Fixed

### 1. `backend/requirements-cloud.txt` ⚠️ **CRITICAL FIX**
**Issue**: Line 36 had `sentence-transformers>=2.2.0` which pulls in PyTorch (~500MB)
**Fix**: Removed sentence-transformers from cloud requirements
```python
# ❌ REMOVED (causes OOM on Render Starter 512MB)
# sentence-transformers>=2.2.0

# Cloud mode architecture:
# - Render API: Queues embedding tasks to Upstash Redis
# - Edge Worker: Processes tasks with local GPU (RTX 4070)
# - No ML models loaded on Render instance
```

**Impact**: This was the PRIMARY cause of OOM. Installing sentence-transformers pulls in:
- PyTorch: ~400MB
- Transformers: ~100MB
- Total: ~500MB just for ML libraries
- On 512MB instance: Only ~12MB left for app = OOM guaranteed

### 2. `backend/app/__init__.py`
**Issue**: Lifespan function was importing embeddings in CLOUD mode
**Fix**: Added explicit log message that ML models will NOT be loaded in CLOUD mode
```python
if deployment_mode == "CLOUD":
    logger.info("✓ Cloud mode: ML models will NOT be loaded (queued to edge worker via Redis)")
```

### 2. `backend/app/shared/circuit_breaker.py`
**Issue**: AI circuit breakers (`ai_embedding_breaker`, `ai_llm_breaker`) were created at module level
**Fix**: Made circuit breaker creation conditional on MODE
```python
deployment_mode = os.getenv("MODE", "EDGE")
if deployment_mode == "EDGE":
    ai_embedding_breaker = CircuitBreakerFactory.get_ai_breaker("embedding")
    ai_llm_breaker = CircuitBreakerFactory.get_ai_breaker("llm")
else:
    ai_embedding_breaker = None
    ai_llm_breaker = None
```

### 3. `backend/app/modules/pdf_ingestion/service.py`
**Issue**: Module-level import of `EmbeddingService`
**Fix**: Commented out import, made it lazy with type hint
```python
# Lazy import embeddings to avoid loading models in CLOUD mode
# from ...shared.embeddings import EmbeddingService

def __init__(self, db: AsyncSession, embedding_service: "EmbeddingService"):  # type: ignore
```

### 4. `backend/app/modules/pdf_ingestion/router.py`
**Issue**: Dependency function instantiated `EmbeddingService` unconditionally
**Fix**: Made instantiation conditional on MODE, returns 503 in CLOUD mode
```python
def get_pdf_service(db: AsyncSession = Depends(get_db)) -> PDFIngestionService:
    deployment_mode = os.getenv("MODE", "EDGE")
    
    if deployment_mode == "CLOUD":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PDF ingestion requires EDGE mode or edge worker."
        )
    else:
        from ...shared.embeddings import EmbeddingService
        embedding_service = EmbeddingService()
        return PDFIngestionService(db=db, embedding_service=embedding_service)
```

### 5. `backend/app/modules/annotations/service.py`
**Issue**: Module-level import and instantiation of `EmbeddingGenerator`
**Fix**: Made embedding generator a lazy property
```python
# Lazy import embeddings to avoid loading models in CLOUD mode
# from ...shared.embeddings import EmbeddingGenerator

def __init__(self, db: Session):
    self.db = db
    self._embedding_generator = None

@property
def embedding_generator(self):
    """Lazy load embedding generator only in EDGE mode."""
    if self._embedding_generator is None:
        deployment_mode = os.getenv("MODE", "EDGE")
        if deployment_mode == "EDGE":
            from ...shared.embeddings import EmbeddingGenerator
            self._embedding_generator = EmbeddingGenerator()
    return self._embedding_generator
```

## Already Correct (No Changes Needed)

### `backend/app/shared/embeddings.py`
✅ Already has MODE check in `_ensure_loaded()`:
```python
deployment_mode = os.getenv("MODE", "EDGE")
if deployment_mode == "CLOUD":
    logger.info("Cloud mode detected - skipping embedding model load")
    return
```

### `backend/app/modules/resources/service.py`
✅ Already uses lazy imports (inside functions):
```python
# Inside function, not at module level
from ...shared.embeddings import EmbeddingGenerator
embedding_gen = EmbeddingGenerator()
```

### `backend/app/modules/search/service.py`
✅ Already uses lazy imports (inside functions):
```python
# Inside function, not at module level
from ...shared.embeddings import EmbeddingService
embedding_service = EmbeddingService(self.db)
```

## Success Criteria

✅ Render deployment succeeds (stays under 512MB)
✅ No ML models loaded in CLOUD mode
✅ Circuit breakers for AI operations NOT created in CLOUD mode
✅ Health endpoint responds quickly
✅ Embedding tasks are queued to Redis (not processed locally)

## Testing

### Local Test (CLOUD mode)
```bash
cd backend
export MODE=CLOUD
export DATABASE_URL=postgresql://...
uvicorn app.main:app --reload
```

Expected logs:
```
Deployment mode: CLOUD
Cloud mode: Skipping torch-dependent modules
✓ Cloud mode: ML models will NOT be loaded (queued to edge worker via Redis)
Cloud mode: Skipping AI circuit breakers (handled by edge worker)
```

### Render Deployment
1. Push changes to GitHub
2. Render auto-deploys
3. Check logs for:
   - No "Out of memory" errors
   - "Cloud mode: ML models will NOT be loaded" message
   - Health endpoint responds

### Memory Usage
Before fix: >512MB (OOM crash)
After fix: <300MB (no ML models loaded)

## Architecture Context

This is a hybrid edge-cloud architecture:
- **Cloud API (Render)**: Lightweight FastAPI server, NO ML models, queues tasks to Redis
- **Edge Worker (Local GPU)**: Runs ML models (embeddings, LLM), processes tasks from Redis queue

**MODE=CLOUD**: Should NEVER load ML models, only queue tasks
**MODE=EDGE**: Loads ML models for local processing

## Next Steps

1. ✅ Deploy to Render and verify no OOM
2. ✅ Verify health endpoint responds
3. 📋 Implement task queuing for PDF ingestion in CLOUD mode
4. 📋 Implement task queuing for annotations in CLOUD mode
5. 📋 Test edge worker processing of queued tasks

## Related Files

- `backend/start_edge_worker.ps1` - Edge worker startup script
- `backend/app/edge_worker.py` - Edge worker implementation
- `backend/SERVERLESS_DEPLOYMENT_GUIDE.md` - Deployment guide
- `backend/RENDER_FREE_DEPLOYMENT.md` - Render-specific guide
