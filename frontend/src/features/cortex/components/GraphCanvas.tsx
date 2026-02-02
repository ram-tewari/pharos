/**
 * Graph Canvas Component
 * 
 * Main graph visualization canvas using React Flow.
 * Handles node/edge rendering, interactions, and layout.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 6 Graph Canvas
 * Task: 6.1
 */

import { memo, useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeTypes,
  EdgeTypes,
  OnNodesChange,
  OnEdgesChange,
  OnNodeClick,
  OnEdgeClick,
  applyNodeChanges,
  applyEdgeChanges,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { ResourceNode } from './ResourceNode';
import { EntityNode } from './EntityNode';
import { CustomEdge } from './CustomEdge';
import type { GraphNode, GraphEdge, ViewportState } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  onViewportChange?: (viewport: ViewportState) => void;
  selectedNodeId?: string | null;
  showIndicators?: boolean;
  className?: string;
}

// ============================================================================
// Custom Node and Edge Types
// ============================================================================

const nodeTypes: NodeTypes = {
  resource: ResourceNode as any,
  entity: EntityNode as any,
};

const edgeTypes: EdgeTypes = {
  default: CustomEdge as any,
};

// ============================================================================
// Component
// ============================================================================

export const GraphCanvas = memo<GraphCanvasProps>(({
  nodes,
  edges,
  onNodeClick,
  onEdgeClick,
  onViewportChange,
  selectedNodeId,
  showIndicators = true,
  className,
}) => {
  // Transform nodes to React Flow format
  const reactFlowNodes: Node[] = useMemo(() => {
    return nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: {
        ...node.metadata,
        id: node.id,
        label: node.label,
        showIndicators,
      },
      selected: node.id === selectedNodeId,
    }));
  }, [nodes, selectedNodeId, showIndicators]);

  // Transform edges to React Flow format
  const reactFlowEdges: Edge[] = useMemo(() => {
    return edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'default',
      data: {
        relationshipType: edge.type,
        strength: edge.weight,
        showIndicators,
        ...edge.metadata,
      },
    }));
  }, [edges, showIndicators]);

  // Handle node click
  const handleNodeClick: OnNodeClick = useCallback(
    (event, node) => {
      if (onNodeClick) {
        const graphNode = nodes.find((n) => n.id === node.id);
        if (graphNode) {
          onNodeClick(graphNode);
        }
      }
    },
    [nodes, onNodeClick]
  );

  // Handle edge click
  const handleEdgeClick: OnEdgeClick = useCallback(
    (event, edge) => {
      if (onEdgeClick) {
        const graphEdge = edges.find((e) => e.id === edge.id);
        if (graphEdge) {
          onEdgeClick(graphEdge);
        }
      }
    },
    [edges, onEdgeClick]
  );

  return (
    <div className={className}>
      <ReactFlow
        nodes={reactFlowNodes}
        edges={reactFlowEdges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'resource') return '#3B82F6';
            if (node.type === 'entity') return '#8B5CF6';
            return '#6B7280';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
});

GraphCanvas.displayName = 'GraphCanvas';
