# End-to-End Flow Test for Pharos Hybrid Architecture
# Tests: Cloud API -> Redis Queue -> Edge Worker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pharos End-to-End Flow Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "https://pharos-cloud-api.onrender.com"
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "$API_URL"
}

# Step 1: Create a test resource
Write-Host "Step 1: Creating test resource..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$guid = [guid]::NewGuid().ToString().Substring(0,8)
$payload = @{
    url = "https://github.com/test/repo-$guid"
    title = "Test Resource - $timestamp"
    resource_type = "code_repository"
    description = "End-to-end test resource"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/resources" -Method POST -Headers $headers -Body $payload
    $resourceId = $response.id
    Write-Host "Success! Resource created: $resourceId" -ForegroundColor Green
    Write-Host "  Status: $($response.ingestion_status)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "Failed to create resource" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Step 2: Wait a moment for queue processing
Write-Host "Step 2: Waiting for queue processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 3: Check resource status
Write-Host "Step 3: Checking resource status..." -ForegroundColor Yellow
try {
    $resource = Invoke-RestMethod -Uri "$API_URL/api/resources/$resourceId" -Method GET -Headers $headers
    Write-Host "Resource status: $($resource.ingestion_status)" -ForegroundColor Green
    
    if ($resource.ingestion_status -eq "pending") {
        Write-Host "  -> Resource is queued, waiting for edge worker" -ForegroundColor Yellow
    } elseif ($resource.ingestion_status -eq "processing") {
        Write-Host "  -> Edge worker is processing!" -ForegroundColor Cyan
    } elseif ($resource.ingestion_status -eq "completed") {
        Write-Host "  -> Processing completed!" -ForegroundColor Green
    } elseif ($resource.ingestion_status -eq "failed") {
        Write-Host "  -> Processing failed: $($resource.ingestion_error)" -ForegroundColor Red
    }
    Write-Host ""
} catch {
    Write-Host "Failed to check resource status" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Step 4: Check health endpoint
Write-Host "Step 4: Checking API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$API_URL/health" -Method GET
    Write-Host "API Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Services:" -ForegroundColor Gray
    foreach ($service in $health.services.PSObject.Properties) {
        $status = $service.Value
        $color = if ($status -eq "healthy") { "Green" } else { "Yellow" }
        Write-Host "    - $($service.Name): $status" -ForegroundColor $color
    }
    Write-Host ""
} catch {
    Write-Host "Failed to check health" -ForegroundColor Red
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resource ID: $resourceId" -ForegroundColor White
Write-Host "Current Status: $($resource.ingestion_status)" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start edge worker: ./start_edge_worker.ps1" -ForegroundColor Gray
Write-Host "2. Edge worker will pick up the job from Redis queue" -ForegroundColor Gray
Write-Host "3. Check status again with the resource ID above" -ForegroundColor Gray
Write-Host ""
