/**
 * Batch Actions Dropdown
 * 
 * Phase 9: Content Curation Dashboard
 * Dropdown menu for batch operations
 */

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown, Check, X, Flag, Tag, UserPlus, RefreshCw } from 'lucide-react';
import { useCurationStore } from '@/stores/curationStore';
import { useState } from 'react';
import { BatchConfirmDialog } from './BatchConfirmDialog';

export type BatchAction = 'approve' | 'reject' | 'flag' | 'tag' | 'assign' | 'recalculate';

export function BatchActionsDropdown() {
  const { selectedIds } = useCurationStore();
  const [action, setAction] = useState<BatchAction | null>(null);
  
  const handleAction = (newAction: BatchAction) => {
    setAction(newAction);
  };
  
  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" disabled={selectedIds.size === 0}>
            Batch Actions
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => handleAction('approve')}>
            <Check className="mr-2 h-4 w-4" />
            Approve
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction('reject')}>
            <X className="mr-2 h-4 w-4" />
            Reject
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction('flag')}>
            <Flag className="mr-2 h-4 w-4" />
            Flag for Review
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction('tag')}>
            <Tag className="mr-2 h-4 w-4" />
            Add Tags
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction('assign')}>
            <UserPlus className="mr-2 h-4 w-4" />
            Assign Curator
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction('recalculate')}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Recalculate Quality
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      
      {action && (
        <BatchConfirmDialog
          open={!!action}
          action={action}
          count={selectedIds.size}
          onClose={() => setAction(null)}
        />
      )}
    </>
  );
}
