/**
 * Ops Page
 * 
 * Phase 7: Ops & Edge Management (Option C: Hybrid Power)
 * Main operations dashboard with monitoring, alerts, and infrastructure metrics
 */

import { createFileRoute } from '@tanstack/react-router';
import { OpsLayout } from '@/components/ops/OpsLayout';
import { PageHeader } from '@/components/ops/PageHeader';
import { HealthOverviewSection } from '@/components/ops/HealthOverviewSection';
import { ModuleHealthSection } from '@/components/ops/ModuleHealthSection';
import { InfrastructureSection } from '@/components/ops/InfrastructureSection';
import { useOpsStore } from '@/stores/opsStore';
import { useAutoRefresh } from '@/lib/hooks/useAutoRefresh';
import {
  useHealthCheck,
  usePerformanceMetrics,
  useDatabaseMetrics,
  useEventBusMetrics,
  useEventHistory,
  useCacheStats,
  useWorkerStatus as useMonitoringWorkerStatus,
  useModelHealth,
  useUserEngagement,
  useRecommendationQuality,
} from '@/lib/hooks/useMonitoring';

const OpsPage = () => {
  const { autoRefresh, timeRange } = useOpsStore();
  
  // Auto-refresh
  useAutoRefresh(autoRefresh);
  
  // Fetch all data
  const { data: health, error: healthError, isLoading: healthLoading } = useHealthCheck();
  const { data: performance, error: perfError } = usePerformanceMetrics();
  const { data: database, error: dbError } = useDatabaseMetrics();
  const { data: eventBus, error: eventError } = useEventBusMetrics();
  const { data: eventHistory, error: historyError } = useEventHistory();
  const { data: cache, error: cacheError } = useCacheStats();
  const { data: workers, error: workersError } = useMonitoringWorkerStatus();
  const { data: modelHealth, error: modelError } = useModelHealth();
  const { data: engagement, error: engagementError } = useUserEngagement(timeRange);
  const { data: recommendations, error: recsError } = useRecommendationQuality(timeRange);
  
  // Log errors in development
  if (import.meta.env.DEV) {
    if (healthError) console.error('[Ops] Health error:', healthError);
    if (perfError) console.error('[Ops] Performance error:', perfError);
    if (dbError) console.error('[Ops] Database error:', dbError);
    if (eventError) console.error('[Ops] Event bus error:', eventError);
    if (historyError) console.error('[Ops] Event history error:', historyError);
    if (cacheError) console.error('[Ops] Cache error:', cacheError);
    if (workersError) console.error('[Ops] Workers error:', workersError);
    if (modelError) console.error('[Ops] Model error:', modelError);
  }
  
  if (healthLoading) {
    return (
      <OpsLayout>
        <PageHeader />
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading monitoring data...</p>
        </div>
      </OpsLayout>
    );
  }
  
  if (healthError) {
    return (
      <OpsLayout>
        <PageHeader />
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <p className="text-destructive">Failed to load monitoring data</p>
          <p className="text-sm text-muted-foreground">
            {healthError instanceof Error ? healthError.message : 'Unknown error'}
          </p>
          <p className="text-xs text-muted-foreground">
            Check console for details or ensure the backend is running
          </p>
        </div>
      </OpsLayout>
    );
  }
  
  return (
    <OpsLayout>
      <PageHeader />
      
      <div className="space-y-6">
        <HealthOverviewSection health={health} performance={performance} />
        <ModuleHealthSection health={health} />
        <InfrastructureSection 
          database={database}
          eventBus={eventBus}
          eventHistory={eventHistory}
          cache={cache}
          workers={workers}
          modelHealth={modelHealth}
        />
      </div>
    </OpsLayout>
  );
};

export const Route = createFileRoute('/_auth/ops')({
  component: OpsPage,
});
