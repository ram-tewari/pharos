# Phase 7: Ops & Edge Management - Quick Summary (Option C: Hybrid Power)

## ✅ Spec Complete

**Created**: 2026-01-29  
**Updated**: 2026-01-29 (Option C)
**Status**: Ready for implementation  
**Estimated Time**: 16-20 hours  
**Complexity**: ⭐⭐⭐ Medium (Option C)

**Implementation**: Option C - "Hybrid Power" ⭐ RECOMMENDED
- Professional ops dashboard with smart monitoring
- magic-mcp dashboard structure + shadcn-ui + magic-ui
- Intelligent threshold-based alerting
- Anomaly detection on key metrics
- Auto-refresh with visual indicators

---

## What You Get

A comprehensive system monitoring dashboard that displays:

- **System Health**: Overall status + 13 module health cards with anomaly detection
- **Performance**: API response time charts (P50/P95/P99) with trend indicators
- **Database**: Connection pool, query performance, table stats
- **Event Bus**: Event metrics, latency, history timeline
- **Cache**: Hit/miss rates, top keys, clear cache action
- **Workers**: Celery worker status, queue length, failed tasks
- **ML Models**: Model health, inference time, memory usage
- **Engagement**: User activity metrics
- **Recommendations**: Quality metrics and model performance
- **Smart Alerts**: Threshold-based alerts with magic-ui animations ⭐ NEW
- **Anomaly Detection**: Automatic detection of unusual patterns ⭐ NEW
- **Ingestion Queue**: Repository ingestion visualization ⭐ NEW
- **Worker Heartbeat**: Real-time worker status with orbiting circles ⭐ NEW
- **Sparse Embeddings**: Manual sparse embedding generation ⭐ NEW

---

## Key Features

✅ Auto-refresh every 30 seconds  
✅ Manual refresh button  
✅ Time range selector (1h, 6h, 24h, 7d)  
✅ Module health filtering (all/healthy/degraded/down)  
✅ Real-time charts with Recharts  
✅ Color-coded status indicators  
✅ Responsive design (desktop/tablet/mobile)  
✅ Accessibility compliant (WCAG AA)
✅ **Smart alert system with magic-ui animations** ⭐ NEW
✅ **Anomaly detection on key metrics** ⭐ NEW
✅ **Alert history and preferences** ⭐ NEW
✅ **Ingestion queue visualization** ⭐ NEW
✅ **Worker heartbeat with orbiting circles** ⭐ NEW
✅ **Sparse embedding generation UI** ⭐ NEW

---

## Backend Integration

**17 Endpoints** (12 monitoring + 5 ingestion):
- Health checks (system, modules, ML models)
- Performance metrics
- Infrastructure metrics (DB, events, cache, workers)
- User engagement and recommendation quality
- **Ingestion API** (ingest, worker status, job history) ⭐ NEW
- **Sparse embedding generation** ⭐ NEW

**Backend Module**: `backend/app/modules/monitoring/` + `backend/app/routers/ingestion.py`
**API Docs**: `backend/docs/api/monitoring.md` + `backend/docs/api/ingestion.md`

---

## Implementation Plan

### Stage 1: Foundation (2-3h)
- Types, API client, Zustand store
- Base layout and reusable components

### Stage 2: Health Monitoring (2-3h)
- Health overview section
- Module health grid with filters
- ML model health cards

### Stage 3: Performance Metrics (2-3h)
- Performance charts
- User engagement metrics
- Recommendation quality display

### Stage 4: Infrastructure (3-4h)
- Database monitor
- Event bus monitor
- Cache monitor
- Worker monitor

### Stage 5: Polish (2-3h)
- Auto-refresh implementation
- Error handling
- Responsive design
- Accessibility

### Stage 6: Documentation (1h)
- JSDoc comments
- README
- Tests

### Stage 7: Option C Features (4-5h) ⭐ NEW
- Smart alert system
- Anomaly detection
- Ingestion queue & worker management
- Sparse embedding generation

---

## Tech Stack

- **React 18** + TypeScript
- **TanStack Router** (routing)
- **Zustand** (state management)
- **TanStack Query** (data fetching)
- **Recharts** (charts)
- **shadcn-ui** (UI components)
- **magic-ui** (animated alerts, orbiting circles) ⭐ NEW
- **Tailwind CSS** (styling)

---

## File Count

**Total Files**: ~55 components + types + hooks (increased for Option C)

**Key Files**:
- 1 page (`src/pages/ops/index.tsx`)
- 42+ components (`src/components/ops/`) - 12 NEW for Option C
- 1 store (`src/stores/opsStore.ts`)
- 1 alert store (`src/stores/alertStore.ts`) ⭐ NEW
- 1 API client (`src/lib/api/monitoring.ts`)
- 1 ingestion API client (`src/lib/api/ingestion.ts`) ⭐ NEW
- 4 hooks (`src/lib/hooks/useMonitoring.ts`, `useAutoRefresh.ts`, `useAlerts.ts`, `useIngestion.ts`) - 2 NEW
- 1 types file (`src/types/monitoring.ts`)
- 1 utility (`src/lib/utils/anomalyDetection.ts`) ⭐ NEW

---

## Dependencies to Install

```bash
npm install recharts date-fns
npm install @magic-ui/react  # For animated alerts and orbiting circles
```

---

## Success Criteria

- [ ] Dashboard loads in < 2 seconds
- [ ] Auto-refresh works every 30 seconds
- [ ] All 13 backend modules visible
- [ ] All charts render smoothly (60fps)
- [ ] **Smart alerts trigger within 1 second of threshold breach** ⭐ NEW
- [ ] **Anomaly detection works on key metrics** ⭐ NEW
- [ ] **Ingestion queue visualization works** ⭐ NEW
- [ ] **Worker heartbeat shows real-time status** ⭐ NEW
- [ ] **Sparse embedding generation completes successfully** ⭐ NEW
- [ ] Zero accessibility violations
- [ ] Works on Chrome, Firefox, Safari
- [ ] 80%+ test coverage

---

## Next Steps

1. **Read the spec**: Start with `requirements.md` → `design.md` → `tasks.md`
2. **Set up environment**: Install dependencies
3. **Start Stage 1**: Create types, API client, and base layout
4. **Iterate through stages**: Follow tasks.md sequentially
5. **Test continuously**: Test each component as you build
6. **Deploy**: Integrate with Phase 1 workbench

---

## Parallel Work

This phase can be built **in parallel** with:
- Phase 5: Implementation Planner (other worker)
- Phase 9: Content Curation
- Phase 10: Taxonomy Management
- Phase 11: Social Authentication

**No dependencies** on other phases (except Phase 1 which is complete ✅)

---

## Questions?

- Check `requirements.md` for user stories
- Check `design.md` for architecture details
- Check `tasks.md` for step-by-step implementation
- Check backend docs: `backend/docs/api/monitoring.md`

---

**Ready to build!** 🚀
