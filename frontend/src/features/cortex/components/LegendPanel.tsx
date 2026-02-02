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
      <div className="absolute bottom-4 right-4 bg-card border rounded-lg shadow-lg">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(true)}
          className="gap-2"
        >
          <Info className="w-4 h-4" />
          Legend
          <ChevronUp className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="absolute bottom-4 right-4 bg-card border rounded-lg shadow-lg p-4 w-64">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4" />
          <h4 className="font-semibold text-sm">Legend</h4>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsExpanded(false)}
          className="h-6 w-6"
        >
          <ChevronDown className="w-4 h-4" />
        </Button>
      </div>

      {/* Node Colors */}
      <div className="space-y-2 mb-3">
        <p className="text-xs font-medium text-muted-foreground">Resource Types</p>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#3B82F6]" />
            <span>Papers</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#10B981]" />
            <span>Articles</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#8B5CF6]" />
            <span>Books</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
            <span>Code</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Entity Types */}
      <div className="space-y-2 mb-3">
        <p className="text-xs font-medium text-muted-foreground">Entity Types</p>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rotate-45 bg-[#EC4899]" />
            <span>People</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rotate-45 bg-[#6366F1]" />
            <span>Concepts</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rotate-45 bg-[#14B8A6]" />
            <span>Organizations</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rotate-45 bg-[#F97316]" />
            <span>Locations</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Edge Types */}
      <div className="space-y-2 mb-3">
        <p className="text-xs font-medium text-muted-foreground">Relationships</p>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-6 h-0.5 bg-[#6B7280]" />
            <span>Citation</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-6 h-0.5 bg-[#3B82F6]" />
            <span>Semantic</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-6 h-0.5 bg-[#8B5CF6]" />
            <span>Entity</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-6 h-0.5 bg-[#10B981] border-dashed border-t-2 border-[#10B981]" />
            <span>Hidden</span>
          </div>
        </div>
      </div>

      <Separator className="my-3" />

      {/* Quality Scores */}
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground">Quality Score</p>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#10B981]" />
            <span>High (&gt;80%)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
            <span>Medium (50-80%)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
            <span>Low (&lt;50%)</span>
          </div>
        </div>
      </div>
    </div>
  );
});

LegendPanel.displayName = 'LegendPanel';
