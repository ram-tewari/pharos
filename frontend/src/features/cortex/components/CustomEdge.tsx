/**
 * Custom Edge Component
 * 
 * Custom edge component for graph visualization.
 * Displays edges with varying thickness, colors, and styles based on relationship type.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 5 Custom Edges
 * Task: 5.1
 * 
 * Properties:
 * - Property 2: Edge Thickness Proportionality
 * - Property 12: Hidden Connection Styling
 * - Property 25: Supporting Evidence Icon Display
 */

import { memo } from 'react';
import { type EdgeProps, getBezierPath } from 'reactflow';
import { Check } from 'lucide-react';

// ============================================================================
// Types
// ============================================================================

interface CustomEdgeData {
  relationshipType: 'citation' | 'semantic' | 'entity' | 'hypothesis';
  strength?: number; // 0.0 - 1.0
  isContradiction?: boolean;
  isHiddenConnection?: boolean;
  isResearchGap?: boolean;
  hasSupportingEvidence?: boolean;
  showIndicators?: boolean;
  label?: string;
}

// ============================================================================
// Color Mapping
// ============================================================================

const EDGE_COLORS: Record<CustomEdgeData['relationshipType'], string> = {
  citation: '#6B7280',    // gray
  semantic: '#3B82F6',    // blue
  entity: '#8B5CF6',      // purple
  hypothesis: '#10B981',  // green
};

// ============================================================================
// Component
// ============================================================================

export const CustomEdge = memo<EdgeProps<CustomEdgeData>>(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  // Property 2: Edge Thickness Proportionality (0.0-1.0 → 1px-5px)
  const strokeWidth = data?.strength !== undefined
    ? 1 + (data.strength * 4) // Maps 0.0-1.0 to 1-5px
    : 2;

  // Determine color
  let stroke = data?.relationshipType 
    ? EDGE_COLORS[data.relationshipType]
    : '#6B7280';

  if (data?.isContradiction) {
    stroke = '#EF4444'; // red for contradictions
  }

  // Property 12: Hidden Connection Styling (dashed green)
  const strokeDasharray = data?.isHiddenConnection
    ? '5,5'
    : data?.isResearchGap
    ? '2,2'
    : undefined;

  if (data?.isHiddenConnection) {
    stroke = '#10B981'; // green for hidden connections
  }

  return (
    <>
      {/* Edge path */}
      <path
        id={id}
        className="react-flow__edge-path transition-all duration-200"
        d={edgePath}
        stroke={stroke}
        strokeWidth={selected ? strokeWidth + 2 : strokeWidth}
        strokeDasharray={strokeDasharray}
        fill="none"
        markerEnd="url(#arrowhead)"
      />

      {/* Label */}
      {data?.label && (
        <text
          x={labelX}
          y={labelY}
          className="text-xs fill-current"
          textAnchor="middle"
          dominantBaseline="middle"
        >
          <tspan className="bg-white px-1 py-0.5 rounded">
            {data.label}
          </tspan>
        </text>
      )}

      {/* Property 25: Supporting Evidence Icon */}
      {data?.hasSupportingEvidence && data?.showIndicators !== false && (
        <foreignObject
          width={20}
          height={20}
          x={labelX - 10}
          y={labelY - 10}
        >
          <div className="bg-green-500 rounded-full p-0.5 flex items-center justify-center">
            <Check className="w-3 h-3 text-white" />
          </div>
        </foreignObject>
      )}
    </>
  );
});

CustomEdge.displayName = 'CustomEdge';
