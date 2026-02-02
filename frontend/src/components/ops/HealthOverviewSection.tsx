/**
 * Health Overview Section
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Overall system health and quick stats
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from './StatusBadge';
import { MetricCard } from './MetricCard';
import { Activity, TrendingUp, AlertTriangle, Clock } from 'lucide-react';
import type { HealthCheckResponse, PerformanceMetrics } from '@/types/monitoring';

interface HealthOverviewSectionProps {
  health?: HealthCheckResponse;
  performance?: PerformanceMetrics;
}

export function HealthOverviewSection({ health, performance }: HealthOverviewSectionProps) {
  // Use mock data if no real data available
  const mockHealth: HealthCheckResponse = {
    status: 'degraded',
    message: 'Waiting for backend connection...',
    timestamp: new Date().toISOString(),
    components: {
      database: { status: 'unknown', message: 'Not connected' },
      redis: { status: 'unknown', message: 'Not connected' },
      celery: { status: 'unknown', message: 'Not connected' },
      ncf_model: { status: 'unavailable', message: 'Not loaded' },
      api: { status: 'unknown', message: 'Checking...' },
    },
  };

  const mockPerformance: PerformanceMetrics = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    metrics: {
      api_response_time_p95: 0,
      request_rate: 0,
      error_rate: 0,
      uptime_seconds: 0,
    },
  };

  const displayHealth = health || mockHealth;
  const displayPerformance = performance || mockPerformance;
  
  const components = displayHealth?.components || {};
  const healthyCount = Object.values(components).filter(c => c.status === 'healthy').length;
  const totalCount = Object.keys(components).length;
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>System Health</CardTitle>
            <StatusBadge status={displayHealth.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm">{displayHealth.message}</p>
            <p className="text-sm text-muted-foreground">
              {healthyCount} of {totalCount} modules healthy
            </p>
            <p className="text-xs text-muted-foreground">
              Last updated: {new Date(displayHealth.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="API Response Time (P95)"
          value={displayPerformance?.metrics?.api_response_time_p95 ?? 0}
          unit="ms"
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          status={displayPerformance?.metrics?.api_response_time_p95 && displayPerformance.metrics.api_response_time_p95 > 500 ? 'warning' : 'success'}
        />
        
        <MetricCard
          title="Request Rate"
          value={displayPerformance?.metrics?.request_rate ?? 0}
          unit="req/s"
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
        />
        
        <MetricCard
          title="Error Rate"
          value={displayPerformance?.metrics?.error_rate ? `${displayPerformance.metrics.error_rate.toFixed(2)}%` : '0%'}
          icon={<AlertTriangle className="h-4 w-4 text-muted-foreground" />}
          status={displayPerformance?.metrics && displayPerformance.metrics.error_rate > 5 ? 'error' : 'success'}
        />
        
        <MetricCard
          title="Uptime"
          value={displayPerformance?.metrics?.uptime_seconds ? Math.floor(displayPerformance.metrics.uptime_seconds / 3600) : 0}
          unit="hours"
          icon={<Clock className="h-4 w-4 text-muted-foreground" />}
        />
      </div>
    </div>
  );
}
