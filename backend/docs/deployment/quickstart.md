# Pharos Deployment - 5-Minute Quickstart

Deploy Pharos to production in 5 minutes using Render's free tier.

## Prerequisites

- GitHub account
- Render account (sign up at [render.com](https://render.com))
- 5 minutes

## Step 1: Fork Repository

```bash
# Fork the repository on GitHub
# Or clone and push to your own repo
git clone https://github.com/yourusername/pharos
cd pharos
```

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

## Step 3: Deploy

1. Click **"New +"** → **"Web Service"**
2. Select your `pharos` repository
3. Configure:
   - **Name**: `pharos-api`
   - **Region**: Oregon (or closest)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Plan**: Free

4. Render auto-detects `render.yaml` and sets:
   - Build Command: `pip install && alembic upgrade head`
   - Start Command: `gunicorn app.main:app`
   - Environment variables (auto-populated)

5. Click **"Create Web Service"**

## Step 4: Wait for Deployment

Render will:
1. Clone repository (~30s)
2. Build Docker image (~5-10 min)
3. Run database migrations (~30s)
4. Start service (~30s)

**Total time**: ~10-15 minutes

## Step 5: Verify

Once deployed, test your API:

```bash
# Replace with your Render URL
curl https://pharos-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "2.0.0"
}
```

## Step 6: View API Documentation

Open in browser:
```
https://pharos-api.onrender.com/docs
```

You should see the FastAPI Swagger UI with all endpoints.

## Step 7: Get Your API Key

1. Go to Render Dashboard
2. Click on your service
3. Go to **Environment** tab
4. Copy `PHAROS_ADMIN_TOKEN`

Save this - you'll need it for API requests.

## Step 8: Test Context Retrieval

```bash
curl -X POST https://pharos-api.onrender.com/api/context/retrieve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PHAROS_ADMIN_TOKEN" \
  -d '{
    "query": "authentication",
    "codebase": "test-repo",
    "max_chunks": 5
  }'
```

## Done! 🎉

Your Pharos API is now live at:
```
https://pharos-api.onrender.com
```

## What's Included

- ✅ FastAPI backend
- ✅ PostgreSQL database (NeonDB)
- ✅ Redis cache (Upstash)
- ✅ Automatic SSL/HTTPS
- ✅ Health monitoring
- ✅ Auto-deploy on git push

## Cost

**Free tier includes**:
- 512MB RAM
- 750 hours/month
- Sleeps after 15 min inactivity
- 50-second cold start

**Upgrade to paid** ($7/mo) for:
- Always-on (no sleep)
- Instant response
- More RAM/CPU

## Next Steps

### Optional: Add Keep-Alive Monitoring

Prevent cold starts with [UptimeRobot](https://uptimerobot.com):

1. Sign up (free)
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://pharos-api.onrender.com/health`
   - Interval: 5 minutes
3. Done!

### Optional: Add Local GPU Worker

For GPU-accelerated embeddings:

1. See [edge-worker.md](edge-worker.md)
2. Install dependencies
3. Run `start_edge_worker.ps1`

### Optional: Custom Domain

1. Go to Render Dashboard → Settings
2. Add custom domain
3. Update DNS records
4. Done!

## Troubleshooting

### 502 Bad Gateway

**Cause**: Service is starting (cold start)  
**Solution**: Wait 50 seconds and retry

### Database Connection Error

**Cause**: DATABASE_URL incorrect  
**Solution**: Check environment variables in Render

### 401 Unauthorized

**Cause**: Missing API key  
**Solution**: Add `X-API-Key` header with your token

## Support

- [Full Deployment Guide](render.md)
- [Environment Variables](environment.md)
- [Troubleshooting](troubleshooting.md)
- [Architecture Overview](../architecture/overview.md)

---

**Deployment Time**: 5 minutes (setup) + 10 minutes (build)  
**Cost**: $0/month (free tier)  
**Status**: Production Ready
