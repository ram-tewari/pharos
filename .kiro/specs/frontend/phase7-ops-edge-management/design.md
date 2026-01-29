# Phase 7: Ops & Edge Management - Design (Option C: Hybrid Power)

## Architecture Overview

**Implementation**: Option C - "Hybrid Power" ⭐ RECOMMENDED
- Professional ops dashboard with smart monitoring
- magic-mcp dashboard structure for layout
- shadcn-ui for core components
- magic-ui for animated alerts and visual effects
- Intelligent threshold-based alerting
- Auto-refresh with visual indicators
- Anomaly detection on key metrics

```
┌─────────────────────────────────────────────────────────────┐
│                  Ops Dashboard (/ops)                       │
│                  [Option C: Hybrid Power]                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┤
│  │ Smart Alert Panel (magic-ui alerts)                    │
│  │ [!] High error rate in Search module (5.2%)            │
│  │ [!] Worker queue length exceeds threshold (127)        │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │ Health Overview │  │ Performance     │  │ Quick      │ │
│  │ Card + Alerts   │  │ Chart + Trends  │  │ Actions    │ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┤
│  │ Module Health Grid (13 modules) + Anomaly Detection    │
│  ├─────────────────────────────────────────────────────────┤
│  │ [Resources ↑] [Search ⚠️] [Collections ✓] ...          │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Database     │  │ Event Bus    │  │ Cache        │    │
│  │ Monitor      │  │ Monitor      │  │ Monitor      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Ingestion    │  │ Worker       │  │ ML Models    │    │
│  │ Queue Viz    │  │ Heartbeat    │  │ Health       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
OpsPage
├── OpsLayout
│   ├── PageHeader
│   │   ├── Title ("System Operations")
│   │   ├── RefreshButton (with auto-refresh indicator)
│   │   ├── TimeRangeSelector
│   │   └── AlertPreferencesButton
│   │
│   ├── SmartAlertPanel (NEW - Option C)
│   │   ├── ActiveAlerts (magic-ui animated alerts)
│   │   ├── AlertHistoryButton
│   │   └── AlertPreferencesDrawer
│   │
│   ├── HealthOverviewSection
│   │   ├── HealthStatusCard (overall + alert badge)
│   │   └── QuickStatsGrid
│   │       ├── MetricCard (API Response Time + trend)
│   │       ├── MetricCard (Request Rate + trend)
│   │       ├── MetricCard (Error Rate + anomaly indicator)
│   │       └── MetricCard (Uptime)
│   │
│   ├── ModuleHealthSection
│   │   ├── SectionHeader
│   │   ├── ModuleHealthGrid
│   │   │   └── ModuleHealthCard (x13) (NEW - with anomaly detection)
│   │   │       ├── StatusBadge
│   │   │       ├── ModuleName
│   │   │       ├── ResponseTime + TrendIndicator
│   │   │       ├── ErrorCount + AnomalyIndicator
│   │   │       └── AlertBadge (if active alert)
│   │   └── ModuleHealthFilters
│   │
│   ├── PerformanceSection
│   │   ├── SectionHeader
│   │   └── PerformanceChart (with anomaly markers)
│   │       └── LineChart (Recharts)
│   │
│   ├── IngestionSection (NEW - Option C)
│   │   ├── IngestionQueueViz
│   │   │   ├── QueueStatusChart (pending/processing/completed/failed)
│   │   │   └── QueueMetrics
│   │   ├── IngestionTrigger
│   │   │   ├── RepoUrlInput
│   │   │   └── IngestButton
│   │   ├── JobHistoryTable
│   │   │   └── JobRow (status, duration, actions)
│   │   └── WorkerHeartbeat (magic-ui orbiting circles)
│   │
│   ├── InfrastructureSection
│   │   ├── DatabaseMonitor
│   │   │   ├── ConnectionPoolChart
│   │   │   ├── QueryPerformanceTable
│   │   │   └── TableStatsTable
│   │   │
│   │   ├── EventBusMonitor
│   │   │   ├── EventMetricsGrid
│   │   │   ├── EventTypesChart
│   │   │   └── EventHistoryTimeline
│   │   │
│   │   └── CacheMonitor
│   │       ├── CacheHitRateChart
│   │       ├── TopKeysTable
│   │       └── ClearCacheButton
│   │
│   ├── WorkersSection
│   │   └── WorkerMonitor
│   │       ├── WorkerStatusCard
│   │       ├── QueueLengthChart (with alert threshold line)
│   │       └── FailedTasksList
│   │
│   ├── MLSection
│   │   └── ModelHealthMonitor
│   │       └── ModelHealthGrid
│   │           └── ModelHealthCard (x3)
│   │               ├── ModelName
│   │               ├── LoadStatus
│   │               ├── InferenceTime + TrendIndicator
│   │               └── MemoryUsage
│   │
│   ├── EngagementSection
│   │   ├── EngagementMetrics
│   │   │   └── MetricCard (x6)
│   │   └── RecommendationQuality
│   │       └── QualityMetricsGrid
│   │
│   └── OperationsSection (NEW - Option C)
│       └── SparseEmbeddingGenerator
│           ├── GenerateButton
│           ├── ProgressIndicator
│           └── LastGeneratedTimestamp
```

