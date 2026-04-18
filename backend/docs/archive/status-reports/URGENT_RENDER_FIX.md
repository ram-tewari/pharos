# URGENT: Render Deployment Fix - Action Items

**Status**: 🔴 CRITICAL - Deployment Failing  
**Time to Fix**: 5 minutes  
**Root Cause**: 3 configuration issues

---

## 🚨 DO THIS NOW (5 Minutes)

### Step 1: Fix Redis URL (2 minutes)

1. Open Upstash dashboard: https://console.upstash.com
2. Select your Redis database
3. **Scroll down to "Connect" section** (NOT "REST API")
4. Copy the URL starting with `rediss://`
5. Go to Render dashboard → Environment Variables
6. Update `REDIS_URL` with the `rediss://` URL

**Also add these two variables:**
- `UPSTASH_REDIS_REST_URL` = (from "REST API" section)
- `UPSTASH_REDIS_REST_TOKEN` = (from "REST API" section)

### Step 2: Deploy Fixed Code (3 minutes)

```bash
# Commit the fix
git add backend/requirements-cloud.txt
git commit -m "Fix OOM: Remove sentence-transformers from cloud requirements"
git push origin main
```

Render will auto-deploy. Watch the logs.

---

## ✅ Expected Success Logs

```
Deployment mode: CLOUD
Cloud mode: Skipping torch-dependent modules
✓ Cloud mode: ML models will NOT be loaded
Module registration complete
Pharos API ready to accept connections
```

**Memory usage**: <300MB (not >512MB)

---

## ❌ If You See These, It Failed

```
Out of memory (used over 512Mi)  ❌
Loading embedding model...  ❌
Redis URL must specify...  ❌
Port scan timeout...  ❌
```

---

## 🎯 What Was Fixed

### Issue 1: Redis URL ❌ → ✅
- **Before**: Using REST API URL (https://...)
- **After**: Using Redis connection string (rediss://...)

### Issue 2: OOM Crash ❌ → ✅
- **Before**: sentence-transformers in requirements-cloud.txt (~500MB)
- **After**: Removed from requirements-cloud.txt (~0MB)

### Issue 3: Port Binding ✅
- **Already fixed**: gunicorn binds to 0.0.0.0:$PORT

---

## 📊 Memory Usage

### Before Fix (OOM)
```
PyTorch + Transformers:  ~500MB
FastAPI + Gunicorn:      ~100MB
Total:                   ~600MB  ❌ EXCEEDS 512MB
```

### After Fix (Success)
```
FastAPI + Gunicorn:      ~150MB
Database + Redis:         ~60MB
Headroom:                ~300MB
Total:                   ~210MB  ✅ WELL UNDER 512MB
```

---

## 🧪 Test After Deployment

```bash
# Should return healthy
curl https://your-app.onrender.com/health

# Should return 503 (requires edge worker)
curl -X POST https://your-app.onrender.com/api/resources/pdf/ingest
```

---

## 📚 Detailed Documentation

- `RENDER_DEPLOYMENT_FIX.md` - Full technical details
- `OOM_FIX_SUMMARY.md` - Code changes summary
- `verify_cloud_mode.py` - Local verification script

---

## 🆘 If Still Failing

1. Check `MODE=CLOUD` in Render environment variables
2. Check `WEB_CONCURRENCY=1` in Render environment variables
3. Check `REDIS_URL` starts with `rediss://`
4. Check logs for "Loading embedding model" (should NOT appear)
5. Run `python verify_cloud_mode.py` locally

---

**Last Updated**: 2026-04-16  
**Expected Fix Time**: 5 minutes  
**Expected Result**: Deployment succeeds, <300MB memory
