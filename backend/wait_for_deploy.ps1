# Wait for Render deployment and test Redis connection

$baseUrl = "https://pharos-cloud-api.onrender.com"
$maxAttempts = 30
$sleepSeconds = 10

Write-Host "`n=== Waiting for Render Deployment ===" -ForegroundColor Cyan
Write-Host "This will check every $sleepSeconds seconds for up to $($maxAttempts * $sleepSeconds / 60) minutes`n" -ForegroundColor Yellow

for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "[$i/$maxAttempts] Checking deployment status..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/monitoring/health" -Method GET -UseBasicParsing -TimeoutSec 5
        $health = $response.Content | ConvertFrom-Json
        
        $redisStatus = $health.components.redis.status
        $celeryStatus = $health.components.celery.status
        
        Write-Host "  Redis: $redisStatus" -ForegroundColor $(if ($redisStatus -eq "healthy") {"Green"} else {"Yellow"})
        Write-Host "  Celery: $celeryStatus" -ForegroundColor $(if ($celeryStatus -eq "healthy") {"Green"} else {"Yellow"})
        
        if ($redisStatus -eq "healthy" -and $celeryStatus -eq "healthy") {
            Write-Host "`n✓ Deployment successful! All systems healthy." -ForegroundColor Green
            Write-Host "`nFull Status:" -ForegroundColor Cyan
            Write-Host $response.Content
            exit 0
        }
        
        if ($redisStatus -ne "healthy") {
            Write-Host "  Issue: $($health.components.redis.message)" -ForegroundColor Red
        }
        if ($celeryStatus -ne "healthy") {
            Write-Host "  Issue: $($health.components.celery.message)" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($i -lt $maxAttempts) {
        Write-Host "  Waiting $sleepSeconds seconds...`n" -ForegroundColor Gray
        Start-Sleep -Seconds $sleepSeconds
    }
}

Write-Host "`n⚠ Deployment did not complete within timeout" -ForegroundColor Yellow
Write-Host "Check Render dashboard for deployment status" -ForegroundColor Yellow