---

## State Management

### Zustand Store: `useOpsStore`

```typescript
interface OpsStore {
  // Data
  healthData: HealthCheckResponse | null;
  performanceData: PerformanceMetrics | null;
  databaseData: DatabaseMetrics | null;
  eventBusData: EventBusMetrics | null;
  cacheData: CacheStats | null;
  workerData: WorkerStatus | null;
  modelHealthData: ModelHealthMetrics | null;
  engagementData: UserEngagementMetrics | null;
  recommendationData: RecommendationQualityMetrics | null;
  
  // UI State
  timeRange: '1h' | '6h' | '24h' | '7d';
  autoRefresh: boolean;
  moduleFilter: 'all' | 'healthy' | 'degraded' | 'down';
  
  // Actions
  setTimeRange: (range: string) => void;
  toggleAutoRefresh: () => void;
  setModuleFilter: (filter: string) => void;
  refreshAll: () => Promise<void>;
}
```

### TanStack Query Hooks

```typescript
// Health
useHealthCheck() // Polls every 30s
useModuleHealth(moduleName: string)

// Performance
usePerformanceMetrics(timeRange: string)
useRecommendationQuality(timeRange: string)
useUserEngagement(timeRange: string)

// Infrastructure
useDatabaseMetrics()
useDbPoolStatus()
useEventBusMetrics()
useEventHistory(limit: number)
useCacheStats()
useWorkerStatus()

// ML
useMLModelHealth()
useModelHealth()
```

---

## API Integration

### Base Configuration

```typescript
// lib/api/monitoring.ts
import { apiClient } from './client';

const MONITORING_BASE = '/api/monitoring';

export const monitoringApi = {
  // Health
  getHealth: () => 
    apiClient.get<HealthCheckResponse>(`${MONITORING_BASE}/health`),
  
  getMLHealth: () => 
    apiClient.get(`${MONITORING_BASE}/health/ml`),
  
  getModelHealth: () => 
    apiClient.get<ModelHealthMetrics>(`${MONITORING_BASE}/model-health`),
  
  // Performance
  getPerformance: () => 
    apiClient.get<PerformanceMetrics>(`${MONITORING_BASE}/performance`),
  
  getRecommendationQuality: (params?: { time_range?: string }) => 
    apiClient.get<RecommendationQualityMetrics>(
      `${MONITORING_BASE}/recommendation-quality`,
      { params }
    ),
  
  getUserEngagement: (params?: { time_range?: string }) => 
    apiClient.get<UserEngagementMetrics>(
      `${MONITORING_BASE}/user-engagement`,
      { params }
    ),
  
  // Infrastructure
  getDatabase: () => 
    apiClient.get<DatabaseMetrics>(`${MONITORING_BASE}/database`),
  
  getDbPool: () => 
    apiClient.get(`${MONITORING_BASE}/db/pool`),
  
  getEventBus: () => 
    apiClient.get<EventBusMetrics>(`${MONITORING_BASE}/events`),
  
  getEventHistory: (params?: { limit?: number }) => 
    apiClient.get(`${MONITORING_BASE}/events/history`, { params }),
  
  getCacheStats: () => 
    apiClient.get<CacheStats>(`${MONITORING_BASE}/cache/stats`),
  
  getWorkerStatus: () => 
    apiClient.get<WorkerStatus>(`${MONITORING_BASE}/workers/status`),
};
```

