/**
 * Resource Node Component
 * 
 * Custom node component for resource nodes in the graph visualization.
 * Displays resource with color-coded background, quality badge, and metadata.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 4 Custom Nodes
 * Task: 4.1
 * 
 * Properties:
 * - Property 1: Node Color Mapping
 * - Property 26: Quality Score Color Mapping
 * - Property 24: Contradiction Icon Display
 */

import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface ResourceNodeData {
  id: string;
  label: string;
  resourceType: 'paper' | 'article' | 'book' | 'code';
  qualityScore?: number;
  citationCount?: number;
  hasContradiction?: boolean;
  showIndicators?: boolean;
  opacity?: number;
  metadata?: Record<string, unknown>;
}

interface ResourceNodeProps {
  data: ResourceNodeData;
  selected: boolean;
}

// ============================================================================
// Color Mapping (Property 1)
// ============================================================================

const RESOURCE_COLORS: Record<ResourceNodeData['resourceType'], string> = {
  paper: '#3B82F6',    // blue
  article: '#10B981',  // green
  book: '#8B5CF6',     // purple
  code: '#F59E0B',     // orange
};

// ============================================================================
// Quality Score Color Mapping (Property 26)
// ============================================================================

function getQualityColor(score: number): string {
  if (score > 0.8) return '#10B981'; // green
  if (score >= 0.5) return '#F59E0B'; // yellow
  return '#EF4444'; // red
}

// ============================================================================
// Component
// ============================================================================

export const ResourceNode = memo<ResourceNodeProps>(({ data, selected }) => {
  const backgroundColor = RESOURCE_COLORS[data.resourceType];
  const qualityColor = data.qualityScore !== undefined 
    ? getQualityColor(data.qualityScore) 
    : undefined;
  const opacity = data.opacity !== undefined ? data.opacity : 1.0;

  return (
    <div
      className={cn(
        'relative rounded-full transition-all duration-200',
        'hover:scale-105 hover:shadow-lg',
        selected && 'ring-4 ring-primary ring-offset-2 shadow-xl'
      )}
      style={{
        width: 80 + (data.citationCount || 0) * 2, // Size based on citations
        height: 80 + (data.citationCount || 0) * 2,
        backgroundColor,
        border: `${selected ? 4 : 2}px solid ${backgroundColor}`,
        opacity,
      }}
    >
      {/* Handles for connections */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />

      {/* Contradiction Icon (Property 24) */}
      {data.hasContradiction && data.showIndicators !== false && (
        <div
          className="absolute -top-2 -left-2 bg-red-500 rounded-full p-1"
          title="Contradiction detected"
        >
          <AlertTriangle className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Quality Badge (Property 26) */}
      {qualityColor && (
        <div
          className="absolute -top-2 -right-2 rounded-full border-2 border-white"
          style={{
            width: 16,
            height: 16,
            backgroundColor: qualityColor,
          }}
          title={`Quality: ${(data.qualityScore! * 100).toFixed(0)}%`}
        />
      )}

      {/* Label */}
      <div
        className="absolute top-full left-1/2 -translate-x-1/2 mt-2 text-sm font-medium text-center max-w-[120px] truncate"
        title={data.label}
      >
        {data.label}
      </div>
    </div>
  );
});

ResourceNode.displayName = 'ResourceNode';
