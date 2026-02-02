/**
 * Graph API Client
 * 
 * API client for graph-related endpoints including neighbors, overview,
 * hypothesis discovery, entities, and traversal.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 3 API Integration
 * Task: 3.1
 */

import { apiClient } from './client';
import type {
  GraphData,
  GraphNode,
  GraphEdge,
  Hypothesis,
  GraphEntity,
  GraphRelationship,
} from '@/types/graph';

// ============================================================================
// API Response Types
// ============================================================================

interface NeighborsResponse {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    metadata?: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    weight?: number;
    metadata?: Record<string, unknown>;
  }>;
}

interface OverviewResponse {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    centrality?: {
      degree?: number;
      betweenness?: number;
      closeness?: number;
    };
    metadata?: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    weight?: number;
    metadata?: Record<string, unknown>;
  }>;
  metadata?: {
    nodeCount?: number;
    edgeCount?: number;
    density?: number;
    averageDegree?: number;
  };
}

interface HypothesisResponse {
  hypotheses: Array<{
    id: string;
    type: string;
    confidence: number;
    evidence: {
      papers: string[];
      citations: string[];
      connections: string[];
      description: string;
    };
    nodes: string[];
    edges?: string[];
    metadata?: Record<string, unknown>;
  }>;
}

interface EntitiesResponse {
  entities: Array<{
    id: string;
    name: string;
    type: string;
    properties?: Record<string, unknown>;
  }>;
}

interface RelationshipsResponse {
  relationships: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    properties?: Record<string, unknown>;
  }>;
}

interface TraverseResponse {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    metadata?: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    weight?: number;
    metadata?: Record<string, unknown>;
  }>;
  path?: string[];
}

// ============================================================================
// Data Transformation Utilities
// ============================================================================

/**
 * Transform API node to GraphNode
 */
function transformNode(apiNode: NeighborsResponse['nodes'][0]): GraphNode {
  return {
    id: apiNode.id,
    label: apiNode.label,
    type: apiNode.type as GraphNode['type'],
    position: { x: 0, y: 0 }, // Will be computed by layout algorithm
    metadata: apiNode.metadata,
  };
}

/**
 * Transform API edge to GraphEdge
 */
function transformEdge(apiEdge: NeighborsResponse['edges'][0]): GraphEdge {
  return {
    id: apiEdge.id,
    source: apiEdge.source,
    target: apiEdge.target,
    type: apiEdge.type as GraphEdge['type'],
    weight: apiEdge.weight,
    metadata: apiEdge.metadata,
  };
}

/**
 * Transform API response to GraphData
 */
function transformToGraphData(
  nodes: NeighborsResponse['nodes'],
  edges: NeighborsResponse['edges'],
  metadata?: OverviewResponse['metadata']
): GraphData {
  return {
    nodes: nodes.map(transformNode),
    edges: edges.map(transformEdge),
    metadata,
  };
}

// ============================================================================
// Graph API Client Class
// ============================================================================

export class GraphAPIClient {
  /**
   * Get neighbors of a resource
   * 
   * @param resourceId - Resource ID to get neighbors for
   * @returns Graph data with neighbors
   * 
   * @example
   * ```typescript
   * const data = await graphAPI.getNeighbors('resource_123');
   * console.log(`Found ${data.nodes.length} neighbors`);
   * ```
   */
  async getNeighbors(resourceId: string): Promise<GraphData> {
    try {
      const response = await apiClient.get<NeighborsResponse>(
        `/graph/resource/${resourceId}/neighbors`
      );
      
      return transformToGraphData(response.data.nodes, response.data.edges);
    } catch (error) {
      console.error('Failed to fetch neighbors:', error);
      throw new Error('Failed to load graph neighbors. Please try again.');
    }
  }

