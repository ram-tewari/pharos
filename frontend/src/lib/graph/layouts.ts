/**
 * Graph Layout Algorithms
 * 
 * Layout algorithms for positioning nodes in the graph visualization.
 * Includes radial, force-directed, hierarchical, and custom layouts.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 6 Graph Canvas
 * Task: 6.2
 */

import dagre from 'dagre';
import * as d3 from 'd3';
import type { GraphNode, GraphEdge, Position, LayoutAlgorithm, LayoutOptions } from '@/types/graph';

// ============================================================================
// Radial Layout (Mind Map)
// ============================================================================

/**
 * Radial layout for mind map view
 * Places center node at origin, arranges neighbors in circles
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param centerNodeId - ID of the center node
 * @returns Nodes with updated positions
 * 
 * Property 4: Mind Map Center Node
 * Property 5: Radial Neighbor Layout
 */
export function radialLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  centerNodeId: string
): GraphNode[] {
  const centerNode = nodes.find((n) => n.id === centerNodeId);
  if (!centerNode) {
    return nodes;
  }

  // Find neighbors of center node
  const neighborIds = new Set<string>();
  edges.forEach((edge) => {
    if (edge.source === centerNodeId) {
      neighborIds.add(edge.target);
    } else if (edge.target === centerNodeId) {
      neighborIds.add(edge.source);
    }
  });

  const neighbors = nodes.filter((n) => neighborIds.has(n.id));
  const others = nodes.filter((n) => n.id !== centerNodeId && !neighborIds.has(n.id));

  // Position center node at origin
  const updatedNodes: GraphNode[] = [
    {
      ...centerNode,
      position: { x: 0, y: 0 },
    },
  ];

  // Position neighbors in a circle
  const radius = 300;
  const angleStep = (2 * Math.PI) / neighbors.length;

  neighbors.forEach((node, index) => {
    const angle = index * angleStep;
    updatedNodes.push({
      ...node,
      position: {
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle),
      },
    });
  });

  // Position other nodes further out
  const outerRadius = 600;
  const outerAngleStep = (2 * Math.PI) / Math.max(others.length, 1);

  others.forEach((node, index) => {
    const angle = index * outerAngleStep;
    updatedNodes.push({
      ...node,
      position: {
        x: outerRadius * Math.cos(angle),
        y: outerRadius * Math.sin(angle),
      },
    });
  });

  return updatedNodes;
}

// ============================================================================
// Force-Directed Layout (Global Overview)
// ============================================================================

/**
 * Force-directed layout using D3
 * Creates organic clustering based on connections
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param options - Layout options
 * @returns Nodes with updated positions
 */
export function forceDirectedLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options?: LayoutOptions['forceDirected']
): GraphNode[] {
  const {
    chargeStrength = -300,
    linkDistance = 100,
    collisionRadius = 30,
  } = options || {};

  // Create D3 simulation
  const simulation = d3
    .forceSimulation(nodes as any)
    .force(
      'link',
      d3
        .forceLink(edges as any)
        .id((d: any) => d.id)
        .distance(linkDistance)
    )
    .force('charge', d3.forceManyBody().strength(chargeStrength))
    .force('center', d3.forceCenter(0, 0))
    .force('collision', d3.forceCollide().radius(collisionRadius));

  // Run simulation synchronously
  simulation.stop();
  for (let i = 0; i < 300; i++) {
    simulation.tick();
  }

  // Extract positions
  return nodes.map((node, index) => {
    const simNode = simulation.nodes()[index] as any;
    return {
      ...node,
      position: {
        x: simNode.x || 0,
        y: simNode.y || 0,
      },
    };
  });
}

// ============================================================================
// Hierarchical Layout (Entity View)
// ============================================================================

/**
 * Hierarchical layout using Dagre
 * Creates top-down or left-right hierarchy
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param options - Layout options
 * @returns Nodes with updated positions
 */
export function hierarchicalLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options?: LayoutOptions['dagre']
): GraphNode[] {
  const {
    rankDir = 'TB',
    nodeSep = 50,
    rankSep = 100,
  } = options || {};

  // Create dagre graph
  const g = new dagre.graphlib.Graph();
  g.setGraph({
    rankdir: rankDir,
    nodesep: nodeSep,
    ranksep: rankSep,
  });
  g.setDefaultEdgeLabel(() => ({}));

  // Add nodes
  nodes.forEach((node) => {
    g.setNode(node.id, { width: 100, height: 50 });
  });

  // Add edges
  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  // Compute layout
  dagre.layout(g);

  // Extract positions
  return nodes.map((node) => {
    const dagreNode = g.node(node.id);
    return {
      ...node,
      position: {
        x: dagreNode.x,
        y: dagreNode.y,
      },
    };
  });
}

