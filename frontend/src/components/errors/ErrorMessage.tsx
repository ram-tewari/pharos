/**
 * ErrorMessage - Inline error message component
 */
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ClassifiedError } from '@/lib/errors';
import { formatError } from '@/lib/errors';

export interface ErrorMessageProps {
  error: ClassifiedError;
  className?: string;
  showIcon?: boolean;
  compact?: boolean;
}

export function ErrorMessage({ 
  error, 
  className, 
  showIcon = true,
  compact = false 
}: ErrorMessageProps) {
  const formatted = formatError(error);

  const getSeverityIcon = () => {
    switch (error.severity) {
      case 'low':
        return <Info className="h-4 w-4" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />;
      case 'high':
        return <AlertCircle className="h-4 w-4" />;
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getSeverityStyles = () => {
    switch (error.severity) {
      case 'low':
        return 'bg-[hsl(var(--info))]/10 border-[hsl(var(--info))]/50 text-[hsl(var(--info))]';
      case 'medium':
        return 'bg-[hsl(var(--warning))]/10 border-[hsl(var(--warning))]/50 text-[hsl(var(--warning))]';
      case 'high':
        return 'bg-destructive/10 border-destructive/50 text-destructive';
      case 'critical':
        return 'bg-destructive/20 border-destructive text-destructive animate-shake';
      default:
        return 'bg-muted border-border text-foreground';
    }
  };

  if (compact) {
    return (
      <div
        role="alert"
        className={cn(
          'flex items-center gap-2 text-sm transition-all duration-200',
          getSeverityStyles(),
          className
        )}
      >
        {showIcon && getSeverityIcon()}
        <span>{formatted.message}</span>
      </div>
    );
  }

  return (
    <div
      role="alert"
      className={cn(
        'rounded-lg border p-4 shadow-sm transition-all duration-200',
        getSeverityStyles(),
        className
      )}
    >
      <div className="flex items-start gap-3">
        {showIcon && (
          <div className="flex-shrink-0 mt-0.5">
            {getSeverityIcon()}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm mb-1">{formatted.title}</h3>
          <p className="text-sm opacity-90 leading-relaxed">{formatted.message}</p>
        </div>
      </div>
    </div>
  );
}
