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
      <div className="flex items-center justify-center h-full p-8 text-center">
        <div className="text-muted-foreground">
          <Network className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Select a node to view details</p>
        </div>
      </div>
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
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b">
        <div className="flex-1 pr-4">
          <h3 className="font-semibold text-lg line-clamp-2" title={node.label}>
            {node.label}
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            {node.type === 'resource' ? 'Resource' : 'Entity'}
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="shrink-0"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Quality Score */}
          {qualityScore !== undefined && (
            <div>
              <h4 className="text-sm font-medium mb-2">Quality Score</h4>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getQualityColor(qualityScore)}`}
                      style={{ width: `${qualityScore * 100}%` }}
                    />
                  </div>
                </div>
                <Badge variant="outline">
                  {getQualityLabel(qualityScore)}
                </Badge>
                <span className="text-sm font-medium">
                  {(qualityScore * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}

          {/* Metadata */}
          <div>
            <h4 className="text-sm font-medium mb-2">Metadata</h4>
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
            <div>
              <h4 className="text-sm font-medium mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Centrality Metrics */}
          {node.metadata?.centrality && (
            <div>
              <h4 className="text-sm font-medium mb-2">Centrality Metrics</h4>
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
          <div className="space-y-2">
            {resourceId && (
              <Button
                variant="default"
                className="w-full"
                onClick={handleViewDetails}
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Details
              </Button>
            )}
            <Button
              variant="outline"
              className="w-full"
              onClick={handleViewInMindMap}
            >
              <Network className="w-4 h-4 mr-2" />
              View in Mind Map
            </Button>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
});

NodeDetailsPanel.displayName = 'NodeDetailsPanel';
