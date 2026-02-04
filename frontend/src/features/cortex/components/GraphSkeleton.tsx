/**
 * Graph Skeleton Component
 * 
 * Loading skeleton for graph visualization with shimmer animation.
 * 
 * Phase: 4 Cortex/Knowledge Graph
 * Priority: 3 Batch 4 - Error Handling
 */

import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface GraphSkeletonProps {
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function GraphSkeleton({ className }: GraphSkeletonProps) {
  return (
    <div className={cn('relative w-full h-full bg-background', className)}>
      {/* Shimmer overlay */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-muted/50 to-transparent" />
      </div>
      
      {/* Fake nodes */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-full h-full max-w-4xl max-h-4xl">
          {/* Center node */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="w-20 h-20 rounded-full bg-muted animate-pulse" />
          </div>
          
          {/* Surrounding nodes */}
          {[...Array(8)].map((_, i) => {
            const angle = (i * Math.PI * 2) / 8;
            const radius = 150;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            
            return (
              <div
                key={i}
                className="absolute top-1/2 left-1/2"
                style={{
                  transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                }}
              >
                <div className="w-16 h-16 rounded-full bg-muted animate-pulse" />
              </div>
            );
          })}
          
          {/* Fake edges */}
          {[...Array(8)].map((_, i) => {
            const angle = (i * Math.PI * 2) / 8;
            const length = 150;
            
            return (
              <div
                key={`edge-${i}`}
                className="absolute top-1/2 left-1/2 origin-left"
                style={{
                  width: `${length}px`,
                  height: '2px',
                  transform: `rotate(${angle}rad)`,
                }}
              >
                <div className="w-full h-full bg-muted/50 animate-pulse" />
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Loading text */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-current animate-bounce" />
          <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:0.2s]" />
          <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:0.4s]" />
          <span className="ml-2 text-sm">Loading graph...</span>
        </div>
      </div>
    </div>
  );
}
