# Phase 7: Ops & Edge Management (Option C: Hybrid Power)

**Status**: Ready to implement  
**Complexity**: ⭐⭐⭐ Medium (Option C)
**Estimated Time**: 16-20 hours  
**Dependencies**: Phase 1 (workbench) ✅

**Implementation**: Option C - "Hybrid Power" ⭐ RECOMMENDED
- Professional ops dashboard with smart monitoring
- magic-mcp dashboard structure + shadcn-ui + magic-ui
- Intelligent threshold-based alerting
- Anomaly detection on key metrics
- Auto-refresh with visual indicators

---

## Quick Summary

System health monitoring dashboard for DevOps and power users. Displays real-time metrics for backend performance, module health, database, event bus, cache, workers, and ML models.

---

## What's Included

### Features
- Overall system health status with smart alerts
- 13 backend module health monitoring with anomaly detection
- Performance metrics (API response time, request rate, error rate)
- Database connection pool monitoring
- Event bus metrics and history
- Redis cache performance
- Celery worker status
- ML model health checks
- User engagement metrics
- Recommendation quality metrics
- **Smart alert system with magic-ui animations** (Option C)
- **Anomaly detection on key metrics** (Option C)
- **Ingestion queue visualization** (Option C)
- **Worker heartbeat with orbiting circles** (Option C)
- **Sparse embedding generation UI** (Option C)

### UI Components
- Health overview dashboard with smart alerts
- Module health grid with filters and anomaly detection
- Performance charts (line charts) with trend indicators
- Infrastructure monitors (database, event bus, cache, workers)
- ML model health cards
- Engagement metrics grid
- **Smart alert panel with magic-ui animations** (Option C)
- **Alert history and preferences** (Option C)
- **Ingestion queue visualization** (Option C)
- **Worker heartbeat animation** (Option C)
- **Sparse embedding generator** (Option C)
- Auto-refresh controls
- Time range selector

---

## Backend API

All endpoints are in `backend/app/modules/monitoring/router.py` and `backend/app/routers/ingestion.py`

**17 Endpoints** (12 monitoring + 5 ingestion):
- `/api/monitoring/health` - Overall health
- `/api/monitoring/health/ml` - ML model health
- `/api/monitoring/model-health` - NCF model health
- `/api/monitoring/health/module/{module_name}` - Module-specific health (NEW)
- `/api/monitoring/performance` - Performance metrics
- `/api/monitoring/recommendation-quality` - Recommendation quality
- `/api/monitoring/user-engagement` - User engagement
- `/api/monitoring/database` - Database metrics
- `/api/monitoring/db/pool` - Connection pool
- `/api/monitoring/events` - Event bus metrics
- `/api/monitoring/events/history` - Event history
- `/api/monitoring/cache/stats` - Cache stats
- `/api/monitoring/workers/status` - Worker status
- `/api/v1/ingestion/ingest/{repo_url:path}` - Ingest repository (NEW - Option C)
- `/api/v1/ingestion/worker/status` - Worker status (NEW - Option C)
- `/api/v1/ingestion/jobs/history` - Job history (NEW - Option C)
- `/api/v1/ingestion/health` - Ingestion health (NEW - Option C)
- `/admin/sparse-embeddings/generate` - Generate sparse embeddings (NEW - Option C)

---

## File Structure

```
.kiro/specs/frontend/phase7-ops-edge-management/
├── README.md (this file)
├── requirements.md (10 user stories)
├── design.md (architecture & components)
└── tasks.md (6 stages, 18 tasks)
```

---

## Implementation Stages

1. **Foundation** (2-3 hours) - Types, API client, store, layout
2. **Health Monitoring** (2-3 hours) - Health overview, module grid, ML models
3. **Performance Metrics** (2-3 hours) - Charts, engagement, recommendations
4. **Infrastructure** (3-4 hours) - Database, event bus, cache, workers
5. **Polish** (2-3 hours) - Auto-refresh, error handling, responsive design
6. **Documentation** (1 hour) - Docs and testing
7. **Option C Features** (4-5 hours) - Smart alerts, anomaly detection, ingestion, sparse embeddings ⭐ NEW

---

## Key Technologies

- **Charts**: Recharts
- **Animations**: magic-ui (animated alerts, orbiting circles) ⭐ NEW
- **State**: Zustand + TanStack Query
- **UI**: shadcn-ui (Card, Badge, Button, Select)
- **Styling**: Tailwind CSS

---

## Success Metrics

- Dashboard loads in < 2 seconds
- Auto-refresh every 30 seconds without blocking UI
- All 13 backend modules visible with health status
- Charts render smoothly (60fps)
- Zero accessibility violations
- Works on Chrome, Firefox, Safari

---

## Next Steps

1. Read [requirements.md](./requirements.md) for user stories
2. Read [design.md](./design.md) for architecture
3. Follow [tasks.md](./tasks.md) for implementation
4. Start with Stage 1 (Foundation)

---

## Related Documentation

- [Backend Monitoring Module](../../../backend/app/modules/monitoring/README.md)
- [Backend API Docs](../../../backend/docs/api/monitoring.md)
- [Phase 1 Spec](../phase1-workbench-navigation/README.md)
- [Frontend Roadmap](../ROADMAP.md)
