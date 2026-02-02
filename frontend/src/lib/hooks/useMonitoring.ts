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
    queryFn: async () => {
      try {
        const response = await monitoringApi.getHealth();
        console.log('[Monitoring] Health check response:', response);
        return response;
      } catch (error) {
        console.error('[Monitoring] Health check failed:', error);
        throw error;
      }
    },
    refetchInterval: REFETCH_INTERVAL,
    retry: 3,
    retryDelay: 1000,
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
  // Convert timeRange to days (default 7)
  const days = timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 7;
  
  return useQuery({
    queryKey: ['monitoring', 'recommendation-quality', days],
    queryFn: () => monitoringApi.getRecommendationQuality({ time_window_days: days }),
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useUserEngagement(timeRange?: string) {
  // Convert timeRange to days (default 7)
  const days = timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 7;
  
  return useQuery({
    queryKey: ['monitoring', 'user-engagement', days],
    queryFn: () => monitoringApi.getUserEngagement({ time_window_days: days }),
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
