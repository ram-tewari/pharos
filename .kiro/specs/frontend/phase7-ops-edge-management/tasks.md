# Phase 7: Ops & Edge Management - Tasks (Option C: Hybrid Power)

## Overview

**Total Estimated Time**: 16-20 hours (increased for Option C features)
**Complexity**: ⭐⭐⭐ Medium
**Team Size**: 1 developer

**Option C Features**:
- Smart alert system with magic-ui animations
- Anomaly detection on key metrics
- Ingestion queue visualization
- Worker heartbeat with orbiting circles
- Sparse embedding generation UI
- Alert history and preferences

---

## Task Breakdown

### Stage 1: Foundation (2-3 hours)

#### Task 1.1: Setup Types & API Client
**Time**: 1 hour

- [ ] Create `src/types/monitoring.ts` with all response schemas
- [ ] Create `src/lib/api/monitoring.ts` with API client
- [ ] Add TanStack Query hooks in `src/lib/hooks/useMonitoring.ts`
- [ ] Test API integration with backend

**Files to Create**:
```
src/types/monitoring.ts
src/lib/api/monitoring.ts
src/lib/hooks/useMonitoring.ts
```

**Acceptance Criteria**:
- All TypeScript types match backend schemas
- API client successfully fetches from `/api/monitoring/*`
- TanStack Query hooks return typed data

---

#### Task 1.2: Create Zustand Store
**Time**: 30 minutes

- [ ] Create `src/stores/opsStore.ts`
- [ ] Implement state management for UI controls
- [ ] Add auto-refresh toggle
- [ ] Add time range selector state
- [ ] Add module filter state

**Files to Create**:
```
src/stores/opsStore.ts
```

**Acceptance Criteria**:
- Store persists UI state
- Auto-refresh toggle works
- Time range changes trigger data refetch

---

#### Task 1.3: Create Base Layout
**Time**: 1 hour

- [ ] Create `src/pages/ops/index.tsx`
- [ ] Create `src/components/ops/OpsLayout.tsx`
- [ ] Create `src/components/ops/PageHeader.tsx`
- [ ] Add route to router configuration
- [ ] Add "Ops" link to sidebar navigation

**Files to Create**:
```
src/pages/ops/index.tsx
src/components/ops/OpsLayout.tsx
src/components/ops/PageHeader.tsx
```

**Acceptance Criteria**:
- `/ops` route renders page
- Page header shows title and controls
- Layout uses responsive grid

---

#### Task 1.4: Create Reusable Components
**Time**: 30 minutes

- [ ] Create `src/components/ops/MetricCard.tsx`
- [ ] Create `src/components/ops/StatusBadge.tsx`
- [ ] Create `src/components/ops/SectionHeader.tsx`
- [ ] Add Storybook stories (optional)

**Files to Create**:
```
src/components/ops/MetricCard.tsx
src/components/ops/StatusBadge.tsx
src/components/ops/SectionHeader.tsx
```

**Acceptance Criteria**:
- Components are reusable and typed
- Status badge shows correct colors
- Metric card displays value with unit

---

### Stage 2: Health Monitoring (2-3 hours)

#### Task 2.1: Health Overview Section
**Time**: 1 hour

- [ ] Create `src/components/ops/HealthOverviewSection.tsx`
- [ ] Create `src/components/ops/HealthStatusCard.tsx`
- [ ] Create `src/components/ops/QuickStatsGrid.tsx`
- [ ] Integrate with `useHealthCheck()` hook
- [ ] Add auto-refresh every 30 seconds

**Files to Create**:
```
src/components/ops/HealthOverviewSection.tsx
src/components/ops/HealthStatusCard.tsx
src/components/ops/QuickStatsGrid.tsx
```

**Acceptance Criteria**:
- Overall health status displays correctly
- Color-coded status indicator (green/yellow/red)
- Quick stats show API metrics
- Auto-refresh works without blocking UI

---

