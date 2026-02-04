/**
 * Panel Skeleton Component
 * 
 * Loading skeleton for side panels with shimmer animation.
 * 
 * Phase: 4 Cortex/Knowledge Graph
 * Priority: 3 Batch 4 - Error Handling
 */

import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface PanelSkeletonProps {
  className?: string;
  lines?: number;
}

// ============================================================================
// Component
// ============================================================================

export function PanelSkeleton({ className, lines = 5 }: PanelSkeletonProps) {
  return (
    <div className={cn('space-y-4 p-4', className)}>
      {/* Shimmer overlay */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-muted/30 to-transparent" />
      </div>
      
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-6 w-3/4 bg-muted rounded animate-pulse" />
        <div className="h-4 w-1/2 bg-muted rounded animate-pulse" />
      </div>
      
      {/* Content skeleton */}
      <div className="space-y-3">
        {[...Array(lines)].map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-full bg-muted rounded animate-pulse" />
            <div className="h-4 w-5/6 bg-muted rounded animate-pulse" />
          </div>
        ))}
      </div>
      
      {/* Button skeleton */}
      <div className="pt-4">
        <div className="h-10 w-full bg-muted rounded animate-pulse" />
      </div>
    </div>
  );
}
