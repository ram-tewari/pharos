# Authentication Fix Required for Cloud API

**Status**: 🔴 BLOCKED - Authentication middleware enabled but admin token not configured in production

## Problem

The GitHub hybrid storage and ingestion endpoints are returning 403 Forbidden because:

1. ✅ **Authentication middleware is enabled** (fixed in `backend/app/__init__.py`)
2. ❌ **`PHAROS_ADMIN_TOKEN` environment variable not set in Render**
3. ❌ **Code changes not deployed to production**

## Solution Required

### Step 1: Deploy Code Changes
The authentication middleware fix needs to be deployed to https://pharos-cloud-api.onrender.com

**Files Changed**:
- `backend/app/__init__.py` - Re-enabled authentication middleware with admin token support

### Step 2: Set Environment Variable in Render
1. Go to Render Dashboard → pharos-cloud-api service
2. Navigate to Environment tab  
3. Add environment variable:
   - **Key**: `PHAROS_ADMIN_TOKEN`
   - **Value**: `4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74`
4. Deploy the service

### Step 3: Test Authentication
```bash
# Test GitHub endpoint with admin token
curl -X POST https://pharos-cloud-api.onrender.com/api/github/fetch \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74" \
  -H "Content-Type: application/json" \
  -d '{
    "github_uri": "https://raw.githubusercontent.com/tiangolo/fastapi/main/fastapi/__init__.py",
    "branch_reference": "main",
    "start_line": 1,
    "end_line": 20
  }'

# Test LangChain ingestion
curl -X POST https://pharos-cloud-api.onrender.com/api/v1/ingestion/ingest/github.com/langchain-ai/langchain \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74"
```

## Current Architecture

```
┌─────────────────┐    HTTPS     ┌──────────────────┐    Tailscale    ┌─────────────────┐
│   User Query    │ ──────────► │  Render Cloud    │ ──── Funnel ───► │  Local Edge     │
│   + Admin Token │              │  API (CLOUD)     │                  │  Worker (GPU)   │
└─────────────────┘              └──────────────────┘                  └─────────────────┘
                                          │                                       │
                                          │                                       │
                                          ▼                                       ▼
                                 ┌─────────────────┐                   ┌─────────────────┐
                                 │  PostgreSQL     │                   │  nomic-embed    │
                                 │  (NeonDB)       │                   │  (768-dim)      │
                                 └─────────────────┘                   └─────────────────┘
```

## Expected Flow After Fix

1. **User** sends request with `Authorization: Bearer <admin-token>`
2. **Authentication middleware** validates admin token
3. **GitHub/Ingestion endpoints** process request
4. **GitHub hybrid storage** fetches code on-demand
5. **Response** returned with code/ingestion status

## Blocked Operations

Until authentication is fixed, these operations will fail with 403 Forbidden:

- ❌ GitHub code fetching (`/api/github/fetch`)
- ❌ Repository ingestion (`/api/v1/ingestion/ingest/*`)
- ❌ Advanced search with code (`/api/search/advanced` with `include_code: true`)

## Working Operations

These operations work without authentication:

- ✅ Basic search (`/api/search/search/three-way-hybrid`)
- ✅ Health checks (`/health`, `/api/github/health`)
- ✅ Resource listing (`/api/resources`)

## Next Steps

1. **Deploy code changes** to Render
2. **Set PHAROS_ADMIN_TOKEN** in Render environment
3. **Test authentication** with curl commands above
4. **Ingest LangChain repository** for testing
5. **Test GitHub hybrid storage** with code retrieval

**Priority**: HIGH - Blocks GitHub hybrid storage testing and LangChain ingestion