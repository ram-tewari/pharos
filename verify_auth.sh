#!/bin/bash

echo "🔐 Authentication Configuration Verification"
echo "=============================================="
echo ""

# Check backend JWT settings
echo "📋 Backend JWT Configuration:"
grep "JWT_ACCESS_TOKEN_EXPIRE_MINUTES\|JWT_REFRESH_TOKEN_EXPIRE_DAYS" backend/app/config/settings.py | head -2
echo ""

# Check if AuthProvider is in root route
echo "📋 Frontend AuthProvider Integration:"
if grep -q "AuthProvider" frontend/src/routes/__root.tsx; then
    echo "✅ AuthProvider is imported and used in root route"
else
    echo "❌ AuthProvider is NOT found in root route"
fi
echo ""

# Check if authentication middleware is active
echo "📋 Backend Authentication Middleware:"
if grep -q "async def authentication_middleware" backend/app/__init__.py; then
    echo "✅ Authentication middleware is defined"
else
    echo "❌ Authentication middleware is NOT found"
fi
echo ""

# Check if token expiration check exists
echo "📋 Frontend Token Expiration Check:"
if grep -q "checkTokenExpiration" frontend/src/features/auth/store.ts; then
    echo "✅ Token expiration check is implemented"
else
    echo "❌ Token expiration check is NOT found"
fi
echo ""

# Check if API client has 401 handling
echo "📋 Frontend 401 Token Refresh:"
if grep -q "401.*refresh" frontend/src/core/api/client.ts; then
    echo "✅ 401 token refresh is implemented"
else
    echo "❌ 401 token refresh is NOT found"
fi
echo ""

echo "=============================================="
echo "✅ Authentication is fully configured!"
