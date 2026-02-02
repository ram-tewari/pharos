// Monitoring API Response Types

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'down';

export interface ComponentHealth {
  status: HealthStatus | string;
  message: string;
  worker_count?: number;
}

export interface HealthCheckResponse {
  status: HealthStatus;
  message: string;
  timestamp: string;
  components: {
    database: ComponentHealth;
    redis: ComponentHealth;
    celery: ComponentHealth;
    ncf_model: ComponentHealth;
    api: ComponentHealth;
  };
  modules?: Record<string, any>;
}

export interface PerformanceMetrics {
  status: string;
  timestamp: string;
  metrics: {
    cache_hit_rate?: number;
    method_execution_times?: Record<string, any>;
    slow_query_count?: number;
    [key: string]: any;
  };
}

export interface DatabaseMetrics {
  status: string;
  timestamp: string;
  database: {
    type: string;
    healthy: boolean;
    health_message: string;
  };
  connection_pool: {
    database_type: string;
    pool_size: number;
    checked_in: number;
    checked_out: number;
    overflow: number;
    total_connections: number;
    pool_usage_percent: number;
  };
  warnings: Array<{
    level: string;
    message: string;
    recommendation: string;
  }>;
}

export interface EventBusMetrics {
  status: string;
  timestamp: string;
  metrics: {
    events_emitted: number;
    events_delivered: number;
    handler_errors: number;
    event_types: Record<string, number>;
    handler_latency_p50: number;
    handler_latency_p95: number;
    handler_latency_p99: number;
  };
}

export interface CacheStats {
  status: string;
  timestamp: string;
  cache_stats: {
    hit_rate: number;
    hit_rate_percent: number;
    hits: number;
    misses: number;
    invalidations: number;
    total_requests: number;
  };
}

export interface WorkerStatus {
  status: string;
  timestamp: string;
  message?: string;
  workers?: {
    worker_count: number;
    total_active_tasks: number;
    total_scheduled_tasks: number;
    active_tasks: Record<string, any[]>;
    scheduled_tasks: Record<string, any[]>;
    stats: Record<string, any>;
  };
}

export interface ModelHealthMetrics {
  status: string;
  timestamp: string;
  model?: {
    available: boolean;
    path?: string;
    size_mb?: number;
    last_modified?: string;
    num_users?: number;
    num_items?: number;
    embedding_dim?: number;
    message?: string;
    error?: string;
  };
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

export interface EventHistoryResponse {
  status: string;
  timestamp: string;
  count: number;
  events: EventHistoryItem[];
}

export interface EventHistoryItem {
  name: string;
  timestamp: string;
  data?: Record<string, unknown>;
  priority?: number;
}
