/**
 * Phase 5: Progress Bar Component
 */

import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  completed: number;
  total: number;
  className?: string;
}

export function ProgressBar({ completed, total, className }: ProgressBarProps) {
  const percentage = total > 0 ? (completed / total) * 100 : 0;
  const isComplete = completed === total && total > 0;
  
  // Color based on progress
  const getProgressColor = () => {
    if (isComplete) return 'bg-green-500';
    if (percentage >= 67) return 'bg-green-500';
    if (percentage >= 34) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">
          {isComplete ? '🎉 Completed!' : 'Progress'}
        </span>
        <span className={cn(
          'text-muted-foreground',
          isComplete && 'text-green-600 dark:text-green-400 font-semibold'
        )}>
          {completed} of {total} tasks complete
        </span>
      </div>
      <Progress value={percentage} className="h-2" indicatorClassName={getProgressColor()} />
      <div className={cn(
        'text-right text-sm font-medium',
        isComplete && 'text-green-600 dark:text-green-400'
      )}>
        {isComplete ? '✓ 100% Complete!' : `${Math.round(percentage)}%`}
      </div>
    </div>
  );
}
