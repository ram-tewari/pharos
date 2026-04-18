# Render Deployment Fix - Three Critical Issues

**Date**: 2026-04-16  
**Status**: URGENT - Deployment Failing  
**Root Cause**: Configuration leaks causing OOM crash

---

## Issue Summary

Your Render deployment is failing with three distinct issues:

1. ✅ **Redis URL Trap** - Using REST API URL instead of Redis connection string
2. ✅ **Port Binding Timeout** - Already fixed (gunicorn binds to 0.0.0.0:$PORT)
3. ✅ **512MB OOM Crash** - sentence-transformers in requirements-cloud.txt

---

## Issue 1: Redis URL Trap (CRITICAL)

### The Problem
```
Connecting to Upstash Redis (REST API): https://living-sculpin-96916.u...
Redis URL must specify one of the following schemes (redis://, rediss://, unix://)
```

You copied the **REST API URL** instead of the **Redis connection string**.

### The Fix

1. Go to Upstash dashboard: https://console.upstash.com
2. Select your Redis database
3. **Scroll past the REST API section**
4. Find the **Connect** section
5. Copy the URL that starts with `rediss://` (with SSL)
6. Update in Render dashboard:
   - Go to Environment Variables
   - Find `REDIS_URL`
   - Replace with the `rediss://` URL

### Correct Format
```bash
# ❌ WRONG (REST API URL)
REDIS_URL=https://living-sculpin-96916.upstash.io

# ✅ CORRECT (Redis connection string)
REDIS_URL=rediss://default:password@living-sculpin-96916.upstash.io:6379
```

### Additional Required Variables
You also need the REST API credentials for the task queue:
```bash
UPSTASH_REDIS_REST_URL=https://living-sculpin-96916.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here
```

Both are available in the Upstash dashboard under "REST API" section.

---

## Issue 2: Port Binding Timeout (ALREADY FIXED ✅)

### The Problem
```
Port scan timeout reached, no open ports detected.
```

Render expects the server to bind to `0.0.0.0:$PORT` (all interfaces).

### The Fix
✅ **Already fixed** in `gunicorn_conf.py`:
```python
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
```

This is correct. No action needed.

---

## Issue 3: 512MB OOM Crash (CRITICAL - FIXED)

### The Problem
```
==> Out of memory (used over 512Mi)
```

Your app took 12 minutes to boot before OOM crash. Two culprits:

#### Culprit A: Rogue ML Imports ❌
**FOUND IT!** `requirements-cloud.txt` line 36:
```python
sentence-transformers>=2.2.0  # ❌ This pulls in PyTorch (~500MB)
```

This is the smoking gun. Installing sentence-transformers pulls in:
- PyTorch: ~400MB
- Transformers: ~100MB
- Total: ~500MB just for ML libraries

On a 512MB instance, this leaves only ~12MB for the actual app. OOM guaranteed.

#### Culprit B: Too Many Workers ✅
✅ **Already fixed** in `render.yaml`:
```yaml
- key: WEB_CONCURRENCY
  value: 1  # ✅ Correct for Starter plan
```

### The Fix

✅ **FIXED** - Removed sentence-transformers from `requirements-cloud.txt`:
```python
# ❌ REMOVED (causes OOM)
# sentence-transformers>=2.2.0

# Cloud mode architecture:
# - Render API: Queues embedding tasks to Upstash Redis
# - Edge Worker: Processes tasks with local GPU (RTX 4070)
# - No ML models loaded on Render instance
```

---

## Deployment Checklist

### Pre-Deployment (Do This Now)

1. **Fix Redis URL in Render Dashboard**
   - [ ] Go to Render dashboard → Environment Variables
   - [ ] Update `REDIS_URL` to use `rediss://` URL (not REST API URL)
   - [ ] Add `UPSTASH_REDIS_REST_URL` (REST API URL)
   - [ ] Add `UPSTASH_REDIS_REST_TOKEN` (REST API token)

2. **Verify Environment Variables**
   - [ ] `MODE=CLOUD` ✅ (already set)
   - [ ] `WEB_CONCURRENCY=1` ✅ (already set)
   - [ ] `DATABASE_URL=postgresql://...` (your NeonDB URL)
   - [ ] `REDIS_URL=rediss://...` (fix this!)
   - [ ] `UPSTASH_REDIS_REST_URL=https://...` (add this!)
   - [ ] `UPSTASH_REDIS_REST_TOKEN=...` (add this!)

3. **Commit and Push Changes**
   ```bash
   git add backend/requirements-cloud.txt
   git commit -m "Fix OOM: Remove sentence-transformers from cloud requirements"
   git push origin main
   ```

### During Deployment (Watch Logs)

Expected logs (SUCCESS):
```
Deployment mode: CLOUD
Cloud mode: Skipping torch-dependent modules
✓ Cloud mode: ML models will NOT be loaded (queued to edge worker via Redis)
Cloud mode: Skipping AI circuit breakers (handled by edge worker)
Module registration complete: X modules registered
Pharos API ready to accept connections
```

