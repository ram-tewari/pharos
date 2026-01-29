/**
 * Phase 5: Task Item Component
 */

import { useState } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { FileText, Code, ExternalLink, ChevronDown, ChevronRight, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Task } from '@/types/planner';

interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onRemove: () => void;
}

export function TaskItem({ task, onToggle, onRemove }: TaskItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getLinkIcon = (type: string) => {
    switch (type) {
      case 'doc':
        return <FileText className="h-3 w-3" />;
      case 'code':
        return <Code className="h-3 w-3" />;
      default:
        return <ExternalLink className="h-3 w-3" />;
    }
  };

  return (
    <div className={cn(
      'rounded-lg border bg-card p-4 transition-all',
      task.completed && 'opacity-60'
    )}>
      <div className="flex items-start gap-3">
        <Checkbox
          checked={task.completed}
          onCheckedChange={onToggle}
          className="mt-1"
        />
        
        <div className="flex-1 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className={cn(
              'font-medium flex-1',
              task.completed && 'line-through text-muted-foreground'
            )}>
              {task.title}
            </h3>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={onRemove}
                className="h-6 px-2 text-destructive hover:text-destructive"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
              {task.details.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="h-6 px-2"
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              )}
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground">{task.description}</p>
          
          {task.links.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {task.links.map((link) => (
                <a
                  key={link.id}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                >
                  {getLinkIcon(link.type)}
                  {link.label}
                </a>
              ))}
            </div>
          )}
          
          {isExpanded && task.details.length > 0 && (
            <div className="mt-4 space-y-3 border-t pt-3">
              <h4 className="text-sm font-medium">Implementation Steps:</h4>
              {task.details.map((detail) => (
                <div key={detail.id} className="space-y-1">
                  {detail.type === 'text' && (
                    <p className="text-sm text-muted-foreground">{detail.content}</p>
                  )}
                  {detail.type === 'command' && (
                    <div className="rounded bg-muted p-2 font-mono text-sm">
                      $ {detail.content}
                    </div>
                  )}
                  {detail.type === 'code' && (
                    <pre className="overflow-x-auto rounded bg-muted p-3 text-xs">
                      <code>{detail.content}</code>
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
