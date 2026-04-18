# Deployment Documentation

Complete guide to deploying Pharos in various configurations.

## Quick Start

**Want to deploy in 5 minutes?** → [Quickstart Guide](quickstart.md)

## Deployment Options

### 1. Render Cloud API (Recommended)
**Best for**: Production deployment with zero infrastructure management

- [Render Deployment Guide](render.md) - Complete Render setup
- [Environment Variables](environment.md) - All configuration options

### 2. Edge Worker (Local GPU)
**Best for**: Local development with GPU acceleration

- [Edge Worker Setup](edge-worker.md) - Local GPU worker configuration
- [Hybrid Architecture](hybrid-architecture.md) - How edge + cloud work together

### 3. Docker (Local Development)
**Best for**: Local development without GPU

- [Docker Setup](docker.md) - Container-based development

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Render Cloud API                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FastAPI    │  │  PostgreSQL  │  │    Redis     │     │
│  │   (Web)      │  │  (NeonDB)    │  │  (Upstash)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP
┌─────────────────────────────────────────────────────────────┐
│                  Edge Worker (Optional)                     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  GPU Tasks   │  │  Embeddings  │                        │
│  │  (Celery)    │  │  (Local)     │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Decision Tree

**Choose your deployment path:**

```
Do you need GPU acceleration?
├─ No  → Deploy to Render only (quickstart.md)
└─ Yes → Deploy hybrid (render.md + edge-worker.md)

Do you have a custom domain?
├─ Yes → Configure custom domain in Render
└─ No  → Use *.onrender.com subdomain

Do you need high availability?
├─ Yes → Use Render paid plan ($7/mo+)
└─ No  → Use Render free tier (sleeps after 15min)
```

## Documentation Index

### Getting Started
- [Quickstart Guide](quickstart.md) - 5-minute Render deployment
- [Environment Variables](environment.md) - Configuration reference

### Cloud Deployment
- [Render Deployment](render.md) - Complete Render setup guide
- [Monitoring Setup](monitoring.md) - Uptime monitoring with UptimeRobot

### Edge Deployment
- [Edge Worker Setup](edge-worker.md) - Local GPU worker
- [Hybrid Architecture](hybrid-architecture.md) - Edge + Cloud explained

### Advanced
- [Docker Setup](docker.md) - Container-based development
- [Troubleshooting](troubleshooting.md) - Common issues and fixes

## Support

- **Issues**: See [troubleshooting.md](troubleshooting.md)
- **Architecture**: See [../architecture/overview.md](../architecture/overview.md)
- **API Reference**: See [../api/overview.md](../api/overview.md)

---

**Last Updated**: 2026-04-17  
**Status**: Production Ready