#### Task 2.2: Module Health Grid
**Time**: 1.5 hours

- [ ] Create `src/components/ops/ModuleHealthSection.tsx`
- [ ] Create `src/components/ops/ModuleHealthGrid.tsx`
- [ ] Create `src/components/ops/ModuleHealthCard.tsx`
- [ ] Create `src/components/ops/ModuleHealthFilters.tsx`
- [ ] Implement filter by status (all/healthy/degraded/down)
- [ ] Implement sort by name/status/response time

**Files to Create**:
```
src/components/ops/ModuleHealthSection.tsx
src/components/ops/ModuleHealthGrid.tsx
src/components/ops/ModuleHealthCard.tsx
src/components/ops/ModuleHealthFilters.tsx
```

**Acceptance Criteria**:
- All 13 modules display in grid
- Each card shows status, response time, error count
- Filter works correctly
- Sort works correctly

---

#### Task 2.3: ML Model Health
**Time**: 30 minutes

- [ ] Create `src/components/ops/MLSection.tsx`
- [ ] Create `src/components/ops/ModelHealthMonitor.tsx`
- [ ] Create `src/components/ops/ModelHealthCard.tsx`
- [ ] Integrate with `useMLModelHealth()` hook

**Files to Create**:
```
src/components/ops/MLSection.tsx
src/components/ops/ModelHealthMonitor.tsx
src/components/ops/ModelHealthCard.tsx
```

**Acceptance Criteria**:
- Shows embedding, summarizer, classifier models
- Displays load status, inference time, memory usage
- Updates on refresh

---

### Stage 3: Performance Metrics (2-3 hours)

#### Task 3.1: Performance Chart
**Time**: 1.5 hours

- [ ] Install Recharts: `npm install recharts`
- [ ] Create `src/components/ops/PerformanceSection.tsx`
- [ ] Create `src/components/ops/PerformanceChart.tsx`
- [ ] Implement line chart for P50/P95/P99 response times
- [ ] Add time range selector integration
- [ ] Add chart legend and tooltips

**Files to Create**:
```
src/components/ops/PerformanceSection.tsx
src/components/ops/PerformanceChart.tsx
```

**Acceptance Criteria**:
- Chart displays 3 lines (P50, P95, P99)
- Time range selector changes data
- Chart is responsive
- Tooltips show exact values

---

#### Task 3.2: User Engagement Metrics
**Time**: 1 hour

- [ ] Create `src/components/ops/EngagementSection.tsx`
- [ ] Create `src/components/ops/EngagementMetrics.tsx`
- [ ] Display 6 engagement metrics in grid
- [ ] Integrate with `useUserEngagement()` hook
- [ ] Add time range selector

**Files to Create**:
```
src/components/ops/EngagementSection.tsx
src/components/ops/EngagementMetrics.tsx
```

**Acceptance Criteria**:
- Shows active users, resources, searches, annotations, collections
- Time range selector works
- Metrics update on refresh

---

#### Task 3.3: Recommendation Quality
**Time**: 30 minutes

- [ ] Create `src/components/ops/RecommendationQuality.tsx`
- [ ] Create `src/components/ops/QualityMetricsGrid.tsx`
- [ ] Display accuracy, CTR, user rating
- [ ] Integrate with `useRecommendationQuality()` hook

**Files to Create**:
```
src/components/ops/RecommendationQuality.tsx
src/components/ops/QualityMetricsGrid.tsx
```

**Acceptance Criteria**:
- Shows recommendation quality metrics
- Displays model performance comparison
- Updates on refresh

---

### Stage 4: Infrastructure Monitoring (3-4 hours)

#### Task 4.1: Database Monitor
**Time**: 1.5 hours

- [ ] Create `src/components/ops/InfrastructureSection.tsx`
- [ ] Create `src/components/ops/DatabaseMonitor.tsx`
- [ ] Create `src/components/ops/ConnectionPoolChart.tsx`
- [ ] Create `src/components/ops/QueryPerformanceTable.tsx`
- [ ] Create `src/components/ops/TableStatsTable.tsx`
- [ ] Integrate with `useDatabaseMetrics()` hook

