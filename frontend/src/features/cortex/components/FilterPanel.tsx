/**
 * Filter Panel Component
 * 
 * Panel for filtering graph nodes by type, date, and quality.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 10 Side Panel
 * Task: 10.3
 * 
 * Properties:
 * - Property 17: Filter Application
 * - Property 18: Filter Badge Count
 */

import { memo, useState } from 'react';
import { X, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

// ============================================================================
// Types
// ============================================================================

export interface GraphFilters {
  resourceTypes: string[];
  minQuality: number;
  dateRange: [Date, Date] | null;
}

interface FilterPanelProps {
  filters: GraphFilters;
  onFiltersChange: (filters: GraphFilters) => void;
  onClose: () => void;
}

// ============================================================================
// Constants
// ============================================================================

const RESOURCE_TYPES = [
  { value: 'paper', label: 'Papers', color: '#3B82F6' },
  { value: 'article', label: 'Articles', color: '#10B981' },
  { value: 'book', label: 'Books', color: '#8B5CF6' },
  { value: 'code', label: 'Code', color: '#F59E0B' },
];

// ============================================================================
// Component
// ============================================================================

export const FilterPanel = memo<FilterPanelProps>(({
  filters,
  onFiltersChange,
  onClose,
}) => {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleResourceTypeToggle = (type: string) => {
    const newTypes = localFilters.resourceTypes.includes(type)
      ? localFilters.resourceTypes.filter((t) => t !== type)
      : [...localFilters.resourceTypes, type];

    setLocalFilters({
      ...localFilters,
      resourceTypes: newTypes,
    });
  };

  const handleQualityChange = (value: number[]) => {
    setLocalFilters({
      ...localFilters,
      minQuality: value[0],
    });
  };

  const handleApply = () => {
    onFiltersChange(localFilters);
  };

  const handleClearAll = () => {
    const defaultFilters: GraphFilters = {
      resourceTypes: ['paper', 'article', 'book', 'code'],
      minQuality: 0,
      dateRange: null,
    };
    setLocalFilters(defaultFilters);
    onFiltersChange(defaultFilters);
  };

  // Property 18: Filter Badge Count
  const activeFilterCount = 
    (localFilters.resourceTypes.length < 4 ? 1 : 0) +
    (localFilters.minQuality > 0 ? 1 : 0) +
    (localFilters.dateRange ? 1 : 0);

  return (
    <div className="flex flex-col h-full bg-card border-l">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4" />
          <h3 className="font-semibold">Filters</h3>
          {activeFilterCount > 0 && (
            <span className="text-xs text-muted-foreground">
              ({activeFilterCount} active)
            </span>
          )}
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Resource Types */}
          <div>
            <h4 className="text-sm font-medium mb-3">Resource Type</h4>
            <div className="space-y-3">
              {RESOURCE_TYPES.map((type) => (
                <div key={type.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={type.value}
                    checked={localFilters.resourceTypes.includes(type.value)}
                    onCheckedChange={() => handleResourceTypeToggle(type.value)}
                  />
                  <Label
                    htmlFor={type.value}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: type.color }}
                    />
                    {type.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Quality Score */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium">Minimum Quality</h4>
              <span className="text-sm text-muted-foreground">
                {(localFilters.minQuality * 100).toFixed(0)}%
              </span>
            </div>
            <Slider
              value={[localFilters.minQuality]}
              onValueChange={handleQualityChange}
              min={0}
              max={1}
              step={0.1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          <Separator />

          {/* Date Range (Placeholder) */}
          <div>
            <h4 className="text-sm font-medium mb-3">Publication Date</h4>
            <p className="text-sm text-muted-foreground">
              Date range filter coming soon...
            </p>
          </div>
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t space-y-2">
        <Button
          variant="default"
          className="w-full"
          onClick={handleApply}
        >
          Apply Filters
        </Button>
        <Button
          variant="outline"
          className="w-full"
          onClick={handleClearAll}
        >
          Clear All
        </Button>
      </div>
    </div>
  );
});

FilterPanel.displayName = 'FilterPanel';
