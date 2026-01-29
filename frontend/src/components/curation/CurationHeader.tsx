/**
 * Curation Header
 * 
 * Phase 9: Content Curation Dashboard
 * Header with title and batch actions
 */

import { BatchActionsDropdown } from './BatchActionsDropdown';
import { useCurationStore } from '@/stores/curationStore';

export function CurationHeader() {
  const { selectedIds } = useCurationStore();
  
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Content Curation</h1>
        <p className="text-muted-foreground">
          Review and improve content quality
        </p>
      </div>
      
      <div className="flex items-center gap-2">
        {selectedIds.size > 0 && (
          <span className="text-sm text-muted-foreground">
            {selectedIds.size} selected
          </span>
        )}
        <BatchActionsDropdown />
      </div>
    </div>
  );
}
