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
  const { data: health } = useHealthCheck();
  const { data: performance } = usePerformanceMetrics();
  const { data: database } = useDatabaseMetrics();
  const { data: eventBus } = useEventBusMetrics();
  const { data: eventHistory } = useEventHistory();
  const { data: cache } = useCacheStats();
  const { data: workers } = useMonitoringWorkerStatus();
  const { data: modelHealth } = useModelHealth();
  const { data: engagement } = useUserEngagement(timeRange);
  const { data: recommendations } = useRecommendationQuality(timeRange);
  
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