**Files to Create**:
```
src/components/ops/InfrastructureSection.tsx
src/components/ops/DatabaseMonitor.tsx
src/components/ops/ConnectionPoolChart.tsx
src/components/ops/QueryPerformanceTable.tsx
src/components/ops/TableStatsTable.tsx
```

**Acceptance Criteria**:
- Connection pool shows active/idle/max
- Query performance shows avg time and slow queries
- Table stats show row count and size

---

#### Task 4.2: Event Bus Monitor
**Time**: 1 hour

- [ ] Create `src/components/ops/EventBusMonitor.tsx`
- [ ] Create `src/components/ops/EventMetricsGrid.tsx`
- [ ] Create `src/components/ops/EventTypesChart.tsx`
- [ ] Create `src/components/ops/EventHistoryTimeline.tsx`
- [ ] Integrate with `useEventBusMetrics()` and `useEventHistory()` hooks

**Files to Create**:
```
src/components/ops/EventBusMonitor.tsx
src/components/ops/EventMetricsGrid.tsx
src/components/ops/EventTypesChart.tsx
src/components/ops/EventHistoryTimeline.tsx
```

**Acceptance Criteria**:
- Shows events emitted/received
- Displays event latency (P95 < 1ms)
- Event types pie chart
- Event history timeline (last 100 events)

---

#### Task 4.3: Cache Monitor
**Time**: 1 hour

- [ ] Create `src/components/ops/CacheMonitor.tsx`
- [ ] Create `src/components/ops/CacheHitRateChart.tsx`
- [ ] Create `src/components/ops/TopKeysTable.tsx`
- [ ] Create `src/components/ops/ClearCacheButton.tsx`
- [ ] Integrate with `useCacheStats()` hook
- [ ] Add confirmation dialog for cache clear

**Files to Create**:
```
src/components/ops/CacheMonitor.tsx
src/components/ops/CacheHitRateChart.tsx
src/components/ops/TopKeysTable.tsx
src/components/ops/ClearCacheButton.tsx
```

**Acceptance Criteria**:
- Hit/miss rate donut chart
- Top keys table with hit count and size
- Clear cache button with confirmation
- Cache clears successfully

---

#### Task 4.4: Worker Monitor
**Time**: 30 minutes

- [ ] Create `src/components/ops/WorkersSection.tsx`
- [ ] Create `src/components/ops/WorkerMonitor.tsx`
- [ ] Create `src/components/ops/WorkerStatusCard.tsx`
- [ ] Create `src/components/ops/QueueLengthChart.tsx`
- [ ] Integrate with `useWorkerStatus()` hook

**Files to Create**:
```
src/components/ops/WorkersSection.tsx
src/components/ops/WorkerMonitor.tsx
src/components/ops/WorkerStatusCard.tsx
src/components/ops/QueueLengthChart.tsx
```

**Acceptance Criteria**:
- Shows active workers count
- Displays queue length and processing rate
- Shows failed tasks count

---

### Stage 5: Polish & Testing (2-3 hours)

#### Task 5.1: Auto-Refresh Implementation
**Time**: 1 hour

- [x] Create `src/lib/hooks/useAutoRefresh.ts`
- [x] Implement auto-refresh toggle in PageHeader
- [x] Add refresh button for manual refresh
- [x] Add last updated timestamp
- [x] Ensure auto-refresh doesn't block UI

**Files to Create**:
```
src/lib/hooks/useAutoRefresh.ts
```

**Acceptance Criteria**:
- Auto-refresh toggles on/off
- Refreshes every 30 seconds when enabled
- Manual refresh button works
- Last updated timestamp displays correctly

---

#### Task 5.2: Error Handling
**Time**: 1 hour