  /**
   * Get global overview of the graph
   * 
   * @param threshold - Minimum connection strength (0.0-1.0)
   * @returns Graph data with overview
   * 
   * @example
   * ```typescript
   * const data = await graphAPI.getOverview(0.5);
   * console.log(`Overview has ${data.nodes.length} nodes`);
   * ```
   */
  async getOverview(threshold: number = 0.5): Promise<GraphData> {
    try {
      const response = await apiClient.get<OverviewResponse>(
        `/graph/overview`,
        { params: { threshold } }
      );
      
      return transformToGraphData(
        response.data.nodes,
        response.data.edges,
        response.data.metadata
      );
    } catch (error) {
      console.error('Failed to fetch overview:', error);
      throw new Error('Failed to load graph overview. Please try again.');
    }
  }

  /**
   * Discover hypotheses using Literature-Based Discovery (LBD)
   * 
   * @param entityA - Starting entity ID
   * @param entityC - Target entity ID
   * @returns List of discovered hypotheses
   * 
   * @example
   * ```typescript
   * const hypotheses = await graphAPI.discoverHypotheses('entity_a', 'entity_c');
   * console.log(`Found ${hypotheses.length} hypotheses`);
   * ```
   */
  async discoverHypotheses(
    entityA: string,
    entityC: string
  ): Promise<Hypothesis[]> {
    try {
      const response = await apiClient.post<HypothesisResponse>(
        `/graph/discover`,
        {
          entity_a: entityA,
          entity_c: entityC,
        }
      );
      
      return response.data.hypotheses.map((h) => ({
        id: h.id,
        type: h.type as Hypothesis['type'],
        confidence: h.confidence,
        evidence: h.evidence,
        nodes: h.nodes,
        edges: h.edges,
        metadata: h.metadata,
      }));
    } catch (error) {
      console.error('Failed to discover hypotheses:', error);
      throw new Error('Failed to discover hypotheses. Please try again.');
    }
  }

  /**
   * Get all entities in the graph
   * 
   * @returns List of entities
   * 
   * @example
   * ```typescript
   * const entities = await graphAPI.getEntities();
   * console.log(`Found ${entities.length} entities`);
   * ```
   */
  async getEntities(): Promise<GraphEntity[]> {
    try {
      const response = await apiClient.get<EntitiesResponse>(`/graph/entities`);
      
      return response.data.entities;
    } catch (error) {
      console.error('Failed to fetch entities:', error);
      throw new Error('Failed to load entities. Please try again.');
    }
  }

  /**
   * Get relationships for an entity
   * 
   * @param entityId - Entity ID to get relationships for
   * @returns List of relationships
   * 
   * @example
   * ```typescript
   * const relationships = await graphAPI.getEntityRelationships('entity_123');
   * console.log(`Found ${relationships.length} relationships`);
   * ```
   */
  async getEntityRelationships(entityId: string): Promise<GraphRelationship[]> {
    try {
      const response = await apiClient.get<RelationshipsResponse>(
        `/graph/entities/${entityId}/relationships`
      );
      
      return response.data.relationships;
    } catch (error) {
      console.error('Failed to fetch entity relationships:', error);
      throw new Error('Failed to load entity relationships. Please try again.');
    }
  }

  /**
   * Traverse the graph from a starting entity
   * 
   * @param startEntity - Starting entity ID
   * @param depth - Traversal depth (default: 2)
   * @returns Graph data with traversal path
   * 
   * @example
   * ```typescript
   * const data = await graphAPI.traverseGraph('entity_123', 3);
   * console.log(`Traversal found ${data.nodes.length} nodes`);
   * ```
   */
  async traverseGraph(
    startEntity: string,
    depth: number = 2
  ): Promise<GraphData & { path?: string[] }> {
    try {
      const response = await apiClient.get<TraverseResponse>(
        `/graph/traverse`,
        {
          params: {
            start: startEntity,
            depth,
          },
        }
      );
      
      const graphData = transformToGraphData(
        response.data.nodes,
        response.data.edges
      );
      
      return {
        ...graphData,
        path: response.data.path,
      };
    } catch (error) {
      console.error('Failed to traverse graph:', error);
      throw new Error('Failed to traverse graph. Please try again.');
    }
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

/**
 * Singleton instance of GraphAPIClient
 * 
 * @example
 * ```typescript
 * import { graphAPI } from '@/lib/api/graph';
 * 
 * const data = await graphAPI.getNeighbors('resource_123');
 * ```
 */
export const graphAPI = new GraphAPIClient();