### Auto-Refresh Strategy

```typescript
// hooks/useAutoRefresh.ts
export function useAutoRefresh(enabled: boolean, interval = 30000) {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    if (!enabled) return;
    
    const timer = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    }, interval);
    
    return () => clearInterval(timer);
  }, [enabled, interval, queryClient]);
}
```

---

## Component Specifications

### 1. OpsPage

**Location**: `src/pages/ops/index.tsx`

**Responsibilities**:
- Route handler for `/ops`
- Data fetching orchestration
- Auto-refresh coordination

```typescript
export default function OpsPage() {
  const { autoRefresh, timeRange } = useOpsStore();
  
  // Fetch all data
  const { data: health } = useHealthCheck();
  const { data: performance } = usePerformanceMetrics(timeRange);
  const { data: database } = useDatabaseMetrics();
  // ... other queries
  
  // Auto-refresh
  useAutoRefresh(autoRefresh);
  
  return (
    <OpsLayout>
      <PageHeader />
      <HealthOverviewSection health={health} />
      <ModuleHealthSection health={health} />
      <PerformanceSection data={performance} />
      <InfrastructureSection 
        database={database}
        eventBus={eventBus}
        cache={cache}
      />
      <WorkersSection data={workers} />
      <MLSection data={modelHealth} />
      <EngagementSection 
        engagement={engagement}
        recommendations={recommendations}
      />
    </OpsLayout>
  );
}
```

### 2. HealthStatusCard

**Location**: `src/components/ops/HealthStatusCard.tsx`

**Props**:
```typescript
interface HealthStatusCardProps {
  status: 'healthy' | 'degraded' | 'down';
  timestamp: string;
  moduleCount: number;
  degradedModules: string[];
}
```

**Visual Design**:
- Large status indicator (green/yellow/red circle)
- Status text ("System Healthy", "System Degraded", "System Down")
- Last updated timestamp
- Module count summary
- List of degraded modules (if any)

### 3. ModuleHealthCard

**Location**: `src/components/ops/ModuleHealthCard.tsx`

**Props**:
```typescript
interface ModuleHealthCardProps {
  moduleName: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number;
  errorCount: number;
  onClick?: () => void;
}
```

**Visual Design**:
- Module name (e.g., "Resources", "Search")
- Status badge (colored dot + text)
- Response time (ms)
- Error count (last 24h)
- Hover effect for click interaction

### 4. PerformanceChart

**Location**: `src/components/ops/PerformanceChart.tsx`

**Props**:
```typescript
interface PerformanceChartProps {
  data: PerformanceMetrics;
  timeRange: string;
}
```

**Chart Type**: Line chart (Recharts)

**Metrics Displayed**:
- P50 response time (blue line)
- P95 response time (orange line)
- P99 response time (red line)
- X-axis: Time
- Y-axis: Milliseconds

### 5. DatabaseMonitor

**Location**: `src/components/ops/DatabaseMonitor.tsx`

**Props**:
```typescript
interface DatabaseMonitorProps {
  data: DatabaseMetrics;
}
```

**Sections**:
1. **Connection Pool** (progress bar)
   - Active connections (green)
   - Idle connections (blue)
   - Max connections (gray)
   - Utilization percentage

2. **Query Performance** (table)
   - Average query time
   - Slow queries count
   - Slowest query time

