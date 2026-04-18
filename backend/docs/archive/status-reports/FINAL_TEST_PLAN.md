# Final Test Plan - After Deployment

## Current Status

**Latest Fix**: Using `__init__` override instead of `@property` for Pydantic compatibility  
**Commit**: `8a576fe3` - "fix: use __init__ override for Celery broker URL (Pydantic compatible)"  
**Pushed**: Yes  
**Render**: Deploying (wait 2-3 minutes)

## Test Sequence

### Test 1: System Health Check

```powershell
$response = Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/monitoring/health" -UseBasicParsing
$health = $response.Content | ConvertFrom-Json

Write-Host "Redis: $($health.components.redis.status)"
Write-Host "Celery: $($health.components.celery.status)"
```

**Expected**:
- Redis: `healthy`
- Celery: `healthy`

**If Still Unhealthy**:
- Wait another 2 minutes (deployment may still be in progress)
- Check Render dashboard for deployment status
- Check Render logs for errors

### Test 2: Create Resource

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "https://pharos-cloud-api.onrender.com"
}

$body = @{
    url = "https://github.com/test/pharos-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    title = "Test Resource - Deployment Verification"
    resource_type = "code"
    tags = @("test", "deployment")
    description = "Testing resource creation after Redis fix"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/resources" -Method POST -Body $body -Headers $headers -UseBasicParsing
    $resource = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Resource Created!" -ForegroundColor Green
    Write-Host "  ID: $($resource.id)"
    Write-Host "  Status: $($resource.ingestion_status)"
    Write-Host "  Title: $($resource.title)"
    
    # Save ID for later tests
    $global:testResourceId = $resource.id
    
} catch {
    Write-Host "✗ Failed to create resource" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "Error: $errorBody" -ForegroundColor Red
    }
}
```

**Expected**:
- Status: 202 Accepted
- Resource ID returned
- ingestion_status: "pending"

**If Fails**:
- Check error message
- Verify Redis is healthy (Test 1)
- Check CSRF headers are included

### Test 3: Verify Edge Worker Receives Task

**Check your edge worker console output for**:

```
✓ Connected to Redis queue
✓ Received task: ingest_resource
  Resource ID: <ID from Test 2>
  URL: https://github.com/test/pharos-test-...
Processing...
```

**Expected**:
- Task appears in edge worker within 5 seconds
- Edge worker starts processing

**If No Task Received**:
- Check edge worker is running
- Verify `.env.edge` has correct Upstash credentials
- Restart edge worker: `.\start_edge_worker.ps1`
- Check edge worker logs for connection errors

### Test 4: Check Resource Status

Wait 10-30 seconds for processing, then:

```powershell
$resourceId = $global:testResourceId  # From Test 2

$response = Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/resources/$resourceId" -UseBasicParsing
$resource = $response.Content | ConvertFrom-Json

Write-Host "Resource Status: $($resource.ingestion_status)" -ForegroundColor $(if ($resource.ingestion_status -eq "completed") {"Green"} else {"Yellow"})
Write-Host "Chunks: $($resource.chunk_count)"
Write-Host "Quality Score: $($resource.quality_score)"
```

**Expected**:
- ingestion_status: "completed" (or "processing" if still running)
- chunk_count: > 0
- quality_score: 0.0 - 1.0

**If Still "pending"**:
- Edge worker may not be processing
- Check edge worker logs
- Wait longer (large repos take time)

### Test 5: List Resources

```powershell
$response = Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/resources?limit=10" -UseBasicParsing
$data = $response.Content | ConvertFrom-Json

Write-Host "Total Resources: $($data.total)"
Write-Host "Returned: $($data.resources.Count)"

# Show recent resources
$data.resources | ForEach-Object {
    Write-Host "  - $($_.title) [$($_.ingestion_status)]"
}
```

**Expected**:
- List of resources including the test resource
- Various statuses (pending, processing, completed)

### Test 6: Search (if resources exist)

```powershell
$searchBody = @{
    query = "test"
    limit = 5
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "https://pharos-cloud-api.onrender.com"
}

