/**
 * Monitoring Hooks
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * TanStack Query hooks for monitoring data
 */

import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '@/lib/api/monitoring';

const REFETCH_INTERVAL = 30000; // 30 seconds

export function useHealthCheck() {
  return useQuery({
    queryKey: ['monitoring', 'health'],
    queryFn: monitoringApi.getHealth,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useMLModelHealth() {
  return useQuery({
    queryKey: ['monitoring', 'ml-health'],
    queryFn: monitoringApi.getMLHealth,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useModelHealth() {
  return useQuery({
    queryKey: ['monitoring', 'model-health'],
    queryFn: monitoringApi.getModelHealth,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function usePerformanceMetrics() {
  return useQuery({
    queryKey: ['monitoring', 'performance'],
    queryFn: monitoringApi.getPerformance,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useRecommendationQuality(timeRange?: string) {
  return useQuery({
    queryKey: ['monitoring', 'recommendation-quality', timeRange],
    queryFn: () => monitoringApi.getRecommendationQuality({ time_range: timeRange }),
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useUserEngagement(timeRange?: string) {
  return useQuery({
    queryKey: ['monitoring', 'user-engagement', timeRange],
    queryFn: () => monitoringApi.getUserEngagement({ time_range: timeRange }),
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useDatabaseMetrics() {
  return useQuery({
    queryKey: ['monitoring', 'database'],
    queryFn: monitoringApi.getDatabase,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useDbPoolStatus() {
  return useQuery({
    queryKey: ['monitoring', 'db-pool'],
    queryFn: monitoringApi.getDbPool,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useEventBusMetrics() {
  return useQuery({
    queryKey: ['monitoring', 'event-bus'],
    queryFn: monitoringApi.getEventBus,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useEventHistory(limit = 100) {
  return useQuery({
    queryKey: ['monitoring', 'event-history', limit],
    queryFn: () => monitoringApi.getEventHistory({ limit }),
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useCacheStats() {
  return useQuery({
    queryKey: ['monitoring', 'cache-stats'],
    queryFn: monitoringApi.getCacheStats,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useWorkerStatus() {
  return useQuery({
    queryKey: ['monitoring', 'worker-status'],
    queryFn: monitoringApi.getWorkerStatus,
    refetchInterval: REFETCH_INTERVAL,
  });
}
