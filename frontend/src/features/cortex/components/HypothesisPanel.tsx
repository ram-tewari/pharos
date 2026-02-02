/**
 * Hypothesis Panel Component
 * 
 * Side panel for displaying discovered hypotheses from Literature-Based Discovery.
 * Shows ranked list with confidence scores, evidence, and indicators.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 10 Side Panels
 * Task: 10.5
 */

import { memo, useState } from 'react';
import { X, Lightbulb, AlertTriangle, HelpCircle, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Hypothesis } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

interface HypothesisPanelProps {
  hypotheses: Hypothesis[];
  onHypothesisClick: (hypothesis: Hypothesis) => void;
  onDiscoverNew: () => void;
  onClose: () => void;
}

// ============================================================================
// Component
// ============================================================================

export const HypothesisPanel = memo<HypothesisPanelProps>(({
  hypotheses,
  onHypothesisClick,
  onDiscoverNew,
  onClose,
}) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleHypothesisClick = (hypothesis: Hypothesis) => {
    setSelectedId(hypothesis.id);
    onHypothesisClick(hypothesis);
  };

  return (
    <div className="h-full flex flex-col bg-background border-l">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Hypotheses</h2>
          <Badge variant="secondary">{hypotheses.length}</Badge>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          aria-label="Close hypothesis panel"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Discover Button */}
      <div className="p-4 border-b">
        <Button
          onClick={onDiscoverNew}
          className="w-full"
          variant="default"
        >
          <Lightbulb className="h-4 w-4 mr-2" />
          Discover New Hypotheses
        </Button>
      </div>

      {/* Hypotheses List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {hypotheses.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Lightbulb className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No hypotheses discovered yet</p>
              <p className="text-xs mt-1">Click "Discover New" to start</p>
            </div>
          ) : (
            hypotheses.map((hypothesis) => (
              <HypothesisCard
                key={hypothesis.id}
                hypothesis={hypothesis}
                isSelected={selectedId === hypothesis.id}
                onClick={() => handleHypothesisClick(hypothesis)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
});

HypothesisPanel.displayName = 'HypothesisPanel';

// ============================================================================
// Hypothesis Card Component
// ============================================================================

interface HypothesisCardProps {
  hypothesis: Hypothesis;
  isSelected: boolean;
  onClick: () => void;
}

const HypothesisCard = memo<HypothesisCardProps>(({
  hypothesis,
  isSelected,
  onClick,
}) => {
  const hasContradiction = hypothesis.metadata?.hasContradiction;
  const hasResearchGap = hypothesis.metadata?.hasResearchGap;
  const evidenceStrength = hypothesis.confidence * 100;

  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left p-3 rounded-lg border transition-all
        hover:border-primary hover:shadow-sm
        ${isSelected ? 'border-primary bg-primary/5' : 'border-border'}
      `}
    >
      {/* Type and Confidence */}
      <div className="flex items-start justify-between mb-2">
        <Badge variant="outline" className="text-xs">
          {hypothesis.type}
        </Badge>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <TrendingUp className="h-3 w-3" />
          {Math.round(hypothesis.confidence * 100)}%
        </div>
      </div>

      {/* Evidence Description */}
      <p className="text-sm mb-3 line-clamp-2">
        {hypothesis.evidence.description}
      </p>

      {/* Evidence Strength Meter */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
          <span>Evidence Strength</span>
          <span>{Math.round(evidenceStrength)}%</span>
        </div>
        <Progress value={evidenceStrength} className="h-1.5" />
      </div>

      {/* Indicators */}
      <div className="flex items-center gap-2">
        {hasContradiction && (
          <Badge variant="destructive" className="text-xs">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Contradiction
          </Badge>
        )}
        {hasResearchGap && (
          <Badge variant="secondary" className="text-xs">
            <HelpCircle className="h-3 w-3 mr-1" />
            Research Gap
          </Badge>
        )}
      </div>

      {/* Evidence Count */}
      <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
        <span>{hypothesis.evidence.papers.length} papers</span>
        <span>{hypothesis.evidence.citations.length} citations</span>
        <span>{hypothesis.evidence.connections.length} connections</span>
      </div>
    </button>
  );
});

HypothesisCard.displayName = 'HypothesisCard';
