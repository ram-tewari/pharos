/**
 * Legend Panel Component
 * 
 * Displays legend for node colors, edge styles, and icons.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 10 Side Panel
 * Task: 10.7
 */

import { memo, useState } from 'react';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

// ============================================================================
// Component
// ============================================================================

export const LegendPanel = memo(() => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!isExpanded) {
    return (
      <aside 
        className="absolute bottom-2 right-2 md:bottom-4 md:right-4 bg-card/95 backdrop-blur-sm border rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl"
        role="complementary"
        aria-label="Graph legend"
      >
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(true)}
          className="gap-2 min-h-[44px] transition-all duration-200 hover:scale-105 active:scale-95"
          aria-label="Expand legend panel"
          aria-expanded={false}
        >
          <Info className="w-4 h-4" aria-hidden="true" />
          <span className="hidden sm:inline">Legend</span>
          <ChevronUp className="w-4 h-4" aria-hidden="true" />
        </Button>
      </aside>
    );
  }

  return (
    <aside 
      className="absolute bottom-2 right-2 md:bottom-4 md:right-4 bg-card/95 backdrop-blur-sm border rounded-lg shadow-xl p-3 md:p-4 w-56 md:w-64 max-h-[80vh] overflow-y-auto transition-all duration-300 animate-in slide-in-from-bottom-4"
      role="complementary"
      aria-label="Graph legend"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4" aria-hidden="true" />
          <h4 className="font-semibold text-xs md:text-sm">Legend</h4>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsExpanded(false)}
          className="h-8 w-8 min-h-[44px] min-w-[44px] md:h-6 md:w-6 md:min-h-0 md:min-w-0 transition-all duration-200 hover:scale-110 hover:bg-accent active:scale-95"
          aria-label="Collapse legend panel"
          aria-expanded={true}
        >
          <ChevronDown className="w-4 h-4" aria-hidden="true" />
        </Button>
      </div>

      {/* Node Colors */}
      <div className="space-y-2 mb-3" role="group" aria-labelledby="resource-types-heading">
        <p id="resource-types-heading" className="text-xs font-medium text-muted-foreground">Resource Types</p>
        <div className="space-y-1.5" role="list">
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#3B82F6]" aria-hidden="true" />
            <span>Papers</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#10B981]" aria-hidden="true" />
            <span>Articles</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#8B5CF6]" aria-hidden="true" />
            <span>Books</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#F59E0B]" aria-hidden="true" />
            <span>Code</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Entity Types */}
      <div className="space-y-2 mb-3" role="group" aria-labelledby="entity-types-heading">
        <p id="entity-types-heading" className="text-xs font-medium text-muted-foreground">Entity Types</p>
        <div className="space-y-1.5" role="list">
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rotate-45 bg-[#EC4899]" aria-hidden="true" />
            <span>People</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rotate-45 bg-[#6366F1]" aria-hidden="true" />
            <span>Concepts</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rotate-45 bg-[#14B8A6]" aria-hidden="true" />
            <span>Organizations</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rotate-45 bg-[#F97316]" aria-hidden="true" />
            <span>Locations</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Edge Types */}
      <div className="space-y-2 mb-3" role="group" aria-labelledby="relationships-heading">
        <p id="relationships-heading" className="text-xs font-medium text-muted-foreground">Relationships</p>
        <div className="space-y-1.5" role="list">
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-6 h-0.5 bg-[#6B7280]" aria-hidden="true" />
            <span>Citation</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-6 h-0.5 bg-[#3B82F6]" aria-hidden="true" />
            <span>Semantic</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-6 h-0.5 bg-[#8B5CF6]" aria-hidden="true" />
            <span>Entity</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-6 h-0.5 bg-[#10B981] border-dashed border-t-2 border-[#10B981]" aria-hidden="true" />
            <span>Hidden</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Quality Scores */}
      <div className="space-y-2" role="group" aria-labelledby="quality-score-heading">
        <p id="quality-score-heading" className="text-xs font-medium text-muted-foreground">Quality Score</p>
        <div className="space-y-1.5" role="list">
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#10B981]" aria-hidden="true" />
            <span>High (&gt;80%)</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#F59E0B]" aria-hidden="true" />
            <span>Medium (50-80%)</span>
          </div>
          <div className="flex items-center gap-2 text-xs" role="listitem">
            <div className="w-3 h-3 rounded-full bg-[#EF4444]" aria-hidden="true" />
            <span>Low (&lt;50%)</span>
          </div>
        </div>
      </div>
    </div>
  );
});

LegendPanel.displayName = 'LegendPanel';
