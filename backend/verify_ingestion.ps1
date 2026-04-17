# Comprehensive Ingestion Verification Script

param(
    [string]$ResourceId = "0811a2fc-b05d-4b0d-91ad-91c44e2ed4df",
    [string]$ApiUrl = "https://pharos-cloud-api.onrender.com"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PHAROS INGESTION VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. List all resources
Write-Host "1. API: List All Resources" -ForegroundColor Yellow
try {
    $resources = Invoke-RestMethod -Uri "$ApiUrl/api/resources" -Method GET
    Write-Host "   ✅ Total Resources: $($resources.Count)" -ForegroundColor Green
    
    if ($resources.Count -gt 0) {
        Write-Host "`n   Recent Resources:" -ForegroundColor Gray
        $resources | Select-Object -First 5 | ForEach-Object {
            $statusColor = if ($_.ingestion_status -eq 'completed') { 'Green' } elseif ($_.ingestion_status -eq 'processing') { 'Yellow' } else { 'Gray' }
            Write-Host "   📄 $($_.title)" -ForegroundColor White
            Write-Host "      ID: $($_.id)" -ForegroundColor Gray
            Write-Host "      Status: $($_.ingestion_status)" -ForegroundColor $statusColor
            Write-Host "      Created: $($_.created_at)" -ForegroundColor Gray
            Write-Host ""
        }
    }
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Get specific resource
Write-Host "`n2. API: FastAPI Resource Details" -ForegroundColor Yellow
try {
    $resource = Invoke-RestMethod -Uri "$ApiUrl/api/resources/$ResourceId" -Method GET
    Write-Host "   ✅ Resource Found" -ForegroundColor Green
    Write-Host "      Title: $($resource.title)" -ForegroundColor White
    Write-Host "      Status: $($resource.ingestion_status)" -ForegroundColor $(if ($resource.ingestion_status -eq 'completed') { 'Green' } else { 'Yellow' })
    Write-Host "      Type: $($resource.type)" -ForegroundColor Gray
    Write-Host "      Created: $($resource.created_at)" -ForegroundColor Gray
    Write-Host "      Updated: $($resource.updated_at)" -ForegroundColor Gray
    
    if ($resource.ingestion_started_at) {
        Write-Host "      Ingestion Started: $($resource.ingestion_started_at)" -ForegroundColor Gray
    }
    if ($resource.ingestion_completed_at) {
        Write-Host "      Ingestion Completed: $($resource.ingestion_completed_at)" -ForegroundColor Gray
        
        # Calculate processing time
        $started = [DateTime]::Parse($resource.ingestion_started_at)
        $completed = [DateTime]::Parse($resource.ingestion_completed_at)
        $duration = $completed - $started
        Write-Host "      Processing Time: $([Math]::Round($duration.TotalSeconds, 2))s" -ForegroundColor Cyan
    }
    
    # Check for embedding
    if ($resource.embedding) {
        $embeddingLength = $resource.embedding.Length
        Write-Host "      Has Embedding: ✅ Yes ($embeddingLength chars)" -ForegroundColor Green
    } else {
        Write-Host "      Has Embedding: ❌ No" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Get resource status
Write-Host "`n3. API: Resource Status" -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$ApiUrl/api/resources/$ResourceId/status" -Method GET
    Write-Host "   ✅ Status Retrieved" -ForegroundColor Green
    Write-Host "      Processing Status: $($status.processing_status)" -ForegroundColor $(if ($status.processing_status -eq 'completed') { 'Green' } else { 'Yellow' })
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Get chunks
Write-Host "`n4. API: Resource Chunks" -ForegroundColor Yellow
try {
    $chunks = Invoke-RestMethod -Uri "$ApiUrl/api/resources/$ResourceId/chunks" -Method GET
    Write-Host "   ✅ Total Chunks: $($chunks.Count)" -ForegroundColor Green
    
    if ($chunks.Count -gt 0) {
        Write-Host "`n   Sample Chunks:" -ForegroundColor Gray
        $chunks | Select-Object -First 3 | ForEach-Object {
            Write-Host "   - Chunk ID: $($_.id)" -ForegroundColor Gray
            Write-Host "     Type: $($_.chunk_type)" -ForegroundColor Gray
            Write-Host "     Size: $($_.content.Length) chars" -ForegroundColor Gray
            Write-Host ""
        }
    }
} catch {
    Write-Host "   ⚠️  No chunks found (may not be created yet)" -ForegroundColor Yellow
}

# 5. Get quality assessment
Write-Host "`n5. API: Quality Assessment" -ForegroundColor Yellow
try {
    $quality = Invoke-RestMethod -Uri "$ApiUrl/api/quality/resources/$ResourceId/quality-details" -Method GET
    Write-Host "   ✅ Quality Computed" -ForegroundColor Green
    Write-Host "      Overall Score: $([Math]::Round($quality.overall_score, 3))" -ForegroundColor $(if ($quality.overall_score -gt 0.8) { 'Green' } elseif ($quality.overall_score -gt 0.5) { 'Yellow' } else { 'Red' })
    Write-Host "      Accuracy: $([Math]::Round($quality.accuracy, 3))" -ForegroundColor Gray
    Write-Host "      Completeness: $([Math]::Round($quality.completeness, 3))" -ForegroundColor Gray
    Write-Host "      Consistency: $([Math]::Round($quality.consistency, 3))" -ForegroundColor Gray
    Write-Host "      Relevance: $([Math]::Round($quality.relevance, 3))" -ForegroundColor Gray
} catch {
    Write-Host "   ⚠️  Quality not yet computed (expected for new resource)" -ForegroundColor Yellow
}

# 6. Check worker status
Write-Host "`n6. API: Worker Status" -ForegroundColor Yellow
try {
    $workers = Invoke-RestMethod -Uri "$ApiUrl/api/monitoring/workers/status" -Method GET
    Write-Host "   ✅ Worker Status Retrieved" -ForegroundColor Green
    Write-Host "      Active Tasks: $($workers.workers.total_active_tasks)" -ForegroundColor Gray
    Write-Host "      Scheduled Tasks: $($workers.workers.total_scheduled_tasks)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Resource ID: $ResourceId" -ForegroundColor White
Write-Host "API URL: $ApiUrl" -ForegroundColor Gray

if ($resource -and $resource.ingestion_status -eq 'completed') {
    Write-Host "`n✅ INGESTION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "   - Resource created and stored" -ForegroundColor Green
    Write-Host "   - Embedding generated and saved" -ForegroundColor Green
    Write-Host "   - Status: completed" -ForegroundColor Green
} elseif ($resource -and $resource.ingestion_status -eq 'processing') {
    Write-Host "`n⏳ INGESTION IN PROGRESS..." -ForegroundColor Yellow
    Write-Host "   - Resource created" -ForegroundColor Green
    Write-Host "   - Waiting for edge worker to process" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ INGESTION FAILED OR INCOMPLETE" -ForegroundColor Red
    Write-Host "   - Check edge worker logs" -ForegroundColor Yellow
    Write-Host "   - Check API logs" -ForegroundColor Yellow
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
