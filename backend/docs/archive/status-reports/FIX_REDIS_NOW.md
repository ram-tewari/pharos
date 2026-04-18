# Fix Redis Connection - Step by Step

## Problem

Your Pharos API is deployed and working, but **cannot create resources** because Redis is not connected.

## Solution (5 minutes)

### Step 1: Get Your Upstash Redis URL (1 minute)

1. Open https://console.upstash.com
2. Click on your Redis database
3. Look for "Redis Connect" section
4. Copy the **Redis URL** (NOT the REST URL)
   - Should look like: `rediss://default:AbCd1234...@us1-example-12345.upstash.io:6379`
   - **Must start with `rediss://`** (two S's for SSL)

### Step 2: Set Environment Variable in Render (2 minutes)

1. Open https://dashboard.render.com
2. Click on `pharos-cloud-api` (or your service name)
3. Click "Environment" in the left sidebar
4. Scroll down and click "Add Environment Variable"
5. Enter:
   - **Key**: `REDIS_URL`
   - **Value**: Paste the URL from Step 1
6. Click "Save Changes"
7. Render will show "Deploying..." - wait for it to finish (~2 minutes)

### Step 3: Verify It Works (1 minute)

Once deployment completes, test:

```powershell
# Check system status
Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/monitoring/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

Look for:
```json
{
  "redis": {"status": "healthy"},
  "celery": {"status": "healthy"}
}
```

### Step 4: Test Creating a Resource (1 minute)

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

Expected: Status 202 with resource ID

## Done!

Your API can now:
- ✅ Create resources
- ✅ Queue ingestion tasks
- ✅ Communicate with edge worker
- ✅ Cache results

## If It Still Doesn't Work

### Option 1: Use REST API Instead

If native Redis doesn't work, use REST API:

1. In Upstash dashboard, copy:
   - **REST URL**: `https://us1-example-12345.upstash.io`
   - **REST Token**: `AbCd1234...`

2. In Render, add TWO environment variables:
   - Key: `UPSTASH_REDIS_REST_URL`, Value: (REST URL)
   - Key: `UPSTASH_REDIS_REST_TOKEN`, Value: (REST Token)

3. Save and wait for redeploy

### Option 2: Check Logs

1. In Render dashboard, click "Logs"
2. Look for Redis connection messages
3. Share any errors you see

## Quick Reference

**What you need**:
- Upstash Redis URL (starts with `rediss://`)

**Where to set it**:
- Render Dashboard → pharos-cloud-api → Environment → Add Variable

**Variable name**:
- `REDIS_URL`

**How long**:
- 5 minutes total

**Cost**:
- $0 (Upstash free tier)

---

**You are here**: Need to set REDIS_URL  
**Next step**: Go to Render dashboard  
**Time**: 5 minutes
