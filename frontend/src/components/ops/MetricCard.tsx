/**
 * Metric Card
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Reusable metric display card
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  status?: 'success' | 'warning' | 'error';
  hasAnomaly?: boolean;
  anomalyMessage?: string;
}

export function MetricCard({
  title,
  value,
  unit,
  trend,
  trendValue,
  icon,
  status,
  hasAnomaly,
  anomalyMessage,
}: MetricCardProps) {
  const statusColors = {
    success: 'text-[hsl(var(--success))]',
    warning: 'text-[hsl(var(--warning))]',
    error: 'text-destructive',
  };
  
  return (
    <Card hover className="transition-all duration-200">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div className="text-muted-foreground">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <div className={cn("text-3xl font-bold transition-colors", status && statusColors[status])}>
            {value}
            {unit && <span className="text-sm font-normal text-muted-foreground ml-1">{unit}</span>}
          </div>
          
          {hasAnomaly && (
            <AlertCircle className="h-4 w-4 text-[hsl(var(--warning))] animate-pulse-subtle" title={anomalyMessage} />
          )}
        </div>
        
        {trendValue && (
          <div className="flex items-center gap-1 mt-2">
            {trend === 'up' && <TrendingUp className="h-3 w-3 text-[hsl(var(--success))]" />}
            {trend === 'down' && <TrendingDown className="h-3 w-3 text-destructive" />}
            <p className={cn(
              "text-xs font-medium",
              trend === 'up' && "text-[hsl(var(--success))]",
              trend === 'down' && "text-destructive",
              trend === 'neutral' && "text-muted-foreground"
            )}>
              {trendValue}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
