/**
 * Graph Filters Hook
 * 
 * Custom hook for filtering graph nodes based on search query and filters.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 16 Search and Filtering
 * Task: 16.1
 * 
 * Properties:
 * - Property 15: Search Filtering
 * - Property 16: Search Result Highlighting
 * - Property 17: Filter Application
 */

import { useMemo } from 'react';
import type { GraphNode, GraphEdge } from '@/types/graph';
import type { GraphFilters } from '../components/FilterPanel';

// ============================================================================
// Types
// ============================================================================

interface UseGraphFiltersResult {
  filteredNodes: GraphNode[];
  filteredEdges: GraphEdge[];
  matchingNodeIds: Set<string>;
}

// ============================================================================
// Hook
// ============================================================================

/**
 * Filter graph nodes and edges based on search query and filters
 * 
 * Property 15: Search Filtering - Filters by title, author, tags (case-insensitive)
 * Property 17: Filter Application - AND logic for all filters
 * 
 * @param nodes - All graph nodes
 * @param edges - All graph edges
 * @param searchQuery - Search query string
 * @param filters - Active filters
 * @returns Filtered nodes, edges, and matching node IDs
 */
export function useGraphFilters(
  nodes: GraphNode[],
  edges: GraphEdge[],
  searchQuery: string,
  filters: GraphFilters
): UseGraphFiltersResult {
  return useMemo(() => {
    // Property 15: Search Filtering (case-insensitive)
    const normalizedQuery = searchQuery.toLowerCase().trim();
    
    const filteredNodes = nodes.filter((node) => {
      // Search filter
      if (normalizedQuery) {
        const matchesLabel = node.label.toLowerCase().includes(normalizedQuery);
        const matchesAuthor = node.metadata?.author
          ? String(node.metadata.author).toLowerCase().includes(normalizedQuery)
          : false;
        const matchesTags = node.metadata?.tags
          ? (node.metadata.tags as string[]).some((tag) =>
              tag.toLowerCase().includes(normalizedQuery)
            )
          : false;

        if (!matchesLabel && !matchesAuthor && !matchesTags) {
          return false;
        }
      }

      // Property 17: Filter Application (AND logic)
      
      // Resource type filter
      if (node.type === 'resource' && node.metadata?.resourceType) {
        const resourceType = node.metadata.resourceType as string;
        if (!filters.resourceTypes.includes(resourceType)) {
          return false;
        }
      }

      // Quality filter
      if (node.metadata?.qualityScore !== undefined) {
        const qualityScore = node.metadata.qualityScore as number;
        if (qualityScore < filters.minQuality) {
          return false;
        }
      }

      // Date range filter (TODO: implement when date metadata is available)
      // if (filters.dateRange && node.metadata?.publicationDate) {
      //   const date = new Date(node.metadata.publicationDate);
      //   if (date < filters.dateRange[0] || date > filters.dateRange[1]) {
      //     return false;
      //   }
      // }

      return true;
    });

    // Get IDs of filtered nodes
    const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));

    // Property 16: Matching node IDs for highlighting
    const matchingNodeIds = new Set<string>();
    if (normalizedQuery) {
      filteredNodes.forEach((node) => {
        const matchesLabel = node.label.toLowerCase().includes(normalizedQuery);
        const matchesAuthor = node.metadata?.author
          ? String(node.metadata.author).toLowerCase().includes(normalizedQuery)
          : false;
        const matchesTags = node.metadata?.tags
          ? (node.metadata.tags as string[]).some((tag) =>
              tag.toLowerCase().includes(normalizedQuery)
            )
          : false;

        if (matchesLabel || matchesAuthor || matchesTags) {
          matchingNodeIds.add(node.id);
        }
      });
    }

    // Filter edges to only include those connecting filtered nodes
    const filteredEdges = edges.filter(
      (edge) =>
        filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
    );

    return {
      filteredNodes,
      filteredEdges,
      matchingNodeIds,
    };
  }, [nodes, edges, searchQuery, filters]);
}