3. **Table Stats** (table)
   - Table name
   - Row count
   - Size (MB)

### 6. EventBusMonitor

**Location**: `src/components/ops/EventBusMonitor.tsx`

**Props**:
```typescript
interface EventBusMonitorProps {
  data: EventBusMetrics;
  history: Array<{ type: string; timestamp: string }>;
}
```

**Sections**:
1. **Metrics Grid**
   - Events emitted
   - Events received
   - P95 latency
   - Failed deliveries

2. **Event Types** (pie chart)
   - Breakdown by event type

3. **Event History** (timeline)
   - Last 100 events
   - Event type + timestamp

### 7. CacheMonitor

**Location**: `src/components/ops/CacheMonitor.tsx`

**Props**:
```typescript
interface CacheMonitorProps {
  data: CacheStats;
  onClearCache: () => void;
}
```

**Sections**:
1. **Hit Rate** (donut chart)
   - Hit rate percentage (green)
   - Miss rate percentage (red)

2. **Top Keys** (table)
   - Key name
   - Hit count
   - Size (bytes)

3. **Actions**
   - Clear cache button (with confirmation dialog)

### 8. WorkerMonitor

**Location**: `src/components/ops/WorkerMonitor.tsx`

**Props**:
```typescript
interface WorkerMonitorProps {
  data: WorkerStatus;
}
```

**Sections**:
1. **Worker Status**
   - Active workers count
   - Health status badge

2. **Queue Metrics**
   - Queue length
   - Processing rate (tasks/sec)

3. **Failed Tasks**
   - Failed tasks count
   - Link to task details (if available)

### 9. ModelHealthMonitor

**Location**: `src/components/ops/ModelHealthMonitor.tsx`

**Props**:
```typescript
interface ModelHealthMonitorProps {
  data: ModelHealthMetrics;
}
```

**Layout**: Grid of model cards (3 columns)

**Each Model Card Shows**:
- Model name (e.g., "Embedding Model")
- Load status (✓ Loaded / ✗ Not Loaded)
- Inference time (ms)
- Memory usage (MB)
- Last inference timestamp

### 10. MetricCard

**Location**: `src/components/ops/MetricCard.tsx`

**Props**:
```typescript
interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  status?: 'success' | 'warning' | 'error';
  hasAnomaly?: boolean; // NEW - Option C
  anomalyMessage?: string; // NEW - Option C
}
```

**Reusable Component** for displaying single metrics

---

## NEW: Option C Specific Components

### 11. SmartAlertPanel

**Location**: `src/components/ops/SmartAlertPanel.tsx`

**Props**:
```typescript
interface SmartAlertPanelProps {
  alerts: Alert[];
  onDismiss: (alertId: string) => void;
  onAcknowledge: (alertId: string) => void;
  onViewHistory: () => void;
}

interface Alert {
  id: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
  source: string; // module name or metric
  acknowledged: boolean;
}
```

**Visual Design**:
- Uses magic-ui animated alerts for visual impact
- Stacked alerts with dismiss/acknowledge buttons
- Color-coded by severity (blue/yellow/red)
- Slide-in animation when new alert appears
- Sound notification (optional, toggleable)

**Alert Logic**:
```typescript
// Alert triggers
const ALERT_THRESHOLDS = {
  errorRate: 5, // percentage
  responseTime: 500, // ms
  queueLength: 100, // items
  cacheHitRate: 50, // percentage (below)
  workerHealth: 'degraded',
};
```

### 12. AnomalyDetector

**Location**: `src/components/ops/AnomalyDetector.tsx`

**Props**:
```typescript
interface AnomalyDetectorProps {
  currentValue: number;
  historicalValues: number[];
  threshold?: number; // standard deviations
  onAnomalyDetected?: (anomaly: Anomaly) => void;
}

interface Anomaly {
  type: 'spike' | 'drop' | 'pattern';
  severity: 'low' | 'medium' | 'high';
  message: string;
}
```

