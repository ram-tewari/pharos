/**
 * Low Quality View
 * 
 * Phase 9: Content Curation Dashboard
 * View for low-quality resources with threshold slider
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';
import { ReviewQueueTable } from './ReviewQueueTable';
import { useLowQualityResources } from '@/lib/hooks/useCuration';
import { useCurationStore } from '@/stores/curationStore';

export function LowQualityView() {
  const { qualityThreshold, setQualityThreshold, currentPage, pageSize } = useCurationStore();
  
  const { data, isLoading } = useLowQualityResources(
    qualityThreshold,
    pageSize,
    currentPage * pageSize
  );
  
  const handleExport = () => {
    if (!data?.items) return;
    
    const csv = [
      ['Title', 'Type', 'Quality Score', 'Status', 'Last Updated'].join(','),
      ...data.items.map((item) =>
        [
          `"${item.title}"`,
          item.resource_type,
          item.quality_score,
          item.status,
          item.last_updated,
        ].join(',')
      ),
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `low-quality-resources-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Quality Threshold</CardTitle>
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Threshold:</span>
              <Slider
                value={[qualityThreshold]}
                onValueChange={([value]) => setQualityThreshold(value)}
                min={0}
                max={1}
                step={0.05}
                className="flex-1"
              />
              <span className="text-sm font-medium w-12">{qualityThreshold.toFixed(2)}</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Showing resources with quality score below {qualityThreshold.toFixed(2)}
            </p>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 text-center text-muted-foreground">
              Loading low-quality resources...
            </div>
          ) : data?.items && data.items.length > 0 ? (
            <ReviewQueueTable data={data.items} total={data.total} />
          ) : (
            <div className="p-6 text-center text-muted-foreground">
              No low-quality resources found
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