// ============================================================================
// Circular Layout
// ============================================================================

/**
 * Circular layout
 * Arranges nodes in a circle
 * 
 * @param nodes - All nodes in the graph
 * @param options - Layout options
 * @returns Nodes with updated positions
 */
export function circularLayout(
  nodes: GraphNode[],
  options?: LayoutOptions['circular']
): GraphNode[] {
  const { radius = 400, sortBy = 'alphabetical' } = options || {};

  // Sort nodes
  let sortedNodes = [...nodes];
  if (sortBy === 'centrality') {
    sortedNodes.sort((a, b) => {
      const aDegree = a.metadata?.centrality?.degree || 0;
      const bDegree = b.metadata?.centrality?.degree || 0;
      return bDegree - aDegree;
    });
  } else {
    sortedNodes.sort((a, b) => a.label.localeCompare(b.label));
  }

  // Position nodes in circle
  const angleStep = (2 * Math.PI) / nodes.length;

  return sortedNodes.map((node, index) => {
    const angle = index * angleStep;
    return {
      ...node,
      position: {
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle),
      },
    };
  });
}

// ============================================================================
// Hypothesis Layout (A→B→C)
// ============================================================================

/**
 * Custom layout for hypothesis visualization
 * Arranges nodes to highlight A→B→C paths
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param hypothesisNodes - Node IDs involved in hypothesis
 * @returns Nodes with updated positions
 */
export function hypothesisLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  hypothesisNodes: string[]
): GraphNode[] {
  if (hypothesisNodes.length < 3) {
    // Fall back to force-directed if not enough nodes
    return forceDirectedLayout(nodes, edges);
  }

  const [nodeA, nodeB, nodeC] = hypothesisNodes;

  // Position A, B, C in a line
  const spacing = 300;
  const hypothesisPositions: Record<string, Position> = {
    [nodeA]: { x: -spacing, y: 0 },
    [nodeB]: { x: 0, y: 0 },
    [nodeC]: { x: spacing, y: 0 },
  };

  // Position other nodes around the hypothesis
  const otherNodes = nodes.filter((n) => !hypothesisNodes.includes(n.id));
  const radius = 200;
  const angleStep = (2 * Math.PI) / Math.max(otherNodes.length, 1);

  return nodes.map((node) => {
    if (hypothesisPositions[node.id]) {
      return {
        ...node,
        position: hypothesisPositions[node.id],
      };
    }

    const index = otherNodes.findIndex((n) => n.id === node.id);
    const angle = index * angleStep;
    return {
      ...node,
      position: {
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle) + 300,
      },
    };
  });
}

// ============================================================================
// Layout Dispatcher
// ============================================================================

/**
 * Apply layout algorithm to graph
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param algorithm - Layout algorithm to use
 * @param options - Layout options
 * @param context - Additional context (e.g., center node ID)
 * @returns Nodes with updated positions
 */
export function applyLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  algorithm: LayoutAlgorithm,
  options?: LayoutOptions,
  context?: {
    centerNodeId?: string;
    hypothesisNodes?: string[];
  }
): GraphNode[] {
  switch (algorithm) {
    case 'force_directed':
      return forceDirectedLayout(nodes, edges, options?.forceDirected);

    case 'hierarchical':
      return hierarchicalLayout(nodes, edges, options?.dagre);

    case 'circular':
      return circularLayout(nodes, options?.circular);

    case 'dagre':
      return hierarchicalLayout(nodes, edges, options?.dagre);

    case 'manual':
      // Return nodes as-is for manual positioning
      return nodes;

    default:
      return forceDirectedLayout(nodes, edges);
  }
}

/**
 * Apply radial layout for mind map
 * Separate function because it requires centerNodeId
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param centerNodeId - ID of the center node
 * @returns Nodes with updated positions
 */
export function applyRadialLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  centerNodeId: string
): GraphNode[] {
  return radialLayout(nodes, edges, centerNodeId);
}

/**
 * Apply hypothesis layout
 * Separate function because it requires hypothesis nodes
 * 
 * @param nodes - All nodes in the graph
 * @param edges - All edges in the graph
 * @param hypothesisNodes - Node IDs involved in hypothesis
 * @returns Nodes with updated positions
 */
export function applyHypothesisLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  hypothesisNodes: string[]
): GraphNode[] {
  return hypothesisLayout(nodes, edges, hypothesisNodes);
}
