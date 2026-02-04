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
import { EmptyPanelState } from './EmptyPanelState';
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
    <aside 
      className="h-full flex flex-col bg-background border-l shadow-lg"
      role="complementary"
      aria-label="Hypothesis discovery panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 md:p-4 border-b bg-gradient-to-r from-card to-card/50">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 md:h-5 md:w-5 text-primary" aria-hidden="true" />
          <h2 className="text-base md:text-lg font-semibold">Hypotheses</h2>
          <Badge variant="secondary" aria-label={`${hypotheses.length} hypotheses discovered`} className="animate-in zoom-in-50 duration-200">
            {hypotheses.length}
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          aria-label="Close hypothesis panel"
          className="min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-110 hover:bg-accent active:scale-95"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </Button>
      </div>

      {/* Discover Button */}
      <div className="p-3 md:p-4 border-b bg-gradient-to-b from-card/50 to-card">
        <Button
          onClick={onDiscoverNew}
          className="w-full min-h-[44px] transition-all duration-200 hover:scale-[1.02] hover:shadow-lg active:scale-95"
          variant="default"
          aria-label="Discover new hypotheses using ABC pattern"
        >
          <Lightbulb className="h-4 w-4 mr-2" aria-hidden="true" />
          <span className="hidden sm:inline">Discover New Hypotheses</span>
          <span className="sm:hidden">Discover New</span>
        </Button>
      </div>

      {/* Hypotheses List */}
      <ScrollArea className="flex-1">
        <div className="p-3 md:p-4 space-y-3" role="list" aria-label="Discovered hypotheses">
          {hypotheses.length === 0 ? (
            <EmptyPanelState
              title="No hypotheses discovered yet"
              message='Click "Discover New" to find hidden connections using the ABC pattern.'
              icon="lightbulb"
            />
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
    </aside>
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
        w-full text-left p-3 rounded-lg border transition-all duration-200
        hover:border-primary hover:shadow-md hover:-translate-y-0.5
        min-h-[120px] touch-manipulation
        ${isSelected ? 'border-primary bg-primary/5 shadow-sm' : 'border-border hover:bg-accent/50'}
      `}
      role="listitem"
      aria-label={`Hypothesis: ${hypothesis.evidence.description}. Confidence: ${Math.round(hypothesis.confidence * 100)} percent`}
      aria-pressed={isSelected}
    >
      {/* Type and Confidence */}
      <div className="flex items-start justify-between mb-2">
        <Badge variant="outline" className="text-xs">
          {hypothesis.type}
        </Badge>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <TrendingUp className="h-3 w-3" aria-hidden="true" />
          <span aria-label={`Confidence: ${Math.round(hypothesis.confidence * 100)} percent`}>
            {Math.round(hypothesis.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Evidence Description */}
      <p className="text-xs md:text-sm mb-3 line-clamp-2">
        {hypothesis.evidence.description}
      </p>

      {/* Evidence Strength Meter */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
          <span>Evidence Strength</span>
          <span aria-hidden="true">{Math.round(evidenceStrength)}%</span>
        </div>
        <Progress 
          value={evidenceStrength} 
          className="h-1.5"
          aria-label={`Evidence strength: ${Math.round(evidenceStrength)} percent`}
        />
      </div>

      {/* Indicators */}
      <div className="flex items-center gap-2 flex-wrap" role="group" aria-label="Hypothesis indicators">
        {hasContradiction && (
          <Badge variant="destructive" className="text-xs">
            <AlertTriangle className="h-3 w-3 mr-1" aria-hidden="true" />
            <span className="hidden sm:inline">Contradiction</span>
            <span className="sm:hidden">Conflict</span>
          </Badge>
        )}
        {hasResearchGap && (
          <Badge variant="secondary" className="text-xs">
            <HelpCircle className="h-3 w-3 mr-1" aria-hidden="true" />
            <span className="hidden sm:inline">Research Gap</span>
            <span className="sm:hidden">Gap</span>
          </Badge>
        )}
      </div>

      {/* Evidence Count */}
      <div className="mt-2 flex items-center gap-2 md:gap-3 text-xs text-muted-foreground flex-wrap">
        <span>{hypothesis.evidence.papers.length} papers</span>
        <span>{hypothesis.evidence.citations.length} citations</span>
        <span className="hidden sm:inline">{hypothesis.evidence.connections.length} connections</span>
      </div>
    </button>
  );
});

HypothesisCard.displayName = 'HypothesisCard';
