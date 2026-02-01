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
  if (!health) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-muted-foreground">Loading health data...</p>
        </CardContent>
      </Card>
    );
  }
  
  const healthyCount = Object.values(health?.modules || {}).filter(m => m.status === 'healthy').length;
  const totalCount = Object.keys(health?.modules || {}).length;
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>System Health</CardTitle>
            <StatusBadge status={health.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              {healthyCount} of {totalCount} modules healthy
            </p>
            <p className="text-xs text-muted-foreground">
              Last updated: {new Date(health.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="API Response Time (P95)"
          value={performance?.api_response_time?.p95 ?? '-'}
          unit="ms"
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          status={performance?.api_response_time?.p95 && performance.api_response_time.p95 > 500 ? 'warning' : 'success'}
        />
        
        <MetricCard
          title="Request Rate"
          value={performance?.request_rate ?? '-'}
          unit="req/s"
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
        />
        
        <MetricCard
          title="Error Rate"
          value={performance?.error_rate ? `${performance.error_rate.toFixed(2)}%` : '-'}
          icon={<AlertTriangle className="h-4 w-4 text-muted-foreground" />}
          status={performance && performance.error_rate > 5 ? 'error' : 'success'}
        />
        
        <MetricCard
          title="Uptime"
          value={performance?.uptime_seconds ? Math.floor(performance.uptime_seconds / 3600) : '-'}
          unit="hours"
          icon={<Clock className="h-4 w-4 text-muted-foreground" />}
        />
      </div>
    </div>
  );
}
