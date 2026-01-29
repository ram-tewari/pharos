// Monitoring API Response Types

export type HealthStatus = 'healthy' | 'degraded' | 'down';

export interface ModuleHealth {
  status: HealthStatus;
  response_time_ms: number;
  error_count: number;
}

export interface HealthCheckResponse {
  status: HealthStatus;
  timestamp: string;
  modules: Record<string, ModuleHealth>;
}

export interface PerformanceMetrics {
  api_response_time: {
    p50: number;
    p95: number;
    p99: number;
  };
  request_rate: number;
  error_rate: number;
  uptime_seconds: number;
}

export interface DatabaseMetrics {
  connection_pool: {
    active: number;
    idle: number;
    max: number;
    utilization: number;
  };
  query_performance: {
    avg_query_time_ms: number;
    slow_queries: number;
  };
  table_stats: Record<string, {
    row_count: number;
    size_mb: number;
  }>;
}

export interface EventBusMetrics {
  events_emitted: number;
  events_received: number;
  event_latency_ms: {
    p50: number;
    p95: number;
    p99: number;
  };
  event_types: Record<string, number>;
  failed_deliveries: number;
}

export interface CacheStats {
  hit_rate: number;
  miss_rate: number;
  size_mb: number;
  eviction_rate: number;
  top_keys: Array<{
    key: string;
    hits: number;
    size_bytes: number;
  }>;
}

export interface WorkerStatus {
  active_workers: number;
  worker_health: HealthStatus;
  queue_length: number;
  processing_rate: number;
  failed_tasks: number;
}

export interface ModelHealthMetrics {
  models: Record<string, {
    loaded: boolean;
    inference_time_ms: number;
    memory_mb: number;
    error_rate: number;
    last_inference: string;
  }>;
}

export interface UserEngagementMetrics {
  active_users: number;
  resources_created: number;
  resources_updated: number;
  searches_performed: number;
  annotations_created: number;
  collections_created: number;
  time_range: string;
}

export interface RecommendationQualityMetrics {
  accuracy: number;
  click_through_rate: number;
  avg_user_rating: number;
  model_performance: Record<string, {
    precision: number;
    recall: number;
    f1_score: number;
  }>;
}

export interface EventHistoryItem {
  type: string;
  timestamp: string;
  data?: Record<string, unknown>;
}
