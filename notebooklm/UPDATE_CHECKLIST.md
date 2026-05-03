# NotebookLM Documentation Update Checklist

> **Based on**: `UPDATES_2026_05_02.md` — Linux ingestion fixes, worker reliability patterns

---

## Quick Reference

**What Changed**: 
- ✅ Session rollback fix (prevents cascade failures)
- ✅ Dedicated ingestion executor (prevents /embed starvation)
- ✅ Worker heartbeat + DLQ (reliability patterns)
- ✅ Worker-offline safeguards (refuses jobs if worker offline)
- ✅ Stale temp dir cleanup script
- ✅ Daemonization guides (systemd + NSSM)

**Files Modified**:
- `backend/app/modules/ingestion/ast_pipeline.py`
- `backend/app/modules/search/service.py`
- `backend/app/workers/main_worker.py`
- `backend/app/routers/ingestion.py`

**Files Created**:
- `backend/clear_stale_temp_dirs.py`
- `backend/deployment/pharos-edge-worker.service`
- `backend/deployment/NSSM_WINDOWS_SETUP.md`

---

## File-by-File Update Guide

### 1. `01_PHAROS_OVERVIEW.md`

**Section**: "Production URLs and Key Constants"

**Add**:
```markdown
- **Worker heartbeat**: `POST /api/v1/ingestion/health/worker` (auth required)
- **Worker status**: `GET /api/v1/ingestion/health/worker` (auth required)
```

**Section**: "Two Redis Queues — What They Actually Do"

**Add** (after `ingest_queue` description):
```markdown
- **`pharos:dlq`** — Dead Letter Queue for tasks older than 4 hours. Drained on worker startup.
- **`pharos:worker:last_seen`** — Redis key storing last heartbeat timestamp (10-min TTL).
```

**Section**: "Known Issues & Technical Debt"

**Update** (mark as FIXED):
```markdown
### 1. ~~Session Rollback Missing~~ ✅ FIXED (2026-05-02)
- **Solution**: Added `await session.rollback()` in per-file except block
- **File**: `backend/app/modules/ingestion/ast_pipeline.py:414-430`
- **Impact**: Transient DB errors no longer cascade into 50k+ file failures
```

---

### 2. `02_ARCHITECTURE.md`

**Section**: "High-Level Topology" (diagram)

**Update** diagram to include:
```
┌────────────────────────────────────────────────────────────────┐
│  RENDER — Cloud API (pharos-cloud-api.onrender.com)            │
│  ...                                                           │
│  ✅ NEW: Worker heartbeat endpoints                            │
│  ✅ NEW: Worker-offline safeguards (refuses jobs if offline)   │
└────┬─────────────────┬─────────────────────┬──────────────────┘
     │                 │                     │
     │ SQL             │ Redis REST          │ HTTP (Tailscale)
     ▼                 ▼                     ▼
┌──────────┐   ┌────────────────┐   ┌─────────────────────────┐
│ NeonDB   │   │ Upstash Redis  │   │  LOCAL MACHINE (RTX 4070)│
│ ...      │   │  - pharos:tasks│   │  - WSL2: embed_server.py │
│          │   │  - ingest_queue│   │  - Windows: edge worker  │
│          │   │  - pharos:dlq  │   │    ✅ NEW: Heartbeat     │
│          │   │  - pharos:worker:last_seen │  ✅ NEW: DLQ drain │
└──────────┘   └────────────────┘   └─────────────────────────┘
```

**Section**: "Process inventory"

**Update** "Unified edge worker" bullet:
```markdown
3. **Unified edge worker** — `backend/app/workers/main_worker.py`. Single long-running process that:
   - Loads the local embedding model on the RTX 4070.
   - Serves the FastAPI `/embed` endpoint on port `EDGE_EMBED_PORT` (default 8001).
   - **NEW**: Uses dedicated `ingestion_executor` (4 threads) to prevent /embed starvation.
   - **NEW**: Sends heartbeat to Render API every 60s (`POST /api/v1/ingestion/health/worker`).
   - **NEW**: Drains Dead Letter Queue (DLQ) on startup to replay stale tasks.
   - Blocks on **both** Redis queues with a single connection:
     ```
     BLPOP pharos:tasks ingest_queue 30
     ```
   - **NEW**: Checks task age; moves tasks >4 hours old to `pharos:dlq`.
   - Wraps each handler in try/except with **session rollback** so transient DB errors don't cascade.
```

**Section**: "Failure Modes and Safeguards"

**Add**:
```markdown
- **Edge worker offline** → Render API returns 503 for new ingestion jobs after 5 min without heartbeat. Existing queued tasks moved to DLQ after 4 hours. DLQ drained on worker restart.
- **Transient DB error during ingestion** → Per-file except block calls `session.rollback()` so one failed file doesn't cascade into 50k+ failures.
- **Ingestion starving /embed** → Dedicated `ingestion_executor` (4 threads) isolates ingestion from FastAPI's default thread pool, preventing /embed timeouts.
```

