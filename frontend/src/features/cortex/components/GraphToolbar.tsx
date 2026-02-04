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
    <nav 
      className="flex flex-wrap items-center gap-2 md:gap-4 p-2 md:p-4 bg-card border-b shadow-sm transition-shadow duration-200"
      role="navigation"
      aria-label="Graph visualization controls"
    >
      {/* Mode Selector - Full width on mobile, auto on desktop */}
      <div role="group" aria-label="View mode selection" className="w-full md:w-auto">
        <Select value={viewMode} onValueChange={(v) => onViewModeChange(v as VisualizationMode)}>
          <SelectTrigger 
            className="w-full md:w-[200px] min-h-[44px]"
            aria-label="Select visualization mode"
          >
            <SelectValue placeholder="Select view mode" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={VisualizationMode.CityMap}>City Map</SelectItem>
            <SelectItem value={VisualizationMode.BlastRadius}>Blast Radius</SelectItem>
            <SelectItem value={VisualizationMode.DependencyWaterfall}>Dependency Waterfall</SelectItem>
            <SelectItem value={VisualizationMode.Hypothesis}>Hypothesis</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Search Bar - Full width on mobile, flex-1 on desktop */}
      <div className="relative flex-1 w-full md:max-w-md" role="search">
        <Search 
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" 
          aria-hidden="true"
        />
        <Input
          type="search"
          placeholder="Search resources, entities, or tags..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 min-h-[44px]"
          aria-label="Search graph nodes"
        />
      </div>

      {/* Spacer - Hidden on mobile */}
      <div className="hidden md:flex md:flex-1" />

      {/* Zoom Controls - Compact on mobile */}
      <div 
        className="flex items-center gap-1 md:gap-2"
        role="group"
        aria-label="Zoom controls"
      >
        <Button
          variant="outline"
          size="icon"
          onClick={onZoomOut}
          title="Zoom out"
          aria-label="Zoom out (keyboard shortcut: minus key)"
          className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
        >
          <ZoomOut className="w-4 h-4" aria-hidden="true" />
        </Button>
        <span 
          className="text-xs md:text-sm text-muted-foreground min-w-[40px] md:min-w-[50px] text-center"
          aria-live="polite"
          aria-label={`Current zoom level: ${Math.round(zoom * 100)} percent`}
        >
          {Math.round(zoom * 100)}%
        </span>
        <Button
          variant="outline"
          size="icon"
          onClick={onZoomIn}
          title="Zoom in"
          aria-label="Zoom in (keyboard shortcut: plus key)"
          className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
        >
          <ZoomIn className="w-4 h-4" aria-hidden="true" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={onFitView}
          title="Fit to screen"
          aria-label="Fit graph to screen (keyboard shortcut: 0 key)"
          className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
        >
          <Maximize className="w-4 h-4" aria-hidden="true" />
        </Button>
      </div>

      {/* Export Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={onExport}
        title="Export graph"
        aria-label="Export graph as image"
        className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
      >
        <Download className="w-4 h-4" aria-hidden="true" />
      </Button>

      {/* Indicator Toggle (Hypothesis Mode Only) */}
      {viewMode === VisualizationMode.Hypothesis && onToggleIndicators && (
        <Button
          variant="outline"
          size="icon"
          onClick={onToggleIndicators}
          title={showIndicators ? "Hide indicators" : "Show indicators"}
          aria-label={showIndicators ? "Hide hypothesis indicators" : "Show hypothesis indicators"}
          aria-pressed={showIndicators}
          className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
        >
          {showIndicators ? (
            <Eye className="w-4 h-4" aria-hidden="true" />
          ) : (
            <EyeOff className="w-4 h-4" aria-hidden="true" />
          )}
        </Button>
      )}

      {/* Filter Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={onToggleFilters}
        title="Toggle filters"
        aria-label={`Toggle filter panel${activeFilterCount > 0 ? ` (${activeFilterCount} active filters)` : ''}`}
        className="relative min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95"
      >
        <Filter className="w-4 h-4" aria-hidden="true" />
        {activeFilterCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs animate-in zoom-in-50 duration-200"
            aria-label={`${activeFilterCount} active filters`}
          >
            {activeFilterCount}
          </Badge>
        )}
      </Button>
    </nav>
  );
});

GraphToolbar.displayName = 'GraphToolbar';
