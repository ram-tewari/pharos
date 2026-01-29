# Configuration Files

This directory contains all configuration files for Neo Alexandria 2.0.

## Contents

### Environment Templates
- `.env.example` - Example environment configuration
- `.env.cloud.template` - Cloud API environment template
- `.env.edge.template` - Edge worker environment template
- `.env.staging` - Staging environment configuration

### Application Config
- `retraining_config.json` - ML model retraining configuration
- `training_config.json` - ML model training configuration

### Requirements Files
- `requirements.txt` - Full production dependencies
- `requirements-base.txt` - Base dependencies (minimal)
- `requirements-cloud.txt` - Cloud API dependencies
- `requirements-edge.txt` - Edge worker dependencies
- `requirements-minimal.txt` - Minimal deployment dependencies
- `requirements-ml.txt` - ML/AI dependencies
- `requirements-processing.txt` - Data processing dependencies
- `runtime.txt` - Python runtime version

### Tool Configuration
- `pytest.ini` - Pytest configuration
- `alembic.ini` - Alembic database migration configuration

### Monitoring
- `monitoring/` - Prometheus and Grafana configurations

## Environment Setup

### Development
```bash
cp .env.example ../.env
# Edit ../.env with your configuration
```

### Cloud Deployment
```bash
cp .env.cloud.template ../.env
# Edit ../.env with cloud-specific settings
```

### Edge Deployment
```bash
cp .env.edge.template ../.env
# Edit ../.env with edge-specific settings
```

## Requirements Installation

### Full Installation
```bash
pip install -r requirements.txt
```

### Minimal Installation
```bash
pip install -r requirements-minimal.txt
```

### Cloud API Only
```bash
pip install -r requirements-cloud.txt
```

### Edge Worker Only
```bash
pip install -r requirements-edge.txt
```

## Documentation

For detailed configuration instructions, see:
- [Setup Guide](../docs/guides/setup.md)
- [Requirements Strategy](../docs/guides/REQUIREMENTS_STRATEGY.md)
- [Environment Configuration](../docs/guides/deployment.md#environment-variables)