- [x] Add error boundaries to all sections
- [x] Implement retry logic for failed requests
- [x] Show "Stale Data" warning when backend is down
- [x] Add loading skeletons for all components
- [x] Handle partial data failures gracefully

**Acceptance Criteria**:
- Errors display user-friendly messages
- Retry button works
- Loading states show skeletons
- Partial failures don't crash entire page

---

#### Task 5.3: Responsive Design
**Time**: 30 minutes

- [x] Test on desktop (1920x1080)
- [x] Test on tablet (768px)
- [x] Test on mobile (375px)
- [x] Adjust grid columns for breakpoints
- [x] Ensure charts are responsive

**Acceptance Criteria**:
- Desktop: 3-4 column grid
- Tablet: 2 column grid
- Mobile: 1 column grid
- Charts resize correctly

---

#### Task 5.4: Accessibility
**Time**: 30 minutes

- [x] Add ARIA labels to all metrics
- [x] Add ARIA live regions for auto-updating data
- [x] Test keyboard navigation
- [x] Test screen reader support
- [x] Ensure color contrast meets WCAG AA

**Acceptance Criteria**:
- All interactive elements keyboard accessible
- Screen reader announces updates
- Color contrast passes WCAG AA
- No accessibility violations in axe DevTools

---

#### Task 5.5: Unit Testing
**Time**: 1 hour

- [x] Write unit tests for opsStore
- [x] Test time range management
- [x] Test auto-refresh toggle
- [x] Test module filter
- [x] Test state persistence
- [x] Achieve 100% test coverage for store

**Files Created**:
```
src/stores/__tests__/opsStore.test.ts
```

**Acceptance Criteria**:
- All store actions tested
- 10+ unit tests passing
- 100% code coverage for store
- Tests run in <100ms

---

### Stage 6: Documentation & Deployment (1 hour)

#### Task 6.1: Documentation
**Time**: 30 minutes

- [ ] Add JSDoc comments to all components
- [ ] Create README.md in `src/pages/ops/`
- [ ] Document API integration
- [ ] Add usage examples

**Files to Create**:
```
src/pages/ops/README.md
```

**Acceptance Criteria**:
- All components have JSDoc comments
- README explains feature and usage
- API integration documented

---

#### Task 6.2: Testing
**Time**: 30 minutes

- [ ] Write unit tests for key components
- [ ] Write integration tests for API hooks
- [ ] Test auto-refresh behavior
- [ ] Test error handling
- [ ] Test filter/sort functionality

**Acceptance Criteria**:
- 80%+ code coverage
- All critical paths tested
- Tests pass in CI/CD

---

## File Structure

```
src/
├── pages/
│   └── ops/
│       ├── index.tsx
│       └── README.md
├── components/
│   └── ops/
│       ├── OpsLayout.tsx
│       ├── PageHeader.tsx
│       ├── MetricCard.tsx
│       ├── StatusBadge.tsx
│       ├── SectionHeader.tsx
│       ├── HealthOverviewSection.tsx
│       ├── HealthStatusCard.tsx
│       ├── QuickStatsGrid.tsx
│       ├── ModuleHealthSection.tsx
│       ├── ModuleHealthGrid.tsx
│       ├── ModuleHealthCard.tsx
│       ├── ModuleHealthFilters.tsx
│       ├── PerformanceSection.tsx
│       ├── PerformanceChart.tsx
│       ├── InfrastructureSection.tsx
│       ├── DatabaseMonitor.tsx
│       ├── ConnectionPoolChart.tsx
│       ├── QueryPerformanceTable.tsx
│       ├── TableStatsTable.tsx
│       ├── EventBusMonitor.tsx
│       ├── EventMetricsGrid.tsx
│       ├── EventTypesChart.tsx
│       ├── EventHistoryTimeline.tsx
│       ├── CacheMonitor.tsx
│       ├── CacheHitRateChart.tsx
│       ├── TopKeysTable.tsx
│       ├── ClearCacheButton.tsx
│       ├── WorkersSection.tsx
│       ├── WorkerMonitor.tsx
│       ├── WorkerStatusCard.tsx
│       ├── QueueLengthChart.tsx
│       ├── MLSection.tsx
│       ├── ModelHealthMonitor.tsx
│       ├── ModelHealthCard.tsx
│       ├── EngagementSection.tsx
│       ├── EngagementMetrics.tsx
│       ├── RecommendationQuality.tsx
│       └── QualityMetricsGrid.tsx
├── lib/
│   ├── api/
│   │   └── monitoring.ts
│   └── hooks/
│       ├── useMonitoring.ts
│       └── useAutoRefresh.ts
├── stores/
│   └── opsStore.ts
└── types/
    └── monitoring.ts
```

