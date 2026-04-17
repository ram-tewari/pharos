# Deployment In Progress - Redis Fix

## What Was Fixed

### Issue
Celery broker URL was hardcoded to `localhost:6379` instead of using the `REDIS_URL` environment variable.

### Solution Applied

**File**: `backend/app/config/settings.py`

Changed Celery configuration from static to dynamic:

**Before**:
```python
CELERY_BROKER_URL: str = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
```

**After**:
```python
@property
def CELERY_BROKER_URL(self) -> str:
    if self.REDIS_URL:
        base_url = self.REDIS_URL.rsplit('/', 1)[0]
        return f"{base_url}/0"
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

@property
def CELERY_RESULT_BACKEND(self) -> str:
    if self.REDIS_URL:
        base_url = self.REDIS_URL.rsplit('/', 1)[0]
        return f"{base_url}/1"
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
```

This makes Celery use:
- **Production (Render)**: `rediss://...upstash.io:6379/0` (from REDIS_URL env var)
- **Development**: `redis://localhost:6379/0` (fallback)

## Changes Pushed

**Commit**: `fix: use REDIS_URL for Celery broker and lazy Redis connection`

**Files Modified**:
1. `backend/app/config/settings.py` - Dynamic Celery broker URL
2. `backend/app/__init__.py` - Lazy Redis connection (no startup ping)
3. `backend/app/shared/cache.py` - 30s timeout for cold starts

**Git Push**: ✅ Completed at $(Get-Date)

## Render Deployment

**Status**: In Progress  
**Expected Time**: 2-3 minutes  
**Auto-Deploy**: Yes (triggered by git push)

## How to Monitor

### Option 1: Watch Render Dashboard
1. Go to https://dashboard.render.com
2. Click on `pharos-cloud-api`
3. Watch "Events" tab for deployment progress

### Option 2: Use Monitoring Script
```powershell
cd backend
.\wait_for_deploy.ps1
```

This will check every 10 seconds until Redis is healthy.

### Option 3: Manual Check
```powershell
Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/monitoring/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

Look for:
```json
{
  "redis": {"status": "healthy"},
  "celery": {"status": "healthy"}
}
```

## Expected Timeline

| Time | Event |
|------|-------|
| T+0 | Git push completed |
| T+30s | Render detects changes |
| T+1m | Build starts |
| T+2m | Deploy starts |
| T+3m | Health checks pass |
| T+3m | Redis connected ✓ |

## What Happens Next

Once deployment completes:

1. **Redis Connection**: Will use Upstash URL from environment
2. **Celery Workers**: Will connect to Upstash queue
3. **Edge Worker**: Can receive tasks from queue
4. **Resource Creation**: Will work end-to-end

## Testing After Deployment

### Test 1: Check System Health
```powershell
Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/monitoring/health" -UseBasicParsing
```

Expected: All components healthy

### Test 2: Create a Resource
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "https://pharos-cloud-api.onrender.com"
}

$body = @{
    url = "https://github.com/test/test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    title = "Test Resource"
    resource_type = "code"
    tags = @("test")
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/resources" -Method POST -Body $body -Headers $headers -UseBasicParsing
```

Expected: 202 Accepted with resource ID

### Test 3: Verify Edge Worker Receives Task

Check your edge worker logs for:
```
Received task: ingest_resource
Processing resource: <resource_id>
```

## Troubleshooting

### If Redis Still Shows Unhealthy

1. Check Render logs for Redis connection errors
2. Verify REDIS_URL format in Render dashboard (must start with `rediss://`)
3. Try REST API fallback (UPSTASH_REDIS_REST_URL + TOKEN)
4. Check Upstash dashboard for connection attempts

### If Celery Still Shows Unhealthy

1. Verify the code changes deployed (check Render logs)
2. Check if settings.py is using the new property-based approach
3. Verify REDIS_URL is accessible from settings object

### If Edge Worker Can't Connect

1. Verify `.env.edge` has correct Upstash credentials
2. Restart edge worker: `.\start_edge_worker.ps1`
3. Check edge worker logs for connection errors

## Rollback Plan

If issues persist:

```powershell
git revert HEAD
git push origin master
```

This will revert to the previous version.

## Success Criteria

- [ ] Render deployment completes successfully
- [ ] Redis shows "healthy" in monitoring endpoint
- [ ] Celery shows "healthy" in monitoring endpoint
- [ ] Can create resources via API
- [ ] Edge worker receives and processes tasks
- [ ] Resources transition from "pending" to "completed"

## Current Status

**Deployment**: In Progress  
**ETA**: 2-3 minutes from push  
**Next Check**: Run `.\wait_for_deploy.ps1` or check manually

---

**Last Updated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Pushed By**: Automated fix for Redis connection  
**Monitoring**: Use wait_for_deploy.ps1 script