**Detection Logic**:
```typescript
// Simple anomaly detection
function detectAnomaly(current: number, historical: number[]): Anomaly | null {
  const mean = historical.reduce((a, b) => a + b) / historical.length;
  const stdDev = Math.sqrt(
    historical.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / historical.length
  );
  
  const zScore = (current - mean) / stdDev;
  
  if (Math.abs(zScore) > 2) {
    return {
      type: zScore > 0 ? 'spike' : 'drop',
      severity: Math.abs(zScore) > 3 ? 'high' : 'medium',
      message: `Unusual ${zScore > 0 ? 'increase' : 'decrease'} detected`,
    };
  }
  
  return null;
}
```

**Visual Indicator**:
- Small warning icon next to metric
- Tooltip with anomaly details
- Highlight metric card border

### 13. TrendIndicator

**Location**: `src/components/ops/TrendIndicator.tsx`

**Props**:
```typescript
interface TrendIndicatorProps {
  trend: 'up' | 'down' | 'neutral';
  value?: string; // e.g., "+5.2%"
  size?: 'sm' | 'md' | 'lg';
}
```

**Visual Design**:
- Up arrow (green) for improving metrics
- Down arrow (red) for degrading metrics
- Horizontal line (gray) for stable metrics
- Optional percentage change value

### 14. IngestionQueueViz

**Location**: `src/components/ops/IngestionQueueViz.tsx`

**Props**:
```typescript
interface IngestionQueueVizProps {
  queue: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
}
```

**Visual Design**:
- Stacked bar chart or donut chart
- Color-coded sections (gray/blue/green/red)
- Hover shows exact counts
- Click section to filter job history

### 15. IngestionTrigger

**Location**: `src/components/ops/IngestionTrigger.tsx`

**Props**:
```typescript
interface IngestionTriggerProps {
  onIngest: (repoUrl: string) => Promise<void>;
}
```

**Visual Design**:
- Input field for repository URL
- "Ingest" button
- Loading state during ingestion
- Success/error notification
- Recent ingestions list (last 5)

### 16. JobHistoryTable

**Location**: `src/components/ops/JobHistoryTable.tsx`

**Props**:
```typescript
interface JobHistoryTableProps {
  jobs: IngestionJob[];
  onRetry: (jobId: string) => void;
  onCancel: (jobId: string) => void;
}

interface IngestionJob {
  id: string;
  repo_url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
}
```

**Visual Design**:
- Table with columns: Repo, Status, Started, Duration, Actions
- Status badge (color-coded)
- Retry button for failed jobs
- Cancel button for stuck jobs
- Expandable row for error details

### 17. WorkerHeartbeat

**Location**: `src/components/ops/WorkerHeartbeat.tsx`

**Props**:
```typescript
interface WorkerHeartbeatProps {
  workers: Worker[];
}

interface Worker {
  id: string;
  type: 'cloud' | 'edge';
  status: 'online' | 'offline' | 'degraded';
  last_heartbeat: string;
  gpu_available?: boolean;
}
```

**Visual Design**:
- Uses magic-ui orbiting circles for heartbeat animation
- Each worker is a circle
- Pulsing animation when online
- Gray/static when offline
- Tooltip shows worker details

### 18. SparseEmbeddingGenerator

**Location**: `src/components/ops/SparseEmbeddingGenerator.tsx`

**Props**:
```typescript
interface SparseEmbeddingGeneratorProps {
  onGenerate: () => Promise<void>;
  lastGenerated?: string;
}
```

**Visual Design**:
- "Generate Sparse Embeddings" button
- Progress bar during generation
- Estimated time remaining
- Last generated timestamp
- Success/error notification

### 19. AlertHistoryDrawer

**Location**: `src/components/ops/AlertHistoryDrawer.tsx`

**Props**:
```typescript
interface AlertHistoryDrawerProps {
  alerts: Alert[];
  open: boolean;
  onClose: () => void;
}
```