---

## Dependencies to Install

```bash
npm install recharts
npm install date-fns
```

---

## Testing Checklist

- [ ] All API endpoints return data
- [ ] Auto-refresh works without blocking UI
- [ ] Manual refresh button works
- [ ] Time range selector changes data
- [ ] Module filter works correctly
- [ ] Module sort works correctly
- [ ] Charts render correctly
- [ ] Cache clear button works with confirmation
- [ ] Error handling shows user-friendly messages
- [ ] Loading states show skeletons
- [ ] Responsive design works on all breakpoints
- [ ] Keyboard navigation works
- [ ] Screen reader support works
- [ ] Color contrast meets WCAG AA
- [ ] No console errors or warnings

---

## Success Criteria

- [ ] All 10 user stories implemented
- [ ] Dashboard loads in < 2 seconds
- [ ] Auto-refresh works every 30 seconds
- [ ] All 13 backend modules visible
- [ ] All charts render smoothly (60fps)
- [ ] Zero accessibility violations
- [ ] Works on Chrome, Firefox, Safari
- [ ] 80%+ test coverage

---

## Related Documentation

- [Requirements](./requirements.md)
- [Design](./design.md)
- [Backend Monitoring API](../../../backend/docs/api/monitoring.md)
- [Frontend Roadmap](../ROADMAP.md)


---

## Stage 7: Option C Features (4-5 hours) ⭐ NEW

### Task 7.1: Smart Alert System
**Time**: 2 hours

- [ ] Create `src/components/ops/SmartAlertPanel.tsx`
- [ ] Create `src/components/ops/AlertHistoryDrawer.tsx`
- [ ] Create `src/components/ops/AlertPreferencesDrawer.tsx`
- [ ] Implement alert threshold logic
- [ ] Integrate magic-ui animated alerts
- [ ] Add alert sound with toggle
- [ ] Implement alert acknowledgment
- [ ] Add alert history storage (localStorage)

**Files to Create**:
```
src/components/ops/SmartAlertPanel.tsx
src/components/ops/AlertHistoryDrawer.tsx
src/components/ops/AlertPreferencesDrawer.tsx
src/lib/hooks/useAlerts.ts
src/stores/alertStore.ts
```

**Acceptance Criteria**:
- Alerts trigger when thresholds exceeded
- magic-ui animations work smoothly
- Alert history persists across sessions
- Alert preferences save correctly
- Sound notification works with toggle

---

### Task 7.2: Anomaly Detection
**Time**: 1 hour

- [ ] Create `src/components/ops/AnomalyDetector.tsx`
- [ ] Create `src/components/ops/TrendIndicator.tsx`
- [ ] Implement simple anomaly detection algorithm
- [ ] Add anomaly indicators to MetricCard
- [ ] Add trend arrows to module health cards
- [ ] Test anomaly detection with mock data

**Files to Create**:
```
src/components/ops/AnomalyDetector.tsx
src/components/ops/TrendIndicator.tsx
src/lib/utils/anomalyDetection.ts
```

**Acceptance Criteria**:
- Anomaly detection identifies spikes/drops
- Trend indicators show correct direction
- Visual indicators appear on metrics
- Tooltips explain anomalies

---

