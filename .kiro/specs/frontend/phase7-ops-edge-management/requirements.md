# Phase 7: Ops & Edge Management - Requirements

## Overview

**Phase**: 7
**Complexity**: ⭐⭐⭐ Medium (Option C: Hybrid Power)
**Dependencies**: Phase 1 (workbench) ✅
**Status**: Ready to implement

**Purpose**: Professional operations dashboard with smart monitoring, auto-refresh, and intelligent alerts for system health, worker status, and infrastructure metrics.

**Implementation Option**: **Option C: "Hybrid Power"** ⭐ RECOMMENDED
- **Style**: Professional ops dashboard with smart alerts
- **Components**: magic-mcp dashboard structure + shadcn-ui + magic-ui alerts
- **Interaction**: Auto-refresh, smart threshold-based alerts, anomaly detection
- **Pros**: Professional, informative, reliable, intelligent
- **Cons**: Requires robust monitoring backend (already implemented ✅)

---

## User Stories

### US-7.1: System Health Overview with Smart Alerts
**As a** DevOps engineer  
**I want to** see overall system health with intelligent alerts  
**So that** I can quickly identify and respond to issues

**Acceptance Criteria**:
- [ ] Dashboard shows overall health status (healthy/degraded/down)
- [ ] Color-coded status indicators (green/yellow/red)
- [ ] **Smart alerts** appear when thresholds are exceeded
- [ ] **Alert history** shows recent alerts with timestamps
- [ ] **Alert dismissal** with "acknowledge" action
- [ ] Last updated timestamp
- [ ] Quick refresh button
- [ ] Auto-refresh every 30 seconds with visual indicator

### US-7.2: Module Health Monitoring with Anomaly Detection
**As a** system administrator  
**I want to** see health status of each backend module with anomaly detection  
**So that** I can identify which module is causing issues before they escalate

**Acceptance Criteria**:
- [ ] List of all 13 backend modules with health status
- [ ] Each module shows: name, status, response time, error count
- [ ] **Anomaly detection** highlights unusual patterns (spike in errors, slow response)
- [ ] **Trend indicators** show if metrics are improving/degrading
- [ ] Click module to see detailed metrics
- [ ] Filter by status (all/healthy/degraded/down)
- [ ] Sort by name, status, or response time
- [ ] **Alert badge** on modules with active alerts

### US-7.3: Performance Metrics
**As a** performance engineer  
**I want to** view system performance metrics  
**So that** I can optimize resource usage

**Acceptance Criteria**:
- [ ] API response time chart (P50, P95, P99)
- [ ] Request rate (requests/second)
- [ ] Error rate percentage
- [ ] Database query performance
- [ ] Time range selector (1h, 6h, 24h, 7d)

### US-7.4: Database Monitoring
**As a** database administrator  
**I want to** monitor database health and connection pool  
**So that** I can prevent connection exhaustion

**Acceptance Criteria**:
- [ ] Connection pool status (active/idle/max)
- [ ] Query performance metrics
- [ ] Table sizes and row counts
- [ ] Slow query log (queries > 100ms)
- [ ] Connection pool utilization chart

### US-7.5: Event Bus Metrics
**As a** system architect  
**I want to** monitor event bus performance  
**So that** I can ensure event-driven communication is healthy

**Acceptance Criteria**:
- [ ] Events emitted/received counts
- [ ] Event latency (P95 < 1ms target)
- [ ] Event types breakdown
- [ ] Failed event deliveries
- [ ] Event history timeline (last 100 events)

### US-7.6: Cache Performance
**As a** performance engineer  
**I want to** monitor Redis cache performance  
**So that** I can optimize cache hit rates

**Acceptance Criteria**:
- [ ] Cache hit/miss ratio
- [ ] Cache size and memory usage
- [ ] Top cached keys
- [ ] Cache eviction rate
- [ ] Clear cache button (with confirmation)

### US-7.7: Worker Status
**As a** DevOps engineer  
**I want to** monitor Celery worker status  
**So that** I can ensure background tasks are processing