$response = Invoke-WebRequest -Uri "https://pharos-cloud-api.onrender.com/api/search/hybrid" -Method POST -Body $searchBody -Headers $headers -UseBasicParsing
$results = $response.Content | ConvertFrom-Json

Write-Host "Search Results: $($results.results.Count)"
$results.results | ForEach-Object {
    Write-Host "  - $($_.title) (score: $($_.score))"
}
```

**Expected**:
- Search results returned
- Relevance scores
- Test resource may appear if indexed

## Success Criteria

- [ ] Redis shows "healthy"
- [ ] Celery shows "healthy"
- [ ] Can create resources (202 Accepted)
- [ ] Edge worker receives tasks
- [ ] Resources process successfully
- [ ] Can list resources
- [ ] Can search resources

## Troubleshooting Guide

### Issue: Redis Still Unhealthy After 10 Minutes

**Possible Causes**:
1. Pydantic Settings not loading REDIS_URL correctly
2. Upstash connection issue
3. SSL/TLS certificate problem

**Solutions**:
1. Check Render logs for Redis connection errors
2. Verify REDIS_URL format in Render dashboard
3. Try REST API fallback (UPSTASH_REDIS_REST_URL + TOKEN)
4. Check Upstash dashboard for connection attempts

### Issue: Celery Still Unhealthy

**Possible Causes**:
1. CELERY_BROKER_URL not being set correctly
2. __init__ override not working
3. Settings object not being initialized properly

**Solutions**:
1. Check Render logs for Celery connection errors
2. Add debug logging to settings.__init__
3. Verify settings.REDIS_URL is accessible

### Issue: Edge Worker Not Receiving Tasks

**Possible Causes**:
1. Edge worker not connected to correct queue
2. Upstash credentials incorrect in `.env.edge`
3. Queue name mismatch

**Solutions**:
1. Check edge worker logs for connection success
2. Verify UPSTASH_REDIS_REST_URL and TOKEN in `.env.edge`
3. Restart edge worker
4. Check queue name matches (default: `pharos_ingestion`)

### Issue: Resource Creation Fails

**Possible Causes**:
1. CSRF validation failing
2. Redis queue not available
3. Invalid request body

**Solutions**:
1. Ensure Origin header is included
2. Verify Redis is healthy
3. Check request body format
4. Look at Render logs for specific error

## Alternative Approach (If Still Failing)

If the `__init__` override doesn't work, we can try:

### Option 1: Environment Variable Override

Set these in Render dashboard:
- `CELERY_BROKER_URL` = `rediss://default:PASSWORD@living-sculpin-96916.upstash.io:6379/0`
- `CELERY_RESULT_BACKEND` = `rediss://default:PASSWORD@living-sculpin-96916.upstash.io:6379/1`

This bypasses the settings logic entirely.

### Option 2: Use REST API for Queue

Modify ingestion to use Upstash REST API instead of native Redis protocol.

### Option 3: Separate Queue Service

Use a different queue service (e.g., Render Redis, AWS SQS).

## Timeline

| Time | Action | Status |
|------|--------|--------|
| T+0 | Push fix | ✅ Done |
| T+2m | Render deploys | ⏳ In Progress |
| T+3m | Test health | ⏳ Waiting |
| T+4m | Create resource | ⏳ Waiting |
| T+5m | Verify edge worker | ⏳ Waiting |
| T+10m | Full pipeline test | ⏳ Waiting |

## Next Steps After Success

1. Test with real repository (not test URL)
2. Verify embeddings are generated
3. Test search functionality
4. Monitor performance
5. Check costs (should be $0 on free tiers)
6. Consider upgrading if needed

## Documentation

After successful testing, update:
- `README.md` with deployment instructions
- `DEPLOYMENT_GUIDE.md` with lessons learned
- `TROUBLESHOOTING.md` with common issues

---

**Current Status**: Waiting for deployment (commit 8a576fe3)  
**Next**: Run Test 1 after 2-3 minutes  
**ETA**: Should be working in 5 minutes
