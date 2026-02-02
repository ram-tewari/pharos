/**
 * View Mode Hook
 * 
 * Custom hook for managing view mode logic and layout application.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 11 View Modes
 */

import { useEffect, useCallback } from 'react';
import { useGraphStore } from '@/stores/graph';
import { applyLayout, applyRadialLayout } from '@/lib/graph/layouts';
import type { GraphNode, GraphEdge, VisualizationMode, LayoutAlgorithm } from '@/types/graph';

// ============================================================================
// Hook
// ============================================================================

export function useViewMode() {
  const {
    nodes,
    edges,
    visualizationMode,
    selectedNodes,
    setGraphData,
  } = useGraphStore();

  /**
   * Apply layout based on current view mode
   */
  const applyViewModeLayout = useCallback((
    nodesToLayout: GraphNode[],
    edgesToLayout: GraphEdge[],
    centerNodeId?: string
  ) => {
    let layoutedNodes: GraphNode[];

    switch (visualizationMode) {
      case VisualizationMode.CityMap:
        // Force-directed layout for city map (clusters)
        layoutedNodes = applyLayout(nodesToLayout, edgesToLayout, 'force_directed', {
          forceDirected: {
            chargeStrength: -300,
            linkDistance: 100,
            collisionRadius: 30,
          },
        });
        break;

      case VisualizationMode.BlastRadius:
        // Radial layout for blast radius (impact analysis)
        if (centerNodeId) {
          layoutedNodes = applyRadialLayout(nodesToLayout, edgesToLayout, centerNodeId);
        } else if (selectedNodes.size > 0) {
          const firstSelected = Array.from(selectedNodes)[0];
          layoutedNodes = applyRadialLayout(nodesToLayout, edgesToLayout, firstSelected);
        } else {
          // Fallback to force-directed if no center node
          layoutedNodes = applyLayout(nodesToLayout, edgesToLayout, 'force_directed');
        }
        break;

      case VisualizationMode.DependencyWaterfall:
        // Hierarchical layout for dependency waterfall (DAG)
        layoutedNodes = applyLayout(nodesToLayout, edgesToLayout, 'dagre', {
          dagre: {
            rankDir: 'TB', // Top to bottom
            nodeSep: 50,
            rankSep: 100,
          },
        });
        break;

      case VisualizationMode.Hypothesis:
        // Force-directed with tighter clustering for hypothesis mode
        layoutedNodes = applyLayout(nodesToLayout, edgesToLayout, 'force_directed', {
          forceDirected: {
            chargeStrength: -200,
            linkDistance: 80,
            collisionRadius: 25,
          },
        });
        break;

      default:
        layoutedNodes = applyLayout(nodesToLayout, edgesToLayout, 'force_directed');
    }

    return layoutedNodes;
  }, [visualizationMode, selectedNodes]);

  /**
   * Re-apply layout when view mode changes
   */
  useEffect(() => {
    if (nodes.length > 0) {
      const layoutedNodes = applyViewModeLayout(nodes, edges);
      setGraphData({
        nodes: layoutedNodes,
        edges,
        metadata: undefined,
      });
    }
  }, [visualizationMode]); // Only re-layout when mode changes

  return {
    applyViewModeLayout,
  };
}
