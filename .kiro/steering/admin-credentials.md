# Pharos Admin Credentials

## Production API Access

**API URL**: https://pharos-cloud-api.onrender.com  
**Database**: PostgreSQL (NeonDB)  
**Authentication**: Required for protected endpoints

**Admin Token**: `4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74`

## Environment Variable Setup

**CRITICAL**: The `PHAROS_ADMIN_TOKEN` environment variable must be set in the Render dashboard:

1. Go to Render Dashboard → pharos-cloud-api service
2. Navigate to Environment tab
3. Add environment variable:
   - **Key**: `PHAROS_ADMIN_TOKEN`
   - **Value**: `4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74`
4. Deploy the service

## Authentication Status

**Current Issue**: Authentication middleware is enabled but `PHAROS_ADMIN_TOKEN` may not be set in production environment, causing 403 Forbidden errors.

**Solution**: Set the environment variable in Render dashboard and redeploy.

## Usage

### Authentication Header
```bash
Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74
```

### Example Requests

#### GitHub Code Fetch
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/github/fetch \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74" \
  -H "Content-Type: application/json" \
  -d '{
    "github_uri": "https://raw.githubusercontent.com/user/repo/main/file.py",
    "branch_reference": "main",
    "start_line": 1,
    "end_line": 20
  }'
```

#### Advanced Search with Code
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/search/advanced \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication",
    "strategy": "parent-child",
    "top_k": 5,
    "include_code": true
  }'
```

#### Repository Ingestion
```bash
curl -X POST https://pharos-cloud-api.onrender.com/api/v1/ingestion/ingest/github.com/langchain-ai/langchain \
  -H "Authorization: Bearer 4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74"
```

## Security Notes

- This token provides admin access to all API endpoints
- Required for GitHub code fetching and repository ingestion
- Keep secure and do not share publicly
- Used for testing GitHub hybrid storage functionality

## Related Documentation

- [Pharos + Ronin Quick Reference](PHAROS_RONIN_QUICK_REFERENCE.md)
- [Phase 4 Quick Reference](PHASE_4_QUICK_REFERENCE.md)
- [Product Overview](product.md)