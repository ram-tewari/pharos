/**
 * Empty Panel State Component
 * 
 * Friendly empty state for side panels.
 * 
 * Phase: 4 Cortex/Knowledge Graph
 * Priority: 3 Batch 4 - Error Handling
 */

import { FileQuestion, Lightbulb, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface EmptyPanelStateProps {
  title: string;
  message: string;
  icon?: 'question' | 'lightbulb' | 'info';
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function EmptyPanelState({
  title,
  message,
  icon = 'info',
  className,
}: EmptyPanelStateProps) {
  const IconComponent = {
    question: FileQuestion,
    lightbulb: Lightbulb,
    info: Info,
  }[icon];

  return (
    <div className={cn(
      'flex flex-col items-center justify-center p-8 text-center',
      className
    )}>
      {/* Icon */}
      <IconComponent className="w-16 h-16 text-muted-foreground/50 mb-4" />
      
      {/* Title */}
      <h4 className="text-base font-medium mb-2">
        {title}
      </h4>
      
      {/* Message */}
      <p className="text-sm text-muted-foreground max-w-xs">
        {message}
      </p>
    </div>
  );
}
