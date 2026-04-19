# Authentication Fixed - Admin Token Support

**Status**: ✅ FIXED - Admin token authentication now supported

## Changes Made

### 1. Re-enabled Authentication Middleware (`backend/app/__init__.py`)
- Uncommented and simplified authentication middleware
- Removed complex JWT validation dependencies
- Added admin token check before JWT validation
- Added public endpoint exclusions (search, health checks)

### 2. Updated Security Module (`backend/app/shared/security.py`)
- Modified `get_current_user()` to check for admin token first
- Admin token bypasses JWT decoding
- Returns admin TokenData when admin token is used

## Admin Token

**Token**: `4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74`

**Environment Variable**: `PHAROS_ADMIN_TOKEN` (must be set in Render)

## How It Works

```python
# 1. Request comes in with Authorization header
Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74

# 2. Authentication middleware checks admin token
if token == os.getenv("PHAROS_ADMIN_TOKEN"):
    request.state.user = {"user_id": "admin", ...}
    
# 3. Endpoint dependency also checks admin token
async def get_current_user(token: str):
    if token == os.getenv("PHAROS_ADMIN_TOKEN"):
        return TokenData(user_id="admin", tier="admin")
```

## Testing

### Test GitHub Fetch
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/github/fetch \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74" \
  -H "Content-Type: application/json" \
  -d '{
    "github_uri": "https://raw.githubusercontent.com/tiangolo/fastapi/main/fastapi/__init__.py",
    "branch_reference": "main",
    "start_line": 1,
    "end_line": 20
  }'
```

### Test LangChain Ingestion
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/v1/ingestion/ingest/github.com/langchain-ai/langchain \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74"
```

## Deployment Required

**CRITICAL**: These changes need to be deployed to production:

1. **Commit changes**:
   - `backend/app/__init__.py` (authentication middleware)
   - `backend/app/shared/security.py` (admin token support)

2. **Set environment variable in Render**:
   - Key: `PHAROS_ADMIN_TOKEN`
   - Value: `4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74`

3. **Deploy to Render**

## Expected Behavior After Deployment

✅ **GitHub endpoints**: Accept admin token  
✅ **Ingestion endpoints**: Accept admin token  
✅ **Search endpoints**: Public access (no auth required)  
✅ **Health endpoints**: Public access (no auth required)  

## Files Changed

1. `backend/app/__init__.py` - Re-enabled authentication middleware
2. `backend/app/shared/security.py` - Added admin token support to `get_current_user()`
3. `.kiro/steering/admin-credentials.md` - Updated with deployment instructions
4. `.kiro/steering/tech.md` - Updated to reflect cloud API usage
5. `.kiro/steering/PHAROS_RONIN_QUICK_REFERENCE.md` - Updated API URLs

## Next Steps

1. ✅ Code changes complete
2. ⏳ Deploy to Render
3. ⏳ Set PHAROS_ADMIN_TOKEN in Render environment
4. ⏳ Test authentication with admin token
5. ⏳ Ingest LangChain repository
6. ⏳ Test GitHub hybrid storage with code retrieval