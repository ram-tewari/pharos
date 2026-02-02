/**
 * Graph Toolbar Component
 * 
 * Toolbar with controls for mode selection, search, zoom, and export.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 9 Graph Toolbar
 * Task: 9.1-9.8
 */

import { memo } from 'react';
import { Search, ZoomIn, ZoomOut, Maximize, Download, Filter, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { VisualizationMode } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

interface GraphToolbarProps {
  viewMode: VisualizationMode;
  onViewModeChange: (mode: VisualizationMode) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onExport: () => void;
  onToggleFilters: () => void;
  activeFilterCount: number;
  showIndicators?: boolean;
  onToggleIndicators?: () => void;
}

// ============================================================================
// Component
// ============================================================================

export const GraphToolbar = memo<GraphToolbarProps>(({
  viewMode,
  onViewModeChange,
  searchQuery,
  onSearchChange,
  zoom,
  onZoomIn,
  onZoomOut,
  onFitView,
  onExport,
  onToggleFilters,
  activeFilterCount,
  showIndicators = true,
  onToggleIndicators,
}) => {
  return (
    <div className="flex items-center gap-4 p-4 bg-card border-b">
      {/* Mode Selector */}
      <Select value={viewMode} onValueChange={(v) => onViewModeChange(v as VisualizationMode)}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select view mode" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={VisualizationMode.CityMap}>City Map</SelectItem>
          <SelectItem value={VisualizationMode.BlastRadius}>Blast Radius</SelectItem>
          <SelectItem value={VisualizationMode.DependencyWaterfall}>Dependency Waterfall</SelectItem>
          <SelectItem value={VisualizationMode.Hypothesis}>Hypothesis</SelectItem>
        </SelectContent>
      </Select>

      {/* Search Bar */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search resources, entities, or tags..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Zoom Controls */}
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={onZoomOut}
          title="Zoom out (-)"
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <span className="text-sm text-muted-foreground min-w-[50px] text-center">
          {Math.round(zoom * 100)}%
        </span>
        <Button
          variant="outline"
          size="icon"
          onClick={onZoomIn}
          title="Zoom in (+)"
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={onFitView}
          title="Fit to screen (0)"
        >
          <Maximize className="w-4 h-4" />
        </Button>
      </div>

      {/* Export Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={onExport}
        title="Export graph"
      >
        <Download className="w-4 h-4" />
      </Button>

      {/* Indicator Toggle (Hypothesis Mode Only) */}
      {viewMode === VisualizationMode.Hypothesis && onToggleIndicators && (
        <Button
          variant="outline"
          size="icon"
          onClick={onToggleIndicators}
          title={showIndicators ? "Hide indicators" : "Show indicators"}
        >
          {showIndicators ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
        </Button>
      )}

      {/* Filter Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={onToggleFilters}
        title="Toggle filters"
        className="relative"
      >
        <Filter className="w-4 h-4" />
        {activeFilterCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
          >
            {activeFilterCount}
          </Badge>
        )}
      </Button>
    </div>
  );
});

GraphToolbar.displayName = 'GraphToolbar';
