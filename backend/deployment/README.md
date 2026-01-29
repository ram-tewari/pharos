# Deployment Configuration

This directory contains all deployment-related files for Neo Alexandria 2.0.

## Contents

### Docker Files
- `Dockerfile` - Standard production Docker image
- `Dockerfile.cloud` - Cloud API deployment (lightweight, 512MB RAM)
- `Dockerfile.edge` - Edge worker deployment (GPU-accelerated)
- `Dockerfile.minimal` - Minimal deployment without ML features
- `.dockerignore` - Files to exclude from Docker builds

### Docker Compose
- `docker-compose.yml` - Full production stack
- `docker-compose.dev.yml` - Development with backing services only
- `docker-compose.edge.yml` - Edge worker configuration
- `docker-compose.minimal.yml` - Minimal deployment

### Setup Scripts
- `setup_edge.ps1` / `setup_edge.sh` - Edge worker setup
- `build-and-test-edge.bat` / `build-and-test-edge.sh` - Edge build and test
- `start.bat` / `start.sh` - Quick start scripts
- `docker-build.bat` / `docker-build.sh` - Docker build helpers

### Deployment Configs
- `render.yaml` - Render.com deployment configuration
- `gunicorn.conf.py` - Gunicorn WSGI server configuration
- `worker.py` - Celery worker entry point
- `neo-alexandria-worker.service` - Systemd service file

### Docker Subdirectory
- `docker/` - Additional Docker configurations and documentation

## Quick Start

### Development (Docker)
```bash
cd deployment
docker-compose -f docker-compose.dev.yml up -d
```

### Production (Docker)
```bash
cd deployment
docker-compose up -d
```

### Edge Worker
```bash
cd deployment
# Windows
.\setup_edge.ps1

# Linux/Mac
./setup_edge.sh
```

## Documentation

For detailed deployment instructions, see:
- [Deployment Guide](../docs/guides/deployment.md)
- [Docker Setup Guide](../docs/guides/DOCKER_SETUP_GUIDE.md)
- [Edge Setup Guide](../docs/guides/phase19-edge-setup.md)
