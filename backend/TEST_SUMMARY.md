# Pharos API Test Summary - 2026-04-16

## ✅ What's Working

1. **API Server** - Responding correctly at https://pharos-cloud-api.onrender.com
2. **Health Endpoint** - `/health` returns healthy status
3. **Database** - NeonDB PostgreSQL connected successfully
4. **API Documentation** - Swagger UI accessible at `/docs`
5. **Read Operations** - Can list resources via GET `/api/resources`
6. **CSRF Protection** - Working correctly (requires Origin header)
7. **Lazy Redis Connection** - Startup is fast (<2s), doesn't block on Redis

## ❌ What's NOT Working

1. **Redis Connection** - Trying to connect to `localhost:6379` instead of Upstash
2. **Resource Creation** - POST `/api/resources` fails with "Failed to queue ingestion"
3. **Edge Worker Communication** - Cannot receive tasks from Redis queue
4. **Caching** - Disabled due to Redis unavailability

## 🔍 Root Cause

**REDIS_URL environment variable is NOT set in Render dashboard**

Evidence from monitoring endpoint:
```json
{
  "redis": {
    "status": "unhealthy",
    "message": "Connection failed"
  },
  "celery": {
    "status": "unhealthy",
    "message": "Cannot connect to workers: Error 111 connecting to localhost:6379. Connection refused."
  }
}
```

The application is falling back to `localhost:6379` because `REDIS_URL` is not configured.

## 🔧 Solution (5 minutes)

### Step 1: Get Upstash Redis URL

1. Go to Upstash Dashboard: https://console.upstash.com
2. Select your Redis database
3. Copy the connection string (starts with `rediss://`)
   - Format: `rediss://default:PASSWORD@HOST.upstash.io:6379`
   - **Important**: Must use `rediss://` (two S's) for SSL/TLS

### Step 2: Set Environment Variable in Render

1. Go to Render Dashboard: https://dashboard.render.com
2. Select `pharos-cloud-api` service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Set:
   - **Key**: `REDIS_URL`
   - **Value**: `rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379`
6. Click "Save Changes"
7. Render will automatically redeploy (~2 minutes)

### Step 3: Verify Fix

Wait for redeploy to complete, then test:

```powershell
# Test monitoring endpoint
Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/monitoring/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

Expected result:
```json
{
  "status": "healthy",
  "components": {
    "redis": {"status": "healthy"},
    "celery": {"status": "healthy"}
  }
}
```

### Step 4: Test Resource Creation

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "https://pharos-cloud-api.onrender.com"
}

$body = @{
    url = "https://github.com/test/test"
    title = "Test Resource"
    resource_type = "code"
    tags = @("test")
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/resources" -Method POST -Body $body -Headers $headers -UseBasicParsing
```

Expected: 202 Accepted with resource ID

## 📊 Test Results

| Test | Status | Details |
|------|--------|---------|
| Health Check | ✅ PASS | API responding |
| API Docs | ✅ PASS | Swagger UI accessible |
| Database | ✅ PASS | PostgreSQL connected |
| Redis | ❌ FAIL | Not configured |
| Celery | ❌ FAIL | Depends on Redis |
| List Resources | ✅ PASS | Read operations work |
| Create Resource | ❌ FAIL | Requires Redis queue |
| Search | ⏳ SKIP | Requires resources |

## 🎯 Expected Behavior After Fix

### Before (Current State)
```
API: ✅ Healthy
Database: ✅ Connected
Redis: ❌ localhost:6379 connection refused
Celery: ❌ Cannot connect to workers
Resource Creation: ❌ Failed to queue ingestion
```

### After (With REDIS_URL)
```
API: ✅ Healthy
Database: ✅ Connected
Redis: ✅ Connected to Upstash
Celery: ✅ Workers available
Resource Creation: ✅ Queued successfully
Edge Worker: ✅ Receiving tasks
```

## 🔄 Edge Worker Connection

After fixing Redis, verify your edge worker can connect:

1. Check `.env.edge` file has:
   ```
   UPSTASH_REDIS_REST_URL=https://YOUR_HOST.upstash.io
   UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN
   ```

2. Restart edge worker:
   ```powershell
   .\start_edge_worker.ps1
   ```

3. Look for log message:
   ```
   ✓ Redis connection successful
   Listening for tasks on queue: pharos_ingestion
   ```

## 📝 Checklist

- [x] API deployed to Render
- [x] Database connected (NeonDB)
- [x] Health check working
- [x] API docs accessible
- [x] Read operations working
- [ ] **REDIS_URL set in Render** ← YOU ARE HERE
- [ ] Redis connected
- [ ] Resource creation working
- [ ] Edge worker receiving tasks
- [ ] Full ingestion pipeline working

## 💰 Cost

**Current**: $7/mo (Render Starter)  
**After Fix**: $7/mo (no change)  
**Upstash**: $0/mo (free tier)

## ⏱️ Timeline

1. Get Upstash URL: 1 minute
2. Set in Render: 1 minute
3. Wait for redeploy: 2 minutes
4. Test: 1 minute
**Total**: 5 minutes

## 📚 Related Documents

- `RENDER_REDIS_ISSUE.md` - Detailed diagnosis
- `REDIS_FIX_APPLIED.md` - Lazy connection fix
- `ENDPOINT_TEST_RESULTS.md` - Full test results
- `render.yaml` - Deployment configuration

## 🆘 If Issues Persist

1. Check Render logs for errors
2. Verify Upstash URL format (must start with `rediss://`)
3. Check Upstash dashboard for connection attempts
4. Verify edge worker logs
5. Try REST API fallback (set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`)

## ✨ Success Criteria

- [ ] Monitoring shows all components healthy
- [ ] Can create resources successfully
- [ ] Edge worker receives tasks
- [ ] Resources transition from "pending" to "completed"
- [ ] Search returns results

---

**Current Status**: Waiting for REDIS_URL configuration  
**Next Action**: Set REDIS_URL in Render dashboard  
**ETA**: 5 minutes
