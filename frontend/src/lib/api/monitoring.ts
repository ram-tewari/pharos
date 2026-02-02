/**
 * Monitoring API Client
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Provides monitoring, health, and infrastructure metrics endpoints
 */

import { apiClient } from '@/core/api/client';
import type {
  HealthCheckResponse,
  PerformanceMetrics,
  DatabaseMetrics,
  EventBusMetrics,
  CacheStats,
  WorkerStatus,
  ModelHealthMetrics,
  UserEngagementMetrics,
  RecommendationQualityMetrics,
  EventHistoryItem,
} from '@/types/monitoring';

const MONITORING_BASE = '/api/monitoring';

export const monitoringApi = {
  // Health
  getHealth: () => apiClient.get<HealthCheckResponse>(`${MONITORING_BASE}/health`),
  getMLHealth: () => apiClient.get(`${MONITORING_BASE}/health/ml`),
  getModelHealth: () => apiClient.get<ModelHealthMetrics>(`${MONITORING_BASE}/model-health`),
  getModuleHealth: (moduleName: string) => apiClient.get(`${MONITORING_BASE}/health/module/${moduleName}`),
  
  // Performance
  getPerformance: () => apiClient.get<PerformanceMetrics>(`${MONITORING_BASE}/performance`),
  getRecommendationQuality: (params?: { time_window_days?: number }) => 
    apiClient.get<RecommendationQualityMetrics>(`${MONITORING_BASE}/recommendation-quality`, { params }),
  getUserEngagement: (params?: { time_window_days?: number }) => 
    apiClient.get<UserEngagementMetrics>(`${MONITORING_BASE}/user-engagement`, { params }),
  
  // Infrastructure
  getDatabase: () => apiClient.get<DatabaseMetrics>(`${MONITORING_BASE}/database`),
  getDbPool: () => apiClient.get(`${MONITORING_BASE}/db/pool`),
  getEventBus: () => apiClient.get<EventBusMetrics>(`${MONITORING_BASE}/events`),
  getEventHistory: (params?: { limit?: number }) => 
    apiClient.get<EventHistoryResponse>(`${MONITORING_BASE}/events/history`, { params }),
  getCacheStats: () => apiClient.get<CacheStats>(`${MONITORING_BASE}/cache/stats`),
  getWorkerStatus: () => apiClient.get<WorkerStatus>(`${MONITORING_BASE}/workers/status`),
};
