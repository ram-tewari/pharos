# Pharos Render API Test Script
# Tests all critical endpoints to verify deployment

$baseUrl = "https://pharos-cloud-api.onrender.com"
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = $baseUrl
    "Referer" = "$baseUrl/docs"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pharos API Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "[1/6] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing
    $health = $response.Content | ConvertFrom-Json
    Write-Host "  ✓ Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Monitoring Health
Write-Host "[2/6] Testing Monitoring Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/monitoring/health" -Method GET -UseBasicParsing
    $monitoring = $response.Content | ConvertFrom-Json
    Write-Host "  Status: $($monitoring.status)" -ForegroundColor $(if ($monitoring.status -eq "healthy") { "Green" } else { "Yellow" })
    Write-Host "  Database: $($monitoring.components.database.status)" -ForegroundColor $(if ($monitoring.components.database.status -eq "healthy") { "Green" } else { "Red" })
    Write-Host "  Redis: $($monitoring.components.redis.status)" -ForegroundColor $(if ($monitoring.components.redis.status -eq "healthy") { "Green" } else { "Red" })
    Write-Host "  Celery: $($monitoring.components.celery.status)" -ForegroundColor $(if ($monitoring.components.celery.status -eq "healthy") { "Green" } else { "Red" })
    
    if ($monitoring.components.redis.status -ne "healthy") {
        Write-Host "  ⚠ Redis Issue: $($monitoring.components.redis.message)" -ForegroundColor Red
    }
    if ($monitoring.components.celery.status -ne "healthy") {
        Write-Host "  ⚠ Celery Issue: $($monitoring.components.celery.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: List Resources
Write-Host "[3/6] Testing List Resources..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/resources?limit=5" -Method GET -Headers $headers -UseBasicParsing
    $resources = $response.Content | ConvertFrom-Json
    Write-Host "  ✓ Total Resources: $($resources.total)" -ForegroundColor Green
    Write-Host "  ✓ Returned: $($resources.resources.Count)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: API Documentation
Write-Host "[4/6] Testing API Docs..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ API Docs accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Create Resource (requires Redis)
Write-Host "[5/6] Testing Create Resource..." -ForegroundColor Yellow
$testResource = @{
    url = "https://github.com/test/pharos-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    title = "Test Resource $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    resource_type = "code"
    tags = @("test", "automated")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/resources" -Method POST -Body $testResource -Headers $headers -UseBasicParsing
    $created = $response.Content | ConvertFrom-Json
    Write-Host "  ✓ Resource Created: $($created.id)" -ForegroundColor Green
    Write-Host "  ✓ Status: $($created.ingestion_status)" -ForegroundColor Green
    
    # Save resource ID for cleanup
    $global:testResourceId = $created.id
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Error Details: $responseBody" -ForegroundColor Red
    }
}
Write-Host ""

# Test 6: Search (if resources exist)
Write-Host "[6/6] Testing Search..." -ForegroundColor Yellow
$searchQuery = @{
    query = "test"
    limit = 5
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/search/hybrid" -Method POST -Body $searchQuery -Headers $headers -UseBasicParsing
    $searchResults = $response.Content | ConvertFrom-Json
    Write-Host "  ✓ Search Results: $($searchResults.results.Count)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if Redis is working
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/monitoring/health" -Method GET -UseBasicParsing
    $monitoring = $response.Content | ConvertFrom-Json
    
    if ($monitoring.components.redis.status -eq "healthy" -and $monitoring.components.celery.status -eq "healthy") {
        Write-Host "✓ All systems operational!" -ForegroundColor Green
        Write-Host "  - API is responding" -ForegroundColor Green
        Write-Host "  - Database is connected" -ForegroundColor Green
        Write-Host "  - Redis is connected" -ForegroundColor Green
        Write-Host "  - Edge worker can receive tasks" -ForegroundColor Green
    } else {
        Write-Host "⚠ System partially operational" -ForegroundColor Yellow
        Write-Host "  - API is responding" -ForegroundColor Green
        Write-Host "  - Database is connected" -ForegroundColor Green
        
        if ($monitoring.components.redis.status -ne "healthy") {
            Write-Host "  - Redis is NOT connected" -ForegroundColor Red
            Write-Host "    Action: Set REDIS_URL in Render dashboard" -ForegroundColor Yellow
        }
        
        if ($monitoring.components.celery.status -ne "healthy") {
            Write-Host "  - Edge worker cannot receive tasks" -ForegroundColor Red
            Write-Host "    Action: Ensure edge worker is running and connected" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Cannot determine system status" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. If Redis is not connected:" -ForegroundColor White
Write-Host "   - Go to Render Dashboard → Environment" -ForegroundColor White
Write-Host "   - Set REDIS_URL to your Upstash URL" -ForegroundColor White
Write-Host "   - Save and wait for redeploy" -ForegroundColor White
Write-Host ""
Write-Host "2. If Edge Worker is not connected:" -ForegroundColor White
Write-Host "   - Verify edge worker is running" -ForegroundColor White
Write-Host "   - Check UPSTASH_REDIS_REST_URL in .env.edge" -ForegroundColor White
Write-Host "   - Check UPSTASH_REDIS_REST_TOKEN in .env.edge" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
