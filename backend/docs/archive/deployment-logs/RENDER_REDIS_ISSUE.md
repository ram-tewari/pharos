# Render Redis Connection Issue - FOUND

## Problem

From monitoring endpoint:
```json
{
  "redis": {
    "status": "unhealthy",
    "message": "Connection failed"
  },
  "celery": {
    "status": "unhealthy",
    "message": "Cannot connect to workers: Error 111 connecting to localhost:6379. Connection refused.",
    "worker_count": 0
  }
}
```

## Root Cause

The application is trying to connect to `localhost:6379` instead of using the Upstash Redis URL from environment variables.

This means:
1. `REDIS_URL` environment variable is NOT set in Render dashboard
2. OR the application is not reading it correctly
3. OR there's a fallback to localhost that's being used

## Verification Steps

### Step 1: Check Render Environment Variables

1. Go to Render Dashboard → pharos-cloud-api → Environment
2. Check if these variables exist:
   - `REDIS_URL` - Should be set to Upstash rediss:// URL
   - `UPSTASH_REDIS_REST_URL` - Should be set
   - `UPSTASH_REDIS_REST_TOKEN` - Should be set

### Step 2: Check Upstash Dashboard

1. Go to Upstash Dashboard
2. Copy the Redis URL (starts with `rediss://`)
3. Verify it's the correct format

## Solution

### Option 1: Set REDIS_URL in Render (Recommended)

1. Go to Render Dashboard → pharos-cloud-api → Environment
2. Add environment variable:
   - Key: `REDIS_URL`
   - Value: `rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379`
3. Click "Save Changes"
4. Render will automatically redeploy

### Option 2: Set Upstash REST API Credentials

If native Redis doesn't work, use REST API:

1. Go to Render Dashboard → pharos-cloud-api → Environment
2. Add environment variables:
   - Key: `UPSTASH_REDIS_REST_URL`
   - Value: `https://YOUR_HOST.upstash.io`
   - Key: `UPSTASH_REDIS_REST_TOKEN`
   - Value: `YOUR_TOKEN`
3. Click "Save Changes"
4. Render will automatically redeploy

## Expected Behavior After Fix

### Monitoring Endpoint
```json
{
  "status": "healthy",
  "components": {
    "redis": {
      "status": "healthy",
      "message": "Connected"
    },
    "celery": {
      "status": "healthy",
      "message": "Workers available",
      "worker_count": 1
    }
  }
}
```

### Resource Creation
```bash
POST /api/resources
# Should return 202 Accepted with resource ID
```

## Testing After Fix

1. Check monitoring endpoint:
```bash
curl https://pharos-cloud-api.onrender.com/api/monitoring/health
```

2. Create a test resource:
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/resources \
  -H "Content-Type: application/json" \
  -H "Origin: https://pharos-cloud-api.onrender.com" \
  -d '{
    "url": "https://github.com/test/test",
    "title": "Test Resource",
    "resource_type": "code",
    "tags": ["test"]
  }'
```

## Current Status

- **API**: ✅ Healthy (responding)
- **Database**: ✅ Healthy (connected)
- **Redis**: ❌ Unhealthy (localhost:6379 connection refused)
- **Celery**: ❌ Unhealthy (cannot connect to workers)
- **Edge Worker**: ⏳ Running locally but cannot connect to queue

## Impact

Without Redis:
- ❌ Cannot queue ingestion tasks
- ❌ Cannot create resources
- ❌ Edge worker cannot receive tasks
- ❌ No caching
- ✅ Read operations work (list resources, get resource)
- ✅ Health check works

## Priority

**CRITICAL** - Application cannot ingest resources without Redis connection.

## Next Steps

1. ✅ Identify issue (localhost:6379 instead of Upstash)
2. ⏳ Set REDIS_URL in Render dashboard
3. ⏳ Verify connection after redeploy
4. ⏳ Test resource creation
5. ⏳ Verify edge worker receives tasks

## ETA

5 minutes to set environment variable and redeploy.
