#!/bin/bash
# Immediate production fixes for Neo Alexandria

echo "=== Neo Alexandria Production Hotfix ==="

# 1. Fix Redis connection
echo "1. Checking Redis status..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "   Redis not running. Starting Redis..."
    sudo systemctl start redis-server || {
        echo "   Failed to start Redis. Setting REDIS_AVAILABLE=false"
        export REDIS_AVAILABLE=false
    }
else
    echo "   Redis is running"
fi

# 2. Add chardet dependency for encoding detection
echo "2. Installing chardet for file encoding detection..."
pip install chardet

# 3. Restart the application
echo "3. Restarting application..."
if [ -f "backend/app/main.py" ]; then
    echo "   Killing existing processes..."
    pkill -f "uvicorn.*main:app" || true
    sleep 2
    
    echo "   Starting application..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    echo "   Application started on port 8000"
else
    echo "   Application files not found in expected location"
fi

# 4. Check application health
echo "4. Waiting for application to start..."
sleep 5

if curl -s http://localhost:8000/api/monitoring/health > /dev/null; then
    echo "   ✅ Application is healthy"
else
    echo "   ❌ Application health check failed"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Users need to re-authenticate (tokens expired)"
echo "2. Configure Redis properly for production"
echo "3. Implement token refresh mechanism"
echo "4. Add file encoding detection to upload endpoint"
echo ""
echo "=== Monitoring ==="
echo "- Health: curl http://localhost:8000/api/monitoring/health"
echo "- Logs: tail -f /var/log/neo-alexandria.log"
echo "- Redis: redis-cli ping"
