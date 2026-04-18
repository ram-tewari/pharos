# Restart Edge Worker with Fix

## What Changed

The edge worker now:
1. Fetches resource from database using `resource_id`
2. Extracts text from `title` + `description`
3. Generates embedding from that text
4. Updates resource with embedding
5. Sets `ingestion_status` to "completed"
6. Sets `ingestion_completed_at` timestamp

## How to Restart

1. **Stop current edge worker**: Press `Ctrl+C` in the terminal where it's running

2. **Start it again**:
```powershell
cd C:\Users\rooma\PycharmProjects\pharos\backend
./start_edge_worker_simple.ps1
```

3. **Test it**:
```powershell
# In another terminal
cd C:\Users\rooma\PycharmProjects\pharos\backend
./test_end_to_end_flow.ps1
```

## What You Should See

### In Edge Worker Terminal:
```
Received task: <uuid>
Processing task <uuid> for resource <uuid>
Extracted text (XX chars) from resource <uuid>
Generated embedding (768 dims) in XXXms
Stored embedding for resource <uuid>
Task completed (total: 1 processed, 0 failed)
```

### Resource Status:
```powershell
# Check resource status
$resource = Invoke-RestMethod -Uri "https://pharos-cloud-api.onrender.com/api/resources/<resource-id>" -Method GET
$resource.ingestion_status  # Should be "completed"
```

## If It Still Fails

Check the error message in the edge worker logs. Common issues:
- Database connection timeout (NeonDB auto-suspend)
- Missing resource in database
- Embedding generation failure

---

**Status**: Ready to test
**Next**: Restart edge worker and run test