**Acceptance Criteria**:
- [ ] Active workers count
- [ ] Worker health status
- [ ] Task queue length
- [ ] Task processing rate
- [ ] Failed tasks count

### US-7.8: ML Model Health
**As a** ML engineer  
**I want to** monitor ML model health and performance  
**So that** I can ensure models are loaded and responding

**Acceptance Criteria**:
- [ ] Model loading status (embedding, summarizer, classifier)
- [ ] Model inference time
- [ ] Model memory usage
- [ ] Model error rate
- [ ] Last inference timestamp

### US-7.9: User Engagement Metrics
**As a** product manager  
**I want to** view user engagement metrics  
**So that** I can understand system usage patterns

**Acceptance Criteria**:
- [ ] Active users count
- [ ] Resources created/updated
- [ ] Searches performed
- [ ] Annotations created
- [ ] Collections created
- [ ] Time range selector

### US-7.10: Recommendation Quality
**As a** ML engineer  
**I want to** monitor recommendation quality metrics  
**So that** I can improve recommendation algorithms

**Acceptance Criteria**:
- [ ] Recommendation accuracy metrics
- [ ] Click-through rate
- [ ] User feedback scores
- [ ] Model performance comparison
- [ ] A/B test results (if applicable)

### US-7.11: Smart Alert System
**As a** DevOps engineer  
**I want to** receive intelligent alerts based on thresholds and patterns  
**So that** I can proactively respond to issues

**Acceptance Criteria**:
- [ ] Alert triggers: error rate > 5%, response time > 500ms, worker queue > 100
- [ ] Alert severity levels (info, warning, critical)
- [ ] Alert notifications with magic-ui animated alerts
- [ ] Alert history with timestamps and resolution status
- [ ] Acknowledge/dismiss alerts
- [ ] Alert sound toggle (optional)
- [ ] Alert preferences (which metrics to monitor)

### US-7.12: Ingestion Queue & Worker Management
**As a** DevOps engineer  
**I want to** monitor and manage repository ingestion  
**So that** I can ensure smooth content processing

**Acceptance Criteria**:
- [ ] Ingestion queue visualization (pending, processing, completed, failed)
- [ ] Manual repository ingestion trigger
- [ ] Job history with status and duration
- [ ] Worker heartbeat status (cloud API + edge GPU worker)
- [ ] Manual re-index button for failed jobs
- [ ] Job cancellation for stuck jobs
- [ ] Ingestion health check

### US-7.13: Sparse Embedding Generation
**As a** system administrator  
**I want to** trigger sparse embedding generation for search optimization  
**So that** I can improve search performance

**Acceptance Criteria**:
- [ ] Sparse embedding generation button
- [ ] Progress indicator during generation
- [ ] Success/failure notification
- [ ] Last generation timestamp
- [ ] Estimated time remaining

---

## Backend API Endpoints

All endpoints are in `backend/app/modules/monitoring/router.py` and `backend/app/routers/ingestion.py`

### System Health
| Endpoint | Method | Response Schema | Purpose |
|----------|--------|-----------------|---------|
| `/api/monitoring/health` | GET | `HealthCheckResponse` | Overall system health |
| `/api/monitoring/health/ml` | GET | `Dict[str, Any]` | ML model health |
| `/api/monitoring/model-health` | GET | `ModelHealthMetrics` | NCF model health |
| `/api/monitoring/health/module/{module_name}` | GET | `Dict[str, Any]` | **NEW** Module-specific health |

### Performance
| Endpoint | Method | Response Schema | Purpose |
|----------|--------|-----------------|---------|
| `/api/monitoring/performance` | GET | `PerformanceMetrics` | Performance summary |
| `/api/monitoring/recommendation-quality` | GET | `RecommendationQualityMetrics` | Recommendation metrics |
| `/api/monitoring/user-engagement` | GET | `UserEngagementMetrics` | User engagement |

