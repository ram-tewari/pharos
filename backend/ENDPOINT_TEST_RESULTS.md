# Pharos API Endpoint Test Results

**Date**: 2026-04-16  
**Environment**: Render Production (pharos-cloud-api.onrender.com)  
**Tester**: Automated Testing

## Test Results Summary

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/health` | ✅ PASS | API is healthy |
| `/docs` | ✅ PASS | API documentation accessible |
| `/api/monitoring/health` | ⚠️ DEGRADED | Redis and Celery unavailable |
| `/api/resources` (GET) | ✅ PASS | Can list resources |
| `/api/resources` (POST) | ❌ FAIL | Cannot create resources (Redis required) |
| `/api/search/hybrid` (POST) | ⏳ UNTESTED | Requires resources to exist |

## Detailed Results

### 1. Health Check ✅

**Endpoint**: `GET /health`  
**Status**: 200 OK  
**Response**:
```json
{
  "status": "healthy",
  "service": "pharos-api"
}
```

**Result**: PASS - API is responding correctly.

---

### 2. API Documentation ✅

**Endpoint**: `GET /docs`  
**Status**: 200 OK  
**Result**: PASS - Swagger UI is accessible.

---

### 3. Monitoring Health ⚠️

**Endpoint**: `GET /api/monitoring/health`  
**Status**: 200 OK  
**Response**:
```json
{
  "status": "degraded",
  "message": "System operational with degraded functionality: Redis unavailable; Celery workers unavailable",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Connected"
    },
    "redis": {
      "status": "unhealthy",
      "message": "Connection failed"
    },
    "celery": {
      "status": "unhealthy",
      "message": "Cannot connect to workers: Error 111 connecting to localhost:6379. Connection refused.",
      "worker_count": 0
    },
    "api": {
      "status": "healthy",
      "message": "API responding"
    }
  }
}
```

**Result**: DEGRADED - API and database work, but Redis and Celery are unavailable.

**Issues Found**:
1. Redis is trying to connect to `localhost:6379` instead of Upstash
2. Celery cannot connect to workers (depends on Redis)

**Root Cause**: `REDIS_URL` environment variable is NOT set in Render dashboard.

---

### 4. List Resources ✅

**Endpoint**: `GET /api/resources?limit=5`  
**Status**: 200 OK  
**Result**: PASS - Can retrieve resources (even without Redis).

---

### 5. Create Resource ❌

**Endpoint**: `POST /api/resources`  
**Status**: 500 Internal Server Error  
**Response**:
```json
{
  "detail": "Failed to queue ingestion"
}
```

**Result**: FAIL - Cannot create resources because Redis queue is unavailable.

**CSRF Protection**: ✅ Working correctly (requires Origin header)

---

## Critical Issues

### Issue #1: Redis Not Connected (CRITICAL)

**Problem**: Application is trying to connect to `localhost:6379` instead of Upstash Redis.

**Evidence**:
```
"Cannot connect to workers: Error 111 connecting to localhost:6379. Connection refused."
```

**Impact**:
- ❌ Cannot create resources
- ❌ Cannot queue ingestion tasks
- ❌ Edge worker cannot receive tasks
- ❌ No caching

**Solution**:
1. Go to Render Dashboard → pharos-cloud-api → Environment
2. Add environment variable:
   - Key: `REDIS_URL`
   - Value: `rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379`
3. Save changes (Render will auto-redeploy)

**Alternative Solution** (if native Redis doesn't work):
1. Set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
2. Application will use REST API instead of native protocol

---

### Issue #2: Edge Worker Cannot Connect

**Problem**: Edge worker is running locally but cannot receive tasks from Redis queue.

**Impact**:
- ❌ Ingestion tasks cannot be processed
- ❌ Embeddings cannot be generated
- ❌ Resources stuck in "pending" status

**Solution**:
1. Fix Redis connection (Issue #1)
2. Verify edge worker has correct Upstash credentials in `.env.edge`:
   ```
   UPSTASH_REDIS_REST_URL=https://YOUR_HOST.upstash.io
   UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN
   ```
3. Restart edge worker

---

## What's Working ✅

1. **API Server**: Responding correctly
2. **Database**: Connected (NeonDB PostgreSQL)
3. **Health Checks**: Working
4. **API Documentation**: Accessible
5. **Read Operations**: Can list resources
6. **CSRF Protection**: Working correctly
7. **Startup**: Fast (<2s with lazy Redis connection)

## What's Not Working ❌

1. **Redis Connection**: Trying to connect to localhost instead of Upstash
2. **Resource Creation**: Cannot queue ingestion tasks
3. **Edge Worker Communication**: Cannot receive tasks from queue
4. **Caching**: Disabled due to Redis unavailability

## Testing Script

A PowerShell test script has been created: `backend/test_render_api.ps1`

**Usage**:
```powershell
cd backend
.\test_render_api.ps1
```

This script tests all endpoints and provides a detailed report.

## Next Steps

### Immediate (5 minutes)

1. ✅ Identify Redis issue (DONE)
2. ⏳ Set `REDIS_URL` in Render dashboard
3. ⏳ Wait for auto-redeploy (~2 minutes)
4. ⏳ Run test script to verify

### After Redis Fix (10 minutes)

1. ⏳ Verify monitoring endpoint shows Redis healthy
2. ⏳ Test resource creation
3. ⏳ Verify edge worker receives tasks
4. ⏳ Test full ingestion pipeline

### Optional Improvements

1. Add Redis connection retry logic (already implemented)
2. Add better error messages for Redis failures
3. Add monitoring alerts for Redis downtime
4. Consider upgrading Upstash to paid tier for better reliability

## Environment Variables Checklist

Required in Render Dashboard:

- [x] `DATABASE_URL` - NeonDB connection string (WORKING)
- [ ] `REDIS_URL` - Upstash rediss:// URL (MISSING - CRITICAL)
- [ ] `UPSTASH_REDIS_REST_URL` - Upstash REST API URL (OPTIONAL)
- [ ] `UPSTASH_REDIS_REST_TOKEN` - Upstash REST API token (OPTIONAL)
- [x] `MODE` - Set to "CLOUD" (WORKING)
- [x] `WEB_CONCURRENCY` - Set to 1 for Starter plan (WORKING)
- [ ] `PHAROS_API_KEY` - M2M authentication (OPTIONAL)
- [ ] `GITHUB_TOKEN` - GitHub API access (OPTIONAL)

## Cost Impact

**Current**: $7/mo (Render Starter)  
**After Fix**: $7/mo (no change)  
**Upstash**: $0/mo (free tier)

## Risk Assessment

**Risk Level**: LOW  
**Reason**: Only Redis connection needs to be configured. No code changes required.

**Rollback Plan**: Remove `REDIS_URL` if issues occur (application will continue without caching).

## Success Criteria

After fixing Redis connection:

1. ✅ Monitoring endpoint shows all components healthy
2. ✅ Can create resources successfully
3. ✅ Edge worker receives and processes tasks
4. ✅ Resources transition from "pending" to "completed"
5. ✅ Caching is enabled and working

## Related Documents

- `backend/RENDER_REDIS_ISSUE.md` - Detailed Redis diagnosis
- `backend/REDIS_FIX_APPLIED.md` - Redis lazy connection fix
- `backend/test_render_api.ps1` - Automated test script
- `backend/render.yaml` - Deployment configuration

## Contact

If issues persist after setting `REDIS_URL`:

1. Check Render logs for errors
2. Check Upstash dashboard for connection attempts
3. Verify edge worker logs
4. Run test script for detailed diagnostics

---

**Status**: Waiting for `REDIS_URL` to be set in Render dashboard.  
**ETA**: 5 minutes to configure + 2 minutes to redeploy = 7 minutes total.