Should NOT see (FAILURE):
```
Out of memory (used over 512Mi)  ❌
Loading embedding model...  ❌
Created circuit breaker 'ai_embedding'  ❌
Importing torch...  ❌
```

### Post-Deployment (Verify)

1. **Test Health Endpoint**
   ```bash
   curl https://your-app.onrender.com/health
   ```
   Expected: `{"status": "healthy", "service": "pharos-api"}`

2. **Check Memory Usage**
   - Go to Render dashboard → Metrics
   - Memory should be <300MB (not >512MB)
   - Should stay stable (no gradual increase)

3. **Test API Endpoints**
   ```bash
   # Should work (no ML required)
   curl https://your-app.onrender.com/api/monitoring/health
   
   # Should return 503 (requires edge worker)
   curl -X POST https://your-app.onrender.com/api/resources/pdf/ingest
   ```

---

## Expected Memory Usage

### Before Fix (OOM Crash)
```
PyTorch:              ~400MB
Transformers:         ~100MB
FastAPI + Gunicorn:   ~100MB
Database connections:  ~50MB
-----------------------------------
Total:                ~650MB  ❌ EXCEEDS 512MB LIMIT
```

### After Fix (Success)
```
FastAPI + Gunicorn:   ~150MB
Database connections:  ~50MB
Redis client:          ~10MB
Python runtime:        ~50MB
Headroom:             ~250MB
-----------------------------------
Total:                ~260MB  ✅ WELL UNDER 512MB LIMIT
```

---

## Architecture Reminder

```
┌─────────────────────────────────────────────────────────────┐
│ CLOUD MODE (Render - 512MB RAM)                            │
│ - FastAPI API server                                        │
│ - NO ML models loaded                                       │
│ - Queues embedding tasks to Upstash Redis                  │
│ - Memory: <300MB                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓ (task queue)
                    Upstash Redis
                          ↓ (task processing)
┌─────────────────────────────────────────────────────────────┐
│ EDGE MODE (Local GPU - RTX 4070)                           │
│ - Processes embedding tasks from queue                      │
│ - Loads ML models (PyTorch, sentence-transformers)         │
│ - GPU-accelerated inference                                 │
│ - Memory: Unlimited (your hardware)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Still Getting OOM?
1. Check `requirements-cloud.txt` has NO sentence-transformers
2. Check `MODE=CLOUD` in Render environment variables
3. Check `WEB_CONCURRENCY=1` in Render environment variables
4. Check logs for "Loading embedding model" (should NOT appear)
5. Run `verify_cloud_mode.py` locally to reproduce

### Redis Connection Errors?
1. Verify `REDIS_URL` starts with `rediss://` (with SSL)
2. Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are set
3. Check Upstash dashboard for connection errors
4. Test connection: `redis-cli -u $REDIS_URL ping`

### Port Binding Timeout?
1. Check `gunicorn_conf.py` binds to `0.0.0.0:$PORT` ✅ (already correct)
2. Check startup time in logs (should be <30 seconds)
3. Check health endpoint responds: `/health`

### Slow Startup?
1. Check database migrations run quickly (<10 seconds)
2. Check no ML models are being loaded
3. Check Redis connection succeeds quickly
4. Review startup logs for bottlenecks

---

## Success Criteria

✅ Deployment completes without OOM error  
✅ Memory usage <300MB (not >512MB)  
✅ Health endpoint responds in <1 second  
✅ No ML models loaded (verified in logs)  
✅ Redis connection succeeds (rediss:// URL)  
✅ App stays running for 24+ hours  

---

## Next Steps After Successful Deployment

1. ✅ Verify Render deployment works
2. 📋 Set up edge worker on local GPU machine
3. 📋 Configure edge worker to connect to Upstash Redis
4. 📋 Test task queue (Render → Redis → Edge Worker)
5. 📋 Test embedding generation via edge worker
6. 📋 Monitor memory usage over 24 hours

---

## Files Changed

- ✅ `backend/requirements-cloud.txt` - Removed sentence-transformers
- ✅ `backend/app/__init__.py` - Added CLOUD mode logging
- ✅ `backend/app/shared/circuit_breaker.py` - Conditional AI breakers
- ✅ `backend/app/modules/pdf_ingestion/service.py` - Lazy imports
- ✅ `backend/app/modules/pdf_ingestion/router.py` - Conditional instantiation
- ✅ `backend/app/modules/annotations/service.py` - Lazy property

---

## Contact

If issues persist after these fixes:
1. Check Render logs for specific error messages
2. Run `verify_cloud_mode.py` locally
3. Review `OOM_FIX_SUMMARY.md` for technical details
4. Check `SERVERLESS_DEPLOYMENT_GUIDE.md` for architecture

---

**Last Updated**: 2026-04-16  
**Status**: Ready for deployment  
**Expected Result**: No OOM, <300MB memory usage, Redis connected