### Infrastructure
| Endpoint | Method | Response Schema | Purpose |
|----------|--------|-----------------|---------|
| `/api/monitoring/database` | GET | `DatabaseMetrics` | Database metrics |
| `/api/monitoring/db/pool` | GET | `Dict[str, Any]` | Connection pool |
| `/api/monitoring/events` | GET | `EventBusMetrics` | Event bus metrics |
| `/api/monitoring/events/history` | GET | `List[Dict]` | Recent events |
| `/api/monitoring/cache/stats` | GET | `CacheStats` | Cache statistics |
| `/api/monitoring/workers/status` | GET | `WorkerStatus` | Worker status |

### Ingestion & Operations
| Endpoint | Method | Response Schema | Purpose |
|----------|--------|-----------------|---------|
| `/api/v1/ingestion/ingest/{repo_url:path}` | POST | `Dict[str, Any]` | **NEW** Ingest repository |
| `/api/v1/ingestion/worker/status` | GET | `Dict[str, Any]` | **NEW** Worker status |
| `/api/v1/ingestion/jobs/history` | GET | `List[Dict]` | **NEW** Job history |
| `/api/v1/ingestion/health` | GET | `Dict[str, Any]` | **NEW** Ingestion health |
| `/admin/sparse-embeddings/generate` | POST | `Dict[str, Any]` | **NEW** Generate sparse embeddings |

---

## Response Schemas

### HealthCheckResponse
```typescript
interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'down';
  timestamp: string;
  modules: {
    [moduleName: string]: {
      status: 'healthy' | 'degraded' | 'down';
      response_time_ms: number;
      error_count: number;
    };
  };
}
```

### PerformanceMetrics
```typescript
interface PerformanceMetrics {
  api_response_time: {
    p50: number;
    p95: number;
    p99: number;
  };
  request_rate: number; // requests/second
  error_rate: number; // percentage
  uptime_seconds: number;
}
```

### DatabaseMetrics
```typescript
interface DatabaseMetrics {
  connection_pool: {
    active: number;
    idle: number;
    max: number;
    utilization: number; // percentage
  };
  query_performance: {
    avg_query_time_ms: number;
    slow_queries: number; // > 100ms
  };
  table_stats: {
    [tableName: string]: {
      row_count: number;
      size_mb: number;
    };
  };
}
```

### EventBusMetrics
```typescript
interface EventBusMetrics {
  events_emitted: number;
  events_received: number;
  event_latency_ms: {
    p50: number;
    p95: number;
    p99: number;
  };
  event_types: {
    [eventType: string]: number;
  };
  failed_deliveries: number;
}
```

### CacheStats
```typescript
interface CacheStats {
  hit_rate: number; // percentage
  miss_rate: number; // percentage
  size_mb: number;
  eviction_rate: number;
  top_keys: Array<{
    key: string;
    hits: number;
    size_bytes: number;
  }>;
}
```

### WorkerStatus
```typescript
interface WorkerStatus {
  active_workers: number;
  worker_health: 'healthy' | 'degraded' | 'down';
  queue_length: number;
  processing_rate: number; // tasks/second
  failed_tasks: number;
}
```

### ModelHealthMetrics
```typescript
interface ModelHealthMetrics {
  models: {
    [modelName: string]: {
      loaded: boolean;
      inference_time_ms: number;
      memory_mb: number;
      error_rate: number;
      last_inference: string; // ISO timestamp
    };
  };
}
```

### UserEngagementMetrics
```typescript
interface UserEngagementMetrics {
  active_users: number;
  resources_created: number;
  resources_updated: number;
  searches_performed: number;
  annotations_created: number;
  collections_created: number;
  time_range: string; // e.g., "24h"
}
```

### RecommendationQualityMetrics
```typescript
interface RecommendationQualityMetrics {
  accuracy: number; // percentage
  click_through_rate: number; // percentage
  avg_user_rating: number; // 1-5
  model_performance: {
    [modelName: string]: {
      precision: number;
      recall: number;
      f1_score: number;
    };
  };
}
```

---

## UI Components Needed

### Pages
- `/ops` - Main ops dashboard

