/**
 * Review Queue Table
 * 
 * Phase 9: Content Curation Dashboard
 * Table displaying review queue items with selection
 */

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { QualityScoreBadge } from './QualityScoreBadge';
import { StatusBadge } from './StatusBadge';
import { QualityAnalysisModal } from './QualityAnalysisModal';
import { useCurationStore } from '@/stores/curationStore';
import { formatDistanceToNow } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import type { ReviewQueueItem } from '@/types/curation';

interface ReviewQueueTableProps {
  data: ReviewQueueItem[];
  total: number;
}

export function ReviewQueueTable({ data, total }: ReviewQueueTableProps) {
  const {
    selectedIds,
    toggleSelection,
    selectAll,
    clearSelection,
    currentPage,
    pageSize,
    setCurrentPage,
  } = useCurationStore();
  
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);
  
  const allSelected = data.length > 0 && data.every((item) => selectedIds.has(item.resource_id));
  const totalPages = Math.ceil(total / pageSize);
  
  const handleSelectAll = () => {
    if (allSelected) {
      clearSelection();
    } else {
      selectAll(data.map((item) => item.resource_id));
    }
  };
  
  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">
              <Checkbox checked={allSelected} onCheckedChange={handleSelectAll} />
            </TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Quality</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Assigned</TableHead>
            <TableHead>Updated</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow
              key={item.resource_id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={(e) => {
                // Don't open modal if clicking checkbox
                if ((e.target as HTMLElement).closest('button')) return;
                setSelectedResourceId(item.resource_id);
              }}
            >
              <TableCell onClick={(e) => e.stopPropagation()}>
                <Checkbox
                  checked={selectedIds.has(item.resource_id)}
                  onCheckedChange={() => toggleSelection(item.resource_id)}
                />
              </TableCell>
              <TableCell className="font-medium">{item.title}</TableCell>
              <TableCell className="capitalize">{item.resource_type}</TableCell>
              <TableCell>
                <QualityScoreBadge score={item.quality_score} />
              </TableCell>
              <TableCell>
                <StatusBadge status={item.status} />
              </TableCell>
              <TableCell>{item.assigned_to || '-'}</TableCell>
              <TableCell className="text-muted-foreground">
                {formatDistanceToNow(new Date(item.last_updated), { addSuffix: true })}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t p-4">
          <div className="text-sm text-muted-foreground">
            Page {currentPage + 1} of {totalPages} ({total} total)
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= totalPages - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
      
      <QualityAnalysisModal
        resourceId={selectedResourceId}
        open={!!selectedResourceId}
        onClose={() => setSelectedResourceId(null)}
      />
    </div>
  );
}
