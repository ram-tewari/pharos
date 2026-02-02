/**
 * Focus Mode Hook
 * 
 * Custom hook for managing focus mode (dimming non-selected nodes).
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 15 Advanced Interactions
 * Task: 15.5
 * 
 * Properties:
 * - Property 33: Focus Mode Dimming
 */

import { useMemo } from 'react';
import type { GraphNode, GraphEdge } from '@/types/graph';

// ============================================================================
// Hook
// ============================================================================

/**
 * Property 33: Focus Mode Dimming
 * 
 * In focus mode, all nodes except selected node and its immediate neighbors
 * have reduced opacity (0.3).
 */
export function useFocusMode(
  nodes: GraphNode[],
  edges: GraphEdge[],
  selectedNodeId: string | null,
  isFocusMode: boolean
) {
  return useMemo(() => {
    if (!isFocusMode || !selectedNodeId) {
      return { nodes, edges };
    }

    // Find immediate neighbors of selected node
    const neighborIds = new Set<string>();
    edges.forEach((edge) => {
      if (edge.source === selectedNodeId) {
        neighborIds.add(edge.target);
      } else if (edge.target === selectedNodeId) {
        neighborIds.add(edge.source);
      }
    });

    // Add selected node itself
    neighborIds.add(selectedNodeId);

    // Apply opacity to nodes
    const focusedNodes = nodes.map((node) => ({
      ...node,
      metadata: {
        ...node.metadata,
        opacity: neighborIds.has(node.id) ? 1.0 : 0.3,
      },
    }));

    // Apply opacity to edges
    const focusedEdges = edges.map((edge) => ({
      ...edge,
      metadata: {
        ...edge.metadata,
        opacity:
          neighborIds.has(edge.source) && neighborIds.has(edge.target)
            ? 1.0
            : 0.3,
      },
    }));

    return {
      nodes: focusedNodes,
      edges: focusedEdges,
    };
  }, [nodes, edges, selectedNodeId, isFocusMode]);
}