### Task 7.3: Ingestion Queue & Worker Management
**Time**: 1.5 hours

- [ ] Create `src/components/ops/IngestionSection.tsx`
- [ ] Create `src/components/ops/IngestionQueueViz.tsx`
- [ ] Create `src/components/ops/IngestionTrigger.tsx`
- [ ] Create `src/components/ops/JobHistoryTable.tsx`
- [ ] Create `src/components/ops/WorkerHeartbeat.tsx`
- [ ] Integrate ingestion API endpoints
- [ ] Implement magic-ui orbiting circles for heartbeat
- [ ] Add manual ingestion trigger
- [ ] Add job retry/cancel actions

**Files to Create**:
```
src/components/ops/IngestionSection.tsx
src/components/ops/IngestionQueueViz.tsx
src/components/ops/IngestionTrigger.tsx
src/components/ops/JobHistoryTable.tsx
src/components/ops/WorkerHeartbeat.tsx
src/lib/api/ingestion.ts
src/lib/hooks/useIngestion.ts
```

**Acceptance Criteria**:
- Queue visualization shows correct counts
- Manual ingestion trigger works
- Job history displays correctly
- Worker heartbeat animates when online
- Retry/cancel actions work

---

### Task 7.4: Sparse Embedding Generation
**Time**: 30 minutes

- [ ] Create `src/components/ops/OperationsSection.tsx`
- [ ] Create `src/components/ops/SparseEmbeddingGenerator.tsx`
- [ ] Integrate sparse embedding API endpoint
- [ ] Add progress indicator
- [ ] Add success/error notifications
- [ ] Display last generated timestamp

**Files to Create**:
```
src/components/ops/OperationsSection.tsx
src/components/ops/SparseEmbeddingGenerator.tsx
```

**Acceptance Criteria**:
- Generate button triggers API call
- Progress indicator shows during generation
- Success/error notifications display
- Last generated timestamp updates

---

## Option C Additional Files

**NEW Components** (10 files):
- SmartAlertPanel.tsx
- AlertHistoryDrawer.tsx
- AlertPreferencesDrawer.tsx
- AnomalyDetector.tsx
- TrendIndicator.tsx
- IngestionSection.tsx
- IngestionQueueViz.tsx
- IngestionTrigger.tsx
- JobHistoryTable.tsx
- WorkerHeartbeat.tsx
- OperationsSection.tsx
- SparseEmbeddingGenerator.tsx

**NEW Utilities** (3 files):
- useAlerts.ts
- useIngestion.ts
- anomalyDetection.ts

**NEW Stores** (1 file):
- alertStore.ts

**NEW API Clients** (1 file):
- ingestion.ts

**Total NEW Files**: 15

---

## Updated Dependencies

```bash
npm install recharts date-fns
npm install @magic-ui/react  # For animated alerts and orbiting circles
```

---

## Updated Testing Checklist

**Option C Specific Tests**:
- [ ] Smart alerts trigger correctly
- [ ] Alert acknowledgment works
- [ ] Alert history persists
- [ ] Anomaly detection identifies patterns
- [ ] Trend indicators show correct direction
- [ ] Ingestion trigger works
- [ ] Job history displays correctly
- [ ] Worker heartbeat animates
- [ ] Sparse embedding generation works

---

## Updated Success Criteria

- [ ] All 13 user stories implemented (including 3 new ones)
- [ ] **Smart alerts trigger within 1 second of threshold breach**
- [ ] **Anomaly detection works on key metrics**
- [ ] **Ingestion queue visualization works**
- [ ] **Worker heartbeat shows real-time status**
- [ ] **Sparse embedding generation completes successfully**
- [ ] Dashboard loads in < 2 seconds
- [ ] Auto-refresh works every 30 seconds
- [ ] All 13 backend modules visible
- [ ] All charts render smoothly (60fps)
- [ ] Zero accessibility violations
- [ ] Works on Chrome, Firefox, Safari
- [ ] 80%+ test coverage
