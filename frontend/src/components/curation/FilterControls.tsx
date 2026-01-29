/**
 * Filter Controls
 * 
 * Phase 9: Content Curation Dashboard
 * Filters for review queue
 */

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useCurationStore } from '@/stores/curationStore';
import type { CurationStatus } from '@/types/curation';

export function FilterControls() {
  const { statusFilter, setStatusFilter } = useCurationStore();
  
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Status:</span>
        <Select
          value={statusFilter}
          onValueChange={(v) => setStatusFilter(v as CurationStatus | 'all')}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="assigned">Assigned</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
            <SelectItem value="flagged">Flagged</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
