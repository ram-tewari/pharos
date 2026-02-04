/**
 * Node Details Panel Component
 * 
 * Displays detailed information about the selected node.
 * Shows resource metadata, quality scores, and actions.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 10 Side Panel
 * Task: 10.1
 * 
 * Properties:
 * - Property 50: View Details Button Visibility
 */

import { memo } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { ExternalLink, Network, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { EmptyPanelState } from './EmptyPanelState';
import type { GraphNode } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

interface NodeDetailsPanelProps {
  node: GraphNode | null;
  onClose: () => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

function getQualityColor(score: number): string {
  if (score > 0.8) return 'bg-green-500';
  if (score >= 0.5) return 'bg-yellow-500';
  return 'bg-red-500';
}

function getQualityLabel(score: number): string {
  if (score > 0.8) return 'High';
  if (score >= 0.5) return 'Medium';
  return 'Low';
}

// ============================================================================
// Component
// ============================================================================

export const NodeDetailsPanel = memo<NodeDetailsPanelProps>(({ node, onClose }) => {
  const navigate = useNavigate();

  if (!node) {
    return (
      <aside 
        className="flex items-center justify-center h-full bg-card"
        role="complementary"
        aria-label="Node details panel"
      >
        <EmptyPanelState
          title="No node selected"
          message="Click on a node in the graph to view its details."
          icon="info"
        />
      </aside>
    );
  }

  const qualityScore = node.metadata?.qualityScore as number | undefined;
  const resourceId = node.metadata?.resourceId as string | undefined;
  const citationCount = node.metadata?.citationCount as number | undefined;
  const tags = node.metadata?.tags as string[] | undefined;

  // Property 50: View Details Button Visibility
  const handleViewDetails = () => {
    if (resourceId) {
      navigate({ to: `/library/${resourceId}` });
    }
  };

  const handleViewInMindMap = () => {
    // TODO: Switch to mind map mode with this node as center
    console.log('View in mind map:', node.id);
  };

  return (
    <aside 
      className="flex flex-col h-full bg-card shadow-lg"
      role="complementary"
      aria-label="Node details panel"
    >
      {/* Header */}
      <div className="flex items-start justify-between p-3 md:p-4 border-b bg-gradient-to-r from-card to-card/50">
        <div className="flex-1 pr-4">
          <h3 
            className="font-semibold text-base md:text-lg line-clamp-2" 
            title={node.label}
            id="node-details-title"
          >
            {node.label}
          </h3>
          <p className="text-xs md:text-sm text-muted-foreground mt-1">
            {node.type === 'resource' ? 'Resource' : 'Entity'}
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="shrink-0 min-h-[44px] min-w-[44px] transition-all duration-200 hover:scale-110 hover:bg-accent active:scale-95"
          aria-label="Close node details panel"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1" aria-labelledby="node-details-title">
        <div className="p-3 md:p-4 space-y-4 md:space-y-6">
          {/* Quality Score */}
          {qualityScore !== undefined && (
            <div role="group" aria-labelledby="quality-heading">
              <h4 id="quality-heading" className="text-sm font-medium mb-2">Quality Score</h4>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div 
                    className="h-2 bg-muted rounded-full overflow-hidden"
                    role="progressbar"
                    aria-valuenow={qualityScore * 100}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Quality score: ${(qualityScore * 100).toFixed(0)} percent`}
                  >
                    <div
                      className={`h-full ${getQualityColor(qualityScore)}`}
                      style={{ width: `${qualityScore * 100}%` }}
                    />
                  </div>
                </div>
                <Badge variant="outline" aria-label={`Quality level: ${getQualityLabel(qualityScore)}`}>
                  {getQualityLabel(qualityScore)}
                </Badge>
                <span className="text-sm font-medium" aria-hidden="true">
                  {(qualityScore * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}

          {/* Metadata */}
          <div role="group" aria-labelledby="metadata-heading">
            <h4 id="metadata-heading" className="text-sm font-medium mb-2">Metadata</h4>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Type</dt>
                <dd className="font-medium capitalize">{node.type}</dd>
              </div>
              {citationCount !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Citations</dt>
                  <dd className="font-medium">{citationCount}</dd>
                </div>
              )}
              {node.metadata?.centrality?.degree !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Connections</dt>
                  <dd className="font-medium">{node.metadata.centrality.degree}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Tags */}
          {tags && tags.length > 0 && (
            <div role="group" aria-labelledby="tags-heading">
              <h4 id="tags-heading" className="text-sm font-medium mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2" role="list">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary" role="listitem">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Centrality Metrics */}
          {node.metadata?.centrality && (
            <div role="group" aria-labelledby="centrality-heading">
              <h4 id="centrality-heading" className="text-sm font-medium mb-2">Centrality Metrics</h4>
              <dl className="space-y-2 text-sm">
                {node.metadata.centrality.degree !== undefined && (
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Degree</dt>
                    <dd className="font-medium">
                      {node.metadata.centrality.degree.toFixed(2)}
                    </dd>
                  </div>
                )}
                {node.metadata.centrality.betweenness !== undefined && (
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Betweenness</dt>
                    <dd className="font-medium">
                      {node.metadata.centrality.betweenness.toFixed(2)}
                    </dd>
                  </div>
                )}
                {node.metadata.centrality.closeness !== undefined && (
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Closeness</dt>
                    <dd className="font-medium">
                      {node.metadata.centrality.closeness.toFixed(2)}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          <Separator />

          {/* Actions */}
          <div className="space-y-2" role="group" aria-label="Node actions">
            {resourceId && (
              <Button
                variant="default"
                className="w-full min-h-[44px] transition-all duration-200 hover:scale-[1.02] hover:shadow-lg active:scale-95"
                onClick={handleViewDetails}
                aria-label={`View full details for ${node.label}`}
              >
                <ExternalLink className="w-4 h-4 mr-2" aria-hidden="true" />
                View Details
              </Button>
            )}
            <Button
              variant="outline"
              className="w-full min-h-[44px] transition-all duration-200 hover:scale-[1.02] hover:shadow-md active:scale-95"
              onClick={handleViewInMindMap}
              aria-label={`View ${node.label} in mind map mode`}
            >
              <Network className="w-4 h-4 mr-2" aria-hidden="true" />
              View in Mind Map
            </Button>
          </div>
        </div>
      </ScrollArea>
    </aside>
  );
});

NodeDetailsPanel.displayName = 'NodeDetailsPanel';