**Visual Design**:
- Drawer from right side
- Timeline of alerts
- Filter by severity
- Search by message
- Export to CSV

### 20. AlertPreferencesDrawer

**Location**: `src/components/ops/AlertPreferencesDrawer.tsx`

**Props**:
```typescript
interface AlertPreferencesDrawerProps {
  preferences: AlertPreferences;
  onSave: (preferences: AlertPreferences) => void;
  open: boolean;
  onClose: () => void;
}

interface AlertPreferences {
  errorRateThreshold: number;
  responseTimeThreshold: number;
  queueLengthThreshold: number;
  soundEnabled: boolean;
  metrics: string[]; // which metrics to monitor
}
```

**Visual Design**:
- Form with threshold inputs
- Toggle switches for each metric
- Sound notification toggle
- Save/Cancel buttons

---

## Styling & Theme

### Color Palette

**Status Colors**:
- Healthy: `green-500` (#22c55e)
- Degraded: `yellow-500` (#eab308)
- Down: `red-500` (#ef4444)

**Chart Colors**:
- Primary: `blue-500` (#3b82f6)
- Secondary: `purple-500` (#a855f7)
- Tertiary: `orange-500` (#f97316)

### Layout

**Grid System**:
- 12-column grid
- Gap: 4 (1rem)
- Responsive breakpoints:
  - Desktop: 3-4 columns
  - Tablet: 2 columns
  - Mobile: 1 column

**Card Style**:
- Border: `border border-border`
- Background: `bg-card`
- Padding: `p-6`
- Rounded: `rounded-lg`
- Shadow: `shadow-sm`

---

## Error Handling

### Scenarios

1. **Backend Unreachable**
   - Show last known values with "Stale Data" warning
   - Display timestamp of last successful fetch
   - Retry button

2. **Partial Data Failure**
   - Show available data
   - Display error message for failed sections
   - Continue auto-refresh for working endpoints

3. **Timeout**
   - Show loading skeleton
   - Timeout after 10 seconds
   - Display timeout error with retry option

### Error UI

```typescript
<ErrorBoundary
  fallback={
    <Alert variant="destructive">
      <AlertTitle>Failed to load monitoring data</AlertTitle>
      <AlertDescription>
        {error.message}
        <Button onClick={retry}>Retry</Button>
      </AlertDescription>
    </Alert>
  }
>
  {children}
</ErrorBoundary>
```

---

## Performance Optimizations

1. **Lazy Loading**
   - Load charts only when visible (Intersection Observer)
   - Defer non-critical metrics

2. **Memoization**
   - Memoize expensive calculations (chart data transformations)
   - Use `React.memo` for static components

3. **Debouncing**
   - Debounce time range selector (500ms)
   - Debounce filter changes (300ms)

4. **Virtual Scrolling**
   - Use virtual scrolling for event history (100+ items)
   - Use virtual scrolling for table stats (50+ tables)

5. **Request Batching**
   - Batch multiple metric requests into single call (if backend supports)
   - Use HTTP/2 multiplexing

---

## Accessibility

### Keyboard Navigation
- Tab through all interactive elements
- Enter/Space to activate buttons
- Arrow keys for chart navigation

### Screen Reader Support
- ARIA labels for all metrics
- ARIA live regions for auto-updating data
- Descriptive alt text for status indicators

### Color Blindness
- Use patterns in addition to colors (dots, stripes)
- Ensure sufficient contrast (WCAG AA)
- Provide text labels for all status indicators

---

## Testing Strategy

### Unit Tests
- Component rendering
- Data transformation logic
- Error handling

### Integration Tests
- API integration
- Auto-refresh behavior
- Filter/sort functionality

### E2E Tests
- Full dashboard load
- Time range selection
- Module health filtering
- Cache clear action

---

## Related Documentation

- [Requirements](./requirements.md)
- [Tasks](./tasks.md)
- [Backend Monitoring API](../../../backend/docs/api/monitoring.md)
- [Phase 1 Design](../phase1-workbench-navigation/design.md)
