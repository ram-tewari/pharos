/**
 * Review Queue View
 * 
 * Phase 9: Content Curation Dashboard
 * Main review queue with table and filters
 */

import { Card, CardContent } from '@/components/ui/card';
import { ReviewQueueTable } from './ReviewQueueTable';
import { FilterControls } from './FilterControls';
import { useReviewQueue } from '@/lib/hooks/useCuration';
import { useCurationStore } from '@/stores/curationStore';

export function ReviewQueueView() {
  const {
    statusFilter,
    minQuality,
    maxQuality,
    assignedToFilter,
    currentPage,
    pageSize,
  } = useCurationStore();
  
  const { data, isLoading, error } = useReviewQueue({
    status: statusFilter !== 'all' ? statusFilter : undefined,
    min_quality: minQuality,
    max_quality: maxQuality,
    assigned_to: assignedToFilter || undefined,
    limit: pageSize,
    offset: currentPage * pageSize,
  });
  
  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-destructive">Failed to load review queue</p>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className="space-y-4">
      <FilterControls />
      
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 text-center text-muted-foreground">
              Loading review queue...
            </div>
          ) : data?.items && data.items.length > 0 ? (
            <ReviewQueueTable data={data.items} total={data.total} />
          ) : (
            <div className="p-6 text-center text-muted-foreground">
              No resources in review queue
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