---

### 3. `04_INGESTION_AND_SEARCH.md`

**Section**: "Two Redis Queues — What They Actually Do"

**Add** (after `ingest_queue` description):
```markdown
- **`pharos:dlq`** — Dead Letter Queue. Tasks older than 4 hours are moved here instead of being processed. Worker drains DLQ on startup, replaying up to 1000 tasks. Prevents lost work if worker is offline for extended periods.
```

**Section**: "Pipeline B: GitHub Repository (Bulk)"

**Update** "Worker clones repo..." step:
```markdown
Worker clones repo, parses AST (Tree-Sitter for Python),
creates one Resource per file + one DocumentChunk per function/class/method
      │
      ▼
**NEW**: Per-file try/except with session.rollback() — transient DB errors
no longer cascade into 50k+ file failures
      │
      ▼
Chunks stored with:
  - content = NULL (no code stored)
  - github_uri = raw.githubusercontent.com URL
  - branch_reference = commit SHA or "HEAD"
  - semantic_summary = signature + docstring + deps
  - embedding = NULL (async later)
```

**Section**: "AST Pipeline — `HybridIngestionPipeline.ingest_github_repo`"

**Update** step 4:
```markdown
4. For each code file:
   a. Create a Resource (metadata only — no source stored)
   b. Run Tree-Sitter parse (Python fully supported; others partial)
   c. Extract symbols: functions, classes, methods, top-level assignments
   d. For each symbol create DocumentChunk with:
        content        = None
        github_uri     = raw.githubusercontent.com URL
        branch_reference = commit SHA if available, else "HEAD"
        start_line / end_line
        semantic_summary = "[lang] signature: 'docstring.' deps: [...]"
        embedding      = None (async later)
   e. **NEW**: Wrap in try/except with `await session.rollback()` on error
      - Prevents transient DB errors from cascading into 50k+ file failures
      - Logs error and continues to next file
```

**Section**: "Frequently-Needed Operational Commands"

**Add**:
```markdown
### Check worker status
```bash
curl -H "Authorization: Bearer $PHAROS_ADMIN_TOKEN" \
  https://pharos-cloud-api.onrender.com/api/v1/ingestion/health/worker
# Returns: {"state": "online|degraded|offline", "seconds_since_last_seen": N}
```

### Clean stale temp dirs
```bash
cd backend
python clear_stale_temp_dirs.py --delete
```

### Drain DLQ manually
```bash
# Worker drains DLQ on startup automatically
# To inspect DLQ size:
curl -X POST "$UPSTASH_REDIS_REST_URL" \
  -H "Authorization: Bearer $UPSTASH_REDIS_REST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["LLEN","pharos:dlq"]'
```
```

---

### 4. `05_API_DEPLOYMENT_OPS.md`

**Section**: "Endpoint Catalog (grouped by module)"

**Add** (under "Ingestion" section):
```markdown
### Worker Health (`/api/v1/ingestion/health`)
- `POST /api/v1/ingestion/health/worker` — Record worker heartbeat (auth required)
- `GET /api/v1/ingestion/health/worker` — Query worker state (auth required)
  - Returns: `{"state": "online|degraded|offline", "last_seen_unix": N, "seconds_since_last_seen": N}`
  - `online`: last_seen < 2 min
  - `degraded`: last_seen 2-5 min
  - `offline`: last_seen > 5 min OR key missing
```

**Section**: "Environment Variables (production, Render dashboard)"

**Add** (under "Required"):
```markdown
| `PHAROS_ADMIN_TOKEN` | M2M bearer for Ronin **AND worker heartbeat** |
```

**Section**: "Edge worker / embed server"

**Add**:
```markdown
- `PHAROS_CLOUD_URL` (default `https://pharos-cloud-api.onrender.com`) — Render API URL for heartbeat
- `PHAROS_INGESTION_THREADS` (default `4`) — Dedicated executor threads for ingestion
```

**Section**: "Operational Runbook"

**Add**:
```markdown
### "Worker shows as offline but it's running"

1. Check worker logs for heartbeat errors:
   ```bash
   tail -f backend/edge_worker.log | grep -i heartbeat
   ```
2. Verify `PHAROS_ADMIN_TOKEN` is set in worker env.
3. Verify `PHAROS_CLOUD_URL` is correct.
4. Test heartbeat endpoint manually:
   ```bash
   curl -X POST -H "Authorization: Bearer $PHAROS_ADMIN_TOKEN" \
     https://pharos-cloud-api.onrender.com/api/v1/ingestion/health/worker
   ```
5. Check Render API logs for 401/403 errors.

### "Tasks sitting in queue forever"

