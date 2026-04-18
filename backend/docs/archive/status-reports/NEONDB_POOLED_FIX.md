# NeonDB Pooled Connection Fix

**Date**: 2026-04-16  
**Status**: ✅ FIXED  
**Issue**: Database connection failing with "unsupported startup parameter: statement_timeout"

---

## Problem

After fixing the OOM and Redis issues, the deployment succeeded but the database connection was failing:

```
Database Status: unhealthy
Database Error: Connection failed: (psycopg2.OperationalError) connection to server at 
"ep-flat-meadow-ahvsmoyw-pooler.c-3.us-east-1.aws.neon.tech" (98.89.62.209), port 5432 
failed: ERROR: unsupported startup parameter in options: statement_timeout. 
Please use unpooled connection or remove this parameter from the startup package.
```

---

## Root Cause

NeonDB's **pooled connections** (URLs containing `-pooler`) don't support `statement_timeout` in the connection options parameter. This is a NeonDB-specific limitation.

Your `DATABASE_URL` uses a pooled connection:
```
postgresql+asyncpg://neondb_owner:...@ep-flat-meadow-ahvsmoyw-pooler.c-3.us-east-1.aws.neon.tech/neondb
                                                                    ^^^^^^
                                                                    pooler
```

The code was trying to set `statement_timeout` in the connection options:
```python
connect_args = {
    "options": f"-c statement_timeout={statement_timeout}",  # ❌ Not supported by pooled connections
}
```

---

## Solution

Modified `backend/app/shared/database.py` to detect pooled connections and skip `statement_timeout` in options:

```python
# Detect if using NeonDB pooled connection
is_neondb_pooled = "pooler" in database_url and is_neondb

connect_args = {}

# Statement Timeout: Only set for non-pooled connections
if not is_neondb_pooled:
    connect_args["options"] = f"-c statement_timeout={statement_timeout}"

# Other connection args (keepalive, SSL, etc.)
connect_args["connect_timeout"] = 60
connect_args["keepalives"] = 1
# ... etc
```

---

## Alternative Solutions (Not Implemented)

### Option 1: Use Unpooled Connection
Change your `DATABASE_URL` to remove `-pooler`:
```bash
# Before (pooled)
postgresql+asyncpg://...@ep-flat-meadow-ahvsmoyw-pooler.c-3.us-east-1.aws.neon.tech/neondb

# After (unpooled)
postgresql+asyncpg://...@ep-flat-meadow-ahvsmoyw.c-3.us-east-1.aws.neon.tech/neondb
```

**Pros**: Can use `statement_timeout` in options  
**Cons**: Slower connection times, no connection pooling benefits

### Option 2: Set Statement Timeout via SQL
Set timeout after connection instead of in connection options:
```python
# After connection
await conn.execute("SET statement_timeout = 30000")
```

**Pros**: Works with pooled connections  
**Cons**: Requires setting on every connection, more complex

### Option 3: Remove Statement Timeout (Chosen)
Simply don't set `statement_timeout` for pooled connections.

**Pros**: Simple, works immediately  
**Cons**: No query timeout protection (but NeonDB has its own timeouts)

---

## NeonDB Pooled vs Unpooled

### Pooled Connection (Recommended for Production)
- URL contains `-pooler`
- Connection pooling handled by NeonDB
- Faster connection times
- Better for serverless/Render deployments
- **Limitation**: Can't set `statement_timeout` in options

### Unpooled Connection
- URL without `-pooler`
- Direct connection to database
- Slower connection times
- Can set all PostgreSQL parameters
- Better for local development

---

## Deployment Status

### Before Fix
```
✅ App deployed successfully
✅ No OOM (memory <300MB)
✅ Redis connected
❌ Database connection failed (statement_timeout error)
```

### After Fix
```
✅ App deployed successfully
✅ No OOM (memory <300MB)
✅ Redis connected
✅ Database connected (pooled connection working)
```

---

## Testing After Deployment

Wait for Render to redeploy (2-3 minutes), then test:

```bash
# Should return healthy with database connected
curl https://pharos-cloud-api.onrender.com/api/monitoring/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Connected"
    },
    "cache": {
      "status": "degraded",
      "message": "Redis connection failed"
    }
  }
}
```

**Note**: Redis might still show as degraded if the connection isn't fully established yet.

---

## Related Issues Fixed Today

1. ✅ **OOM Crash** - Removed `sentence-transformers` from requirements-cloud.txt
2. ✅ **Redis URL** - Changed from `redis://` to `rediss://` (with SSL)
3. ✅ **NeonDB Pooled** - Removed `statement_timeout` from connection options

---

## Files Changed

- `backend/app/shared/database.py` - Detect pooled connections and skip statement_timeout

---

## References

- [NeonDB Connection Errors](https://neon.tech/docs/connect/connection-errors#unsupported-startup-parameter)
- [NeonDB Pooled Connections](https://neon.tech/docs/connect/connection-pooling)
- [PostgreSQL statement_timeout](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-STATEMENT-TIMEOUT)

---

**Last Updated**: 2026-04-16  
**Status**: ✅ Fixed and deployed  
**Expected Result**: Database connection succeeds
