# Pharos Documentation Index

**Last Updated**: April 14, 2026

---

## 📖 Documentation Structure

### Vision & Strategy
Located in `docs/vision/`

- **[PHAROS_RONIN_VISION.md](vision/PHAROS_RONIN_VISION.md)** - Complete technical vision for Pharos + Ronin integration
- **[PHAROS_RONIN_SUMMARY.md](vision/PHAROS_RONIN_SUMMARY.md)** - Executive summary of Pharos + Ronin

### Project Documentation
Located in `docs/`

- **[PHAROS_CODE_AUDIT_REPORT.md](PHAROS_CODE_AUDIT_REPORT.md)** - Code quality audit report
- **[PHAROS_future_steps.md](PHAROS_future_steps.md)** - Future development roadmap

### Backend Documentation
Located in `backend/docs/`

- **[API Documentation](../backend/docs/api/)** - Complete API reference
- **[Architecture](../backend/docs/architecture/)** - System architecture docs
- **[Guides](../backend/docs/guides/)** - Developer guides
- **[Deployment](../backend/docs/deployment/)** - Deployment guides

### Deployment Documentation
Located in `backend/docs/deployment/`

- **[DEPLOY_NOW.md](../backend/docs/deployment/DEPLOY_NOW.md)** - Quick deployment guide (30 min)
- **[PRE_FLIGHT_CHECKLIST.md](../backend/docs/deployment/PRE_FLIGHT_CHECKLIST.md)** - Pre-deployment checklist
- **[RENDER_DEPLOYMENT_SUMMARY.md](../backend/docs/deployment/RENDER_DEPLOYMENT_SUMMARY.md)** - Render deployment summary
- **[SERVERLESS_DEPLOYMENT_SUMMARY.md](../backend/docs/deployment/SERVERLESS_DEPLOYMENT_SUMMARY.md)** - Serverless deployment summary

For detailed deployment guides, see:
- `backend/RENDER_FREE_DEPLOYMENT.md` - Complete Render guide
- `backend/RENDER_DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `backend/UPTIMEROBOT_SETUP.md` - Keep-alive setup

### Steering Documentation
Located in `.kiro/steering/`

- **[product.md](../.kiro/steering/product.md)** - Product vision and goals
- **[tech.md](../.kiro/steering/tech.md)** - Tech stack and constraints
- **[structure.md](../.kiro/steering/structure.md)** - Repository structure
- **[PHAROS_RONIN_QUICK_REFERENCE.md](../.kiro/steering/PHAROS_RONIN_QUICK_REFERENCE.md)** - Quick reference card

---

## 🚀 Quick Links

### Getting Started
1. [Product Overview](../.kiro/steering/product.md) - What is Pharos?
2. [Tech Stack](../.kiro/steering/tech.md) - Technologies used
3. [Setup Guide](../backend/docs/guides/setup.md) - Installation

### Deployment
1. [Deploy Now](../backend/docs/deployment/DEPLOY_NOW.md) - Quick start
2. [Pre-Flight Checklist](../backend/docs/deployment/PRE_FLIGHT_CHECKLIST.md) - Verify before deploy
3. [Render Guide](../backend/RENDER_FREE_DEPLOYMENT.md) - Complete guide

### Development
1. [Architecture Overview](../backend/docs/architecture/overview.md) - System design
2. [API Reference](../backend/docs/api/overview.md) - API endpoints
3. [Developer Guide](../backend/docs/guides/workflows.md) - Common tasks

### Vision & Roadmap
1. [Pharos + Ronin Vision](vision/PHAROS_RONIN_VISION.md) - Complete vision
2. [Quick Reference](../.kiro/steering/PHAROS_RONIN_QUICK_REFERENCE.md) - Quick ref
3. [Future Steps](PHAROS_future_steps.md) - Roadmap

---

## 📂 Directory Structure

```
pharos/
├── docs/                           # Project documentation
│   ├── vision/                     # Vision documents
│   │   ├── PHAROS_RONIN_VISION.md
│   │   └── PHAROS_RONIN_SUMMARY.md
│   ├── PHAROS_CODE_AUDIT_REPORT.md
│   └── PHAROS_future_steps.md
│
├── backend/
│   ├── docs/                       # Backend documentation
│   │   ├── deployment/             # Deployment guides
│   │   │   ├── DEPLOY_NOW.md
│   │   │   ├── PRE_FLIGHT_CHECKLIST.md
│   │   │   ├── RENDER_DEPLOYMENT_SUMMARY.md
│   │   │   └── SERVERLESS_DEPLOYMENT_SUMMARY.md
│   │   ├── api/                    # API reference
│   │   ├── architecture/           # Architecture docs
│   │   └── guides/                 # Developer guides
│   │
│   ├── deployment/                 # Deployment configs
│   │   ├── render.yaml
│   │   ├── Dockerfile.cloud
│   │   ├── deploy_to_render.bat
│   │   └── deploy_to_render.sh
│   │
│   ├── RENDER_FREE_DEPLOYMENT.md   # Complete Render guide
│   ├── RENDER_DEPLOYMENT_CHECKLIST.md
│   └── UPTIMEROBOT_SETUP.md
│
├── .kiro/
│   └── steering/                   # Steering docs
│       ├── product.md
│       ├── tech.md
│       ├── structure.md
│       └── PHAROS_RONIN_QUICK_REFERENCE.md
│
└── README.md                       # Main project README
```

---

## 🔍 Finding What You Need

### "I want to deploy Pharos"
→ Start with [DEPLOY_NOW.md](../backend/docs/deployment/DEPLOY_NOW.md)

### "I want to understand the vision"
→ Read [PHAROS_RONIN_VISION.md](vision/PHAROS_RONIN_VISION.md)

### "I want to develop features"
→ Check [Developer Guide](../backend/docs/guides/workflows.md)

### "I want to understand the API"
→ See [API Reference](../backend/docs/api/overview.md)

### "I want to understand the architecture"
→ Read [Architecture Overview](../backend/docs/architecture/overview.md)

---

## 📝 Documentation Standards

### File Naming
- Use `SCREAMING_SNAKE_CASE.md` for top-level docs
- Use `kebab-case.md` for nested docs
- Include date in filename if time-sensitive

### Structure
- Start with title and metadata (date, status)
- Include table of contents for long docs
- Use clear headings and sections
- Include code examples where relevant
- Link to related documentation

### Maintenance
- Update "Last Updated" date when editing
- Keep documentation in sync with code
- Archive outdated documentation
- Link to canonical sources

---

## 🤝 Contributing

When adding documentation:
1. Place in appropriate directory
2. Update this index
3. Link from related docs
4. Follow naming conventions
5. Include metadata (date, status)

---

**Need help?** Check the [Repository Structure](../.kiro/steering/structure.md) guide.
