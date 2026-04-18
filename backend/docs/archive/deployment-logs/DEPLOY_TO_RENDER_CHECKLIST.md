# Deploy to Render - OOM Fix Checklist

## Pre-Deployment Verification

### 1. Run Local Verification
```bash
cd backend
python verify_cloud_mode.py
```

Expected output:
```
✓ ALL CHECKS PASSED
The app can start in CLOUD mode without loading ML models.
Expected memory usage: <300MB (without ML models)
```

### 2. Check Environment Variables
Ensure these are set in Render dashboard:
- `MODE=CLOUD` ✅ (Critical - prevents ML model loading)
- `DATABASE_URL=postgresql://...` ✅ (Your Render PostgreSQL URL)
- `WEB_CONCURRENCY=1` ✅ (Minimize memory usage)
- `ENV=prod` ✅ (Production mode)

### 3. Verify Changes
Files modified to fix OOM:
- ✅ `app/__init__.py` - Added explicit CLOUD mode logging
- ✅ `app/shared/circuit_breaker.py` - Conditional AI circuit breaker creation
- ✅ `app/modules/pdf_ingestion/service.py` - Lazy embedding import
- ✅ `app/modules/pdf_ingestion/router.py` - Conditional embedding instantiation
- ✅ `app/modules/annotations/service.py` - Lazy embedding property

## Deployment Steps

### 1. Commit and Push
```bash
git add .
git commit -m "Fix OOM: Make embedding imports lazy and conditional on MODE"
git push origin main
```

### 2. Monitor Render Deployment
1. Go to Render dashboard
2. Watch deployment logs
3. Look for these success indicators:

**Expected logs:**
```
Deployment mode: CLOUD
Cloud mode: Skipping torch-dependent modules
✓ Cloud mode: ML models will NOT be loaded (queued to edge worker via Redis)
Cloud mode: Skipping AI circuit breakers (handled by edge worker)
Module registration complete: X modules registered
Neo Alexandria 2.0 startup complete
```

**Should NOT see:**
```
Out of memory (used over 512Mi)  ❌
Loading embedding model...  ❌
Created circuit breaker 'ai_embedding'  ❌
```

### 3. Test Health Endpoint
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "pharos-api"
}
```

### 4. Check Memory Usage
In Render dashboard:
- Memory usage should be <300MB
- Should stay stable (no gradual increase)
- No OOM crashes

## Post-Deployment Verification

### 1. Test API Endpoints
```bash
# Health check
curl https://your-app.onrender.com/health

# Monitoring health (if available)
curl https://your-app.onrender.com/api/monitoring/health

# Auth endpoints (should work)
curl https://your-app.onrender.com/api/auth/health
```

### 2. Test Endpoints That Should Return 503
These endpoints require EDGE mode (ML models):
```bash
# PDF ingestion (should return 503)
curl -X POST https://your-app.onrender.com/api/resources/pdf/ingest \
  -F "file=@test.pdf" \
  -F "title=Test"

# Expected: 503 Service Unavailable
# "PDF ingestion requires EDGE mode or edge worker"
```

### 3. Monitor for 24 Hours
- Check memory usage stays <300MB
- Check no OOM crashes
- Check health endpoint responds consistently

## Rollback Plan

If deployment fails:

### Option 1: Revert Changes
```bash
git revert HEAD
git push origin main
```

### Option 2: Disable Problematic Modules
In `app/__init__.py`, comment out modules that cause issues:
```python
# ("pdf_ingestion", "app.modules.pdf_ingestion", ["router"]),
```

### Option 3: Emergency Fix
Set environment variable in Render:
```
TESTING=true
```
This will skip heavy initialization (but also disables auth - use only temporarily!)

## Success Criteria

✅ Deployment completes without OOM error
✅ Memory usage <300MB
✅ Health endpoint responds
✅ No ML models loaded (verified in logs)
✅ No AI circuit breakers created (verified in logs)
✅ App stays running for 24+ hours

## Known Limitations (CLOUD Mode)

These features are NOT available in CLOUD mode (require EDGE worker):
- ❌ PDF ingestion (returns 503)
- ❌ Semantic search (requires embeddings)
- ❌ Annotation semantic search (requires embeddings)
- ❌ AI summarization (requires transformers)
- ❌ Auto-classification (requires ML models)

These features WORK in CLOUD mode:
- ✅ Health checks
- ✅ Authentication
- ✅ Resource CRUD (without embeddings)
- ✅ Collections
- ✅ Basic search (keyword only)
- ✅ Graph operations (without embeddings)

## Next Steps After Successful Deployment

1. ✅ Verify CLOUD mode deployment works
2. 📋 Set up edge worker (local GPU machine)
3. 📋 Configure Redis for task queue
4. 📋 Test edge worker processing
5. 📋 Implement task queuing for PDF ingestion
6. 📋 Implement task queuing for semantic search
7. 📋 Full integration testing

## Troubleshooting

### Still Getting OOM?
1. Check `MODE=CLOUD` is set in Render
2. Check logs for "Loading embedding model" (should NOT appear)
3. Check logs for "Created circuit breaker 'ai_embedding'" (should NOT appear)
4. Run `verify_cloud_mode.py` locally to reproduce

### Health Endpoint Not Responding?
1. Check logs for startup errors
2. Check database connection (DATABASE_URL)
3. Check if auth module is causing issues
4. Try disabling auth module temporarily

### 503 Errors on All Endpoints?
1. Check if app started successfully
2. Check if database migrations ran
3. Check if modules registered successfully
4. Check logs for module registration errors

## Contact

If issues persist:
1. Check logs in Render dashboard
2. Run `verify_cloud_mode.py` locally
3. Review `OOM_FIX_SUMMARY.md` for details
4. Check `SERVERLESS_DEPLOYMENT_GUIDE.md` for architecture

---

**Last Updated**: 2026-04-16
**Status**: Ready for deployment
**Expected Result**: No OOM, <300MB memory usage
