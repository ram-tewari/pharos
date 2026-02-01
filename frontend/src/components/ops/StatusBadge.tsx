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
  const config = {
    healthy: {
      variant: 'success' as const,
      icon: <CheckCircle2 className="h-3 w-3" />,
      label: 'Healthy',
    },
    degraded: {
      variant: 'warning' as const,
      icon: <AlertTriangle className="h-3 w-3" />,
      label: 'Degraded',
    },
    down: {
      variant: 'destructive' as const,
      icon: <XCircle className="h-3 w-3" />,
      label: 'Down',
    },
  };
  
  const statusConfig = config[status] || config.degraded; // Fallback to degraded if status is unknown
  const { variant, icon, label } = statusConfig;
  
  return (
    <Badge variant={variant} className={className}>
      {showIcon && icon}
      {label}
    </Badge>
  );
}
