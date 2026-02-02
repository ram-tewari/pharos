/**
 * Status Badge
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Color-coded status indicator
 */

import { Badge } from '@/components/ui/badge';
import type { HealthStatus } from '@/types/monitoring';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: HealthStatus;
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const config: Record<string, { variant: 'success' | 'warning' | 'destructive' | 'default'; icon: JSX.Element; label: string }> = {
    healthy: {
      variant: 'success',
      icon: <CheckCircle2 className="h-3 w-3" />,
      label: 'Healthy',
    },
    degraded: {
      variant: 'warning',
      icon: <AlertTriangle className="h-3 w-3" />,
      label: 'Degraded',
    },
    unhealthy: {
      variant: 'destructive',
      icon: <XCircle className="h-3 w-3" />,
      label: 'Unhealthy',
    },
    down: {
      variant: 'destructive',
      icon: <XCircle className="h-3 w-3" />,
      label: 'Down',
    },
    available: {
      variant: 'success',
      icon: <CheckCircle2 className="h-3 w-3" />,
      label: 'Available',
    },
    unavailable: {
      variant: 'warning',
      icon: <AlertTriangle className="h-3 w-3" />,
      label: 'Unavailable',
    },
    ok: {
      variant: 'success',
      icon: <CheckCircle2 className="h-3 w-3" />,
      label: 'OK',
    },
    error: {
      variant: 'destructive',
      icon: <XCircle className="h-3 w-3" />,
      label: 'Error',
    },
    unknown: {
      variant: 'default',
      icon: <AlertTriangle className="h-3 w-3" />,
      label: 'Unknown',
    },
  };
  
  // Normalize status to lowercase and handle undefined/null
  const normalizedStatus = (status || 'unknown').toString().toLowerCase();
  const statusConfig = config[normalizedStatus] || config.unknown;
  const { variant, icon, label } = statusConfig;
  
  return (
    <Badge variant={variant} className={className}>
      {showIcon && icon}
      {label}
    </Badge>
  );
}
