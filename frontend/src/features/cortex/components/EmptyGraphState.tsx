/**
 * Empty Graph State Component
 * 
 * Friendly empty state for when no graph data is available.
 * 
 * Phase: 4 Cortex/Knowledge Graph
 * Priority: 3 Batch 4 - Error Handling
 */

import { Network, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface EmptyGraphStateProps {
  title?: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: 'network' | 'search' | 'filter';
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function EmptyGraphState({
  title = 'No graph data available',
  message = 'Start by adding resources to your library or adjusting your filters.',
  action,
  icon = 'network',
  className,
}: EmptyGraphStateProps) {
  const IconComponent = {
    network: Network,
    search: Search,
    filter: Filter,
  }[icon];

  return (
    <div className={cn(
      'flex flex-col items-center justify-center h-full p-8 text-center',
      className
    )}>
      {/* Icon */}
      <div className="mb-6 relative">
        <div className="absolute inset-0 bg-primary/10 rounded-full blur-2xl" />
        <IconComponent className="relative w-24 h-24 text-muted-foreground/50" />
      </div>
      
      {/* Title */}
      <h3 className="text-lg font-semibold mb-2">
        {title}
      </h3>
      
      {/* Message */}
      <p className="text-muted-foreground mb-6 max-w-md">
        {message}
      </p>
      
      {/* Action button */}
      {action && (
        <Button onClick={action.onClick} variant="default">
          {action.label}
        </Button>
      )}
    </div>
  );
}