### Core Components
- `OpsLayout` - Dashboard layout with grid
- `HealthStatusCard` - Overall health indicator with smart alerts
- `ModuleHealthList` - List of module health statuses with anomaly detection
- `PerformanceChart` - Line chart for metrics over time
- `DatabaseMonitor` - Database metrics display
- `EventBusMonitor` - Event bus metrics display
- `CacheMonitor` - Cache performance display
- `WorkerMonitor` - Worker status display
- `ModelHealthMonitor` - ML model health display
- `EngagementMetrics` - User engagement display
- `RecommendationQuality` - Recommendation metrics display
- `MetricCard` - Reusable metric display card
- `StatusBadge` - Color-coded status indicator
- `RefreshButton` - Manual refresh trigger
- `TimeRangeSelector` - Time range picker

### NEW: Option C Components
- `SmartAlertPanel` - Intelligent alert system with magic-ui alerts
- `AlertHistoryDrawer` - Alert history with acknowledge/dismiss
- `AnomalyDetector` - Visual anomaly indicators on metrics
- `TrendIndicator` - Up/down/neutral trend arrows
- `IngestionQueueViz` - Queue visualization (pending/processing/completed/failed)
- `IngestionTrigger` - Manual ingestion form
- `JobHistoryTable` - Job history with status
- `WorkerHeartbeat` - Worker status with heartbeat animation
- `SparseEmbeddingGenerator` - Sparse embedding generation UI
- `AlertPreferences` - Alert threshold configuration

---

## Non-Functional Requirements

### Performance
- Dashboard loads in < 2 seconds
- Auto-refresh every 30 seconds without blocking UI
- Charts render smoothly (60fps)
- Handle 100+ metrics without lag
- **Smart alerts** trigger within 1 second of threshold breach

### Accessibility
- WCAG 2.1 AA compliant
- Keyboard navigation for all controls
- Screen reader support for metrics and alerts
- Color-blind friendly status indicators
- Alert sound with toggle option

### Responsiveness
- Desktop-first (1920x1080 primary)
- Tablet support (768px+)
- Mobile view (optional, read-only)

### Error Handling
- Graceful degradation if backend is down
- Show last known values with timestamp
- Retry failed requests with exponential backoff
- Clear error messages for users
- **Alert system** continues working even if some metrics fail

---

## Out of Scope

❌ **Email/SMS Alerts** - Browser notifications only
❌ **Historical Data Storage** - Use external monitoring (Prometheus/Grafana)
❌ **Log Viewer** - No log file browsing
❌ **Configuration UI** - No system configuration changes
❌ **User Management** - No user admin features
❌ **Deployment Controls** - No deploy/restart buttons (except re-index)
❌ **Cost Tracking** - No AWS billing integration
❌ **Custom Dashboards** - No user-customizable layouts
❌ **Advanced Anomaly Detection** - Simple threshold-based only

---

## Success Metrics

- [ ] All 13 backend modules visible with health status
- [ ] Dashboard loads in < 2 seconds
- [ ] Auto-refresh works without UI blocking
- [ ] All 13 user stories implemented (including 3 new ones)
- [ ] Smart alerts trigger correctly on threshold breach
- [ ] Ingestion queue visualization works
- [ ] Manual ingestion trigger works
- [ ] Sparse embedding generation works
- [ ] Zero accessibility violations
- [ ] Works on Chrome, Firefox, Safari

---

## Dependencies

### Phase 1 (Complete ✅)
- Workbench layout
- Sidebar navigation
- Theme system

### Backend (Complete ✅)
- Monitoring module with 12 endpoints
- All metrics collection implemented
- Event bus metrics aggregation
- Ingestion API with worker status
- Sparse embedding generation endpoint

### External Libraries
- Recharts (for charts)
- shadcn-ui (Card, Badge, Button, Select, Alert, Dialog)
- magic-ui (animated alerts, orbiting circles for heartbeat)
- TanStack Query (data fetching)
- date-fns (time formatting)

---

## Related Documentation

- [Backend Monitoring Module](../../../backend/app/modules/monitoring/README.md)
- [Backend API Docs](../../../backend/docs/api/monitoring.md)
- [Backend Ingestion API](../../../backend/docs/api/ingestion.md)
- [Phase 1 Spec](../phase1-workbench-navigation/requirements.md)
- [Frontend Roadmap](../ROADMAP.md)
