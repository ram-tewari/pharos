# Quick Pharos API Test
$baseUrl = "https://pharos-cloud-api.onrender.com"

Write-Host "`n=== Pharos API Quick Test ===" -ForegroundColor Cyan

# Test 1: Health
Write-Host "`n[1] Health Check..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    Write-Host "  ✓ API is healthy" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed" -ForegroundColor Red
}

# Test 2: Monitoring
Write-Host "`n[2] System Status..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "$baseUrl/api/monitoring/health" -UseBasicParsing
    $m = $r.Content | ConvertFrom-Json
    Write-Host "  Overall: $($m.status)" -ForegroundColor $(if ($m.status -eq "healthy") {"Green"} else {"Yellow"})
    Write-Host "  Database: $($m.components.database.status)" -ForegroundColor $(if ($m.components.database.status -eq "healthy") {"Green"} else {"Red"})
    Write-Host "  Redis: $($m.components.redis.status)" -ForegroundColor $(if ($m.components.redis.status -eq "healthy") {"Green"} else {"Red"})
    Write-Host "  Celery: $($m.components.celery.status)" -ForegroundColor $(if ($m.components.celery.status -eq "healthy") {"Green"} else {"Red"})
}
catch {
    Write-Host "  ✗ Failed" -ForegroundColor Red
}

# Test 3: List Resources
Write-Host "`n[3] List Resources..." -ForegroundColor Yellow
try {
    $h = @{"Origin" = $baseUrl}
    $r = Invoke-WebRequest -Uri "$baseUrl/api/resources?limit=5" -Headers $h -UseBasicParsing
    $d = $r.Content | ConvertFrom-Json
    Write-Host "  ✓ Total: $($d.total)" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed" -ForegroundColor Red
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "If Redis shows 'unhealthy', set REDIS_URL in Render dashboard" -ForegroundColor Yellow
Write-Host ""
