/**
 * Infrastructure Section
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Database, event bus, cache, workers, and ML model monitoring
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, Activity, HardDrive, Cpu, Brain } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { StatusBadge } from './StatusBadge';
import type {
  DatabaseMetrics,
  EventBusMetrics,
  EventHistoryResponse,
  CacheStats,
  WorkerStatus,
  ModelHealthMetrics,
} from '@/types/monitoring';

interface InfrastructureSectionProps {
  database?: DatabaseMetrics;
  eventBus?: EventBusMetrics;
  eventHistory?: EventHistoryResponse;
  cache?: CacheStats;
  workers?: WorkerStatus;
  modelHealth?: ModelHealthMetrics;
}

export function InfrastructureSection({
  database,
  eventBus,
  eventHistory,
  cache,
  workers,
  modelHealth,
}: InfrastructureSectionProps) {
  return (
    <div className="space-y-6">
      {/* Database Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database
          </CardTitle>
        </CardHeader>
        <CardContent>
          {database ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">{database.database?.type?.toUpperCase() ?? 'Unknown'}</p>
                  <p className="text-xs text-muted-foreground">{database.database?.health_message}</p>
                </div>
                <StatusBadge status={database.database?.healthy ? 'healthy' : 'unhealthy'} />
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard
                  title="Connection Pool"
                  value={`${database?.connection_pool?.checked_out ?? 0}/${database?.connection_pool?.pool_size ?? 0}`}
                  status={(database?.connection_pool?.pool_usage_percent ?? 0) > 80 ? 'warning' : 'success'}
                />
                <MetricCard
                  title="Pool Usage"
                  value={database?.connection_pool?.pool_usage_percent?.toFixed(1) ?? '0'}
                  unit="%"
                  status={(database?.connection_pool?.pool_usage_percent ?? 0) > 80 ? 'warning' : 'success'}
                />
                <MetricCard
                  title="Total Connections"
                  value={database?.connection_pool?.total_connections ?? 0}
                />
              </div>
              {database.warnings && database.warnings.length > 0 && (
                <div className="space-y-2">
                  {database.warnings.map((warning, i) => (
                    <div key={i} className="text-xs p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800">
                      <p className="font-medium text-yellow-800 dark:text-yellow-200">{warning.message}</p>
                      <p className="text-yellow-700 dark:text-yellow-300">{warning.recommendation}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading database metrics...</p>
          )}
        </CardContent>
      </Card>

      {/* Event Bus Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Event Bus
          </CardTitle>
        </CardHeader>
        <CardContent>
          {eventBus ? (
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  title="Events Emitted"
                  value={eventBus.metrics?.events_emitted ?? 0}
                />
                <MetricCard
                  title="Events Delivered"
                  value={eventBus.metrics?.events_delivered ?? 0}
                />
                <MetricCard
                  title="Latency (P95)"
                  value={eventBus.metrics?.handler_latency_p95 ?? '-'}
                  unit="ms"
                  status={eventBus.metrics?.handler_latency_p95 && eventBus.metrics.handler_latency_p95 > 1 ? 'warning' : 'success'}
                />
                <MetricCard
                  title="Handler Errors"
                  value={eventBus.metrics?.handler_errors ?? 0}
                  status={(eventBus.metrics?.handler_errors ?? 0) > 0 ? 'error' : 'success'}
                />
              </div>
              
              {eventHistory && eventHistory.events && eventHistory.events.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Recent Events</h4>
                  <div className="space-y-1 max-h-40 overflow-y-auto">
                    {eventHistory.events.slice(0, 10).map((event, i) => (
                      <div key={i} className="text-xs flex items-center justify-between py-1 border-b">
                        <span className="font-mono">{event.name}</span>
                        <span className="text-muted-foreground">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading event bus metrics...</p>
          )}
        </CardContent>
      </Card>

      {/* Cache Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive className="h-5 w-5" />
            Cache
          </CardTitle>
        </CardHeader>
        <CardContent>
          {cache ? (
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard
                title="Hit Rate"
                value={cache.cache_stats?.hit_rate_percent != null ? `${cache.cache_stats.hit_rate_percent.toFixed(1)}%` : '-'}
                status={cache.cache_stats?.hit_rate_percent != null && cache.cache_stats.hit_rate_percent < 50 ? 'warning' : 'success'}
              />
              <MetricCard
                title="Total Requests"
                value={cache.cache_stats?.total_requests ?? 0}
              />
              <MetricCard
                title="Invalidations"
                value={cache.cache_stats?.invalidations ?? 0}
              />
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading cache stats...</p>
          )}
        </CardContent>
      </Card>

      {/* Workers Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            Workers
          </CardTitle>
        </CardHeader>
        <CardContent>
          {workers ? (
            <div className="space-y-4">
              {workers.status === 'error' ? (
                <div className="text-sm text-muted-foreground">
                  <p>{workers.message || 'Could not connect to workers'}</p>
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Active Workers</p>
                      <p className="text-2xl font-bold">{workers.workers?.worker_count ?? 0}</p>
                    </div>
                    <StatusBadge status={workers.workers?.worker_count && workers.workers.worker_count > 0 ? 'healthy' : 'degraded'} />
                  </div>
                  
                  <div className="grid gap-4 md:grid-cols-3">
                    <MetricCard
                      title="Active Tasks"
                      value={workers.workers?.total_active_tasks ?? 0}
                    />
                    <MetricCard
                      title="Scheduled Tasks"
                      value={workers.workers?.total_scheduled_tasks ?? 0}
                    />
                    <MetricCard
                      title="Status"
                      value={workers.status === 'ok' ? 'Connected' : 'Disconnected'}
                    />
                  </div>
                </>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading worker status...</p>
          )}
        </CardContent>
      </Card>

      {/* ML Models Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            ML Models
          </CardTitle>
        </CardHeader>
        <CardContent>
          {modelHealth ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">NCF Recommendation Model</p>
                  <p className="text-xs text-muted-foreground">
                    {modelHealth.model?.available ? 'Model loaded' : modelHealth.model?.message || 'Not available'}
                  </p>
                </div>
                <span className={`text-xs ${modelHealth.model?.available ? 'text-green-500' : 'text-yellow-500'}`}>
                  {modelHealth.model?.available ? '✓ Available' : '○ Not Trained'}
                </span>
              </div>
              {modelHealth.model?.available && (
                <div className="grid gap-4 md:grid-cols-3">
                  <MetricCard
                    title="Model Size"
                    value={modelHealth.model.size_mb?.toFixed(2) ?? '-'}
                    unit="MB"
                  />
                  <MetricCard
                    title="Users"
                    value={modelHealth.model.num_users ?? '-'}
                  />
                  <MetricCard
                    title="Items"
                    value={modelHealth.model.num_items ?? '-'}
                  />
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading model health...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