1. Check worker status:
   ```bash
   curl -H "Authorization: Bearer $PHAROS_ADMIN_TOKEN" \
     https://pharos-cloud-api.onrender.com/api/v1/ingestion/health/worker
   ```
2. If offline >5 min, Render API will refuse new jobs (503).
3. Check DLQ size:
   ```bash
   curl -X POST "$UPSTASH_REDIS_REST_URL" \
     -H "Authorization: Bearer $UPSTASH_REDIS_REST_TOKEN" \
     -H "Content-Type: application/json" \
     -d '["LLEN","pharos:dlq"]'
   ```
4. Restart worker — DLQ will drain on startup.

### "Stale pharos_ingest_* dirs filling disk"

```bash
cd backend
python clear_stale_temp_dirs.py --delete
```
```

---

### 5. `06_EVOLUTION_AND_HISTORY.md`

**Section**: "Current Status (April 2026)"

**Update** to "Current Status (May 2026)":
```markdown
### ✅ Production-Ready Features

1. **Backend Infrastructure**
   - ...
   - ✅ **NEW (May 2026)**: Worker heartbeat + DLQ (reliability patterns)
   - ✅ **NEW (May 2026)**: Worker-offline safeguards (refuses jobs if offline >5 min)
   - ✅ **NEW (May 2026)**: Session rollback fix (prevents cascade failures)
   - ✅ **NEW (May 2026)**: Dedicated ingestion executor (prevents /embed starvation)
   - ✅ **NEW (May 2026)**: Stale temp dir cleanup script
   - ✅ **NEW (May 2026)**: Daemonization guides (systemd + NSSM)
```

**Section**: "Lessons Learned"

**Add** (under "What Worked"):
```markdown
6. **Dedicated Executors** (May 2026)
   - Isolating ingestion from /embed prevented starvation
   - 4-thread ingestion executor keeps /embed responsive

7. **Heartbeat Pattern** (May 2026)
   - Simple 60s ping gives visibility into worker state
   - Enables worker-offline safeguards in API

8. **DLQ Pattern** (May 2026)
   - 4-hour TTL + drain on startup prevents lost work
   - Capped at 1000 tasks to prevent memory bloat

9. **Session Rollback** (May 2026)
   - One line of code prevents 50k+ cascade failures
   - Critical for production reliability

10. **Daemonization** (May 2026)
    - systemd/NSSM auto-restart makes worker resilient
    - Production-ready without manual intervention
```

**Add** (under "What Didn't Work"):
```markdown
6. **No Session Rollback** (May 2026)
   - Transient DB errors cascaded into massive failures
   - **Lesson**: Always rollback on per-item errors in batch operations

7. **Shared Thread Pool** (May 2026)
   - Ingestion starved /embed, causing search timeouts
   - **Lesson**: Isolate long-running operations in dedicated executors

8. **10s Timeout** (May 2026)
   - Too short for cold-start embedding model loads
   - **Lesson**: Timeouts must account for worst-case cold-start

9. **No Worker Visibility** (May 2026)
   - Couldn't tell if worker was online or offline
   - **Lesson**: Heartbeat is essential for distributed systems

10. **No Stale Task Handling** (May 2026)
    - Tasks sat in queue forever if worker offline
    - **Lesson**: DLQ + TTL prevents unbounded queue growth
```

---

## Summary of Changes

### Critical Fixes (Production Impact)

1. ✅ **Session Rollback** — Prevents cascade failures (90% of Linux kernel failed without this)
2. ✅ **Dedicated Executor** — Prevents /embed starvation during ingestion
3. ✅ **Worker Heartbeat** — Visibility into worker state (online/offline/degraded)
4. ✅ **Worker-Offline Safeguards** — Refuses new jobs if worker offline >5 min
5. ✅ **DLQ + Drain** — Prevents lost work if worker offline for extended periods

### Operational Improvements

6. ✅ **Stale Temp Dir Cleanup** — Reclaims ~3 GB of orphaned clones
7. ✅ **Daemonization Guides** — Auto-restart on crash (systemd + NSSM)
8. ✅ **30s Timeout** — Cold-start tolerant for embedding model loads

### Documentation

9. ✅ **UPDATES_2026_05_02.md** — Comprehensive update document (this file)
10. ✅ **UPDATE_CHECKLIST.md** — File-by-file update guide (this file)

---

## Next Steps

1. **Update NotebookLM Files** — Apply changes from this checklist
2. **Deploy to Render** — Push to main branch (auto-deploys)
3. **Restart Edge Worker** — With new code (heartbeat + DLQ + rollback)
4. **Verify Heartbeat** — Check worker shows as "online"
5. **Re-Ingest Linux** — With rollback fix (should complete without cascade)
6. **Clean Temp Dirs** — Run cleanup script to reclaim ~3 GB

---

**Last Updated**: May 2, 2026  
**Status**: Ready for implementation  
**Priority**: HIGH — Deploy before next large ingestion

