/**
 * Entity Node Component
 * 
 * Custom node component for entity nodes in the graph visualization.
 * Displays entities as diamond shapes with color-coded backgrounds.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 4 Custom Nodes
 * Task: 4.4
 * 
 * Properties:
 * - Property 19: Entity Node Shape Distinction
 */

import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface EntityNodeData {
  id: string;
  label: string;
  entityType: 'person' | 'concept' | 'organization' | 'location';
  mentionCount?: number;
  metadata?: Record<string, unknown>;
}

interface EntityNodeProps {
  data: EntityNodeData;
  selected: boolean;
}

// ============================================================================
// Color Mapping
// ============================================================================

const ENTITY_COLORS: Record<EntityNodeData['entityType'], string> = {
  person: '#EC4899',       // pink
  concept: '#6366F1',      // indigo
  organization: '#14B8A6', // teal
  location: '#F97316',     // orange
};

// ============================================================================
// Component (Property 19: Diamond Shape)
// ============================================================================

export const EntityNode = memo<EntityNodeProps>(({ data, selected }) => {
  const backgroundColor = ENTITY_COLORS[data.entityType];
  const opacity = (data.metadata?.opacity as number | undefined) ?? 1.0;

  return (
    <div className="relative">
      {/* Handles for connections */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />

      {/* Diamond shape */}
      <div
        className={cn(
          'relative transition-all duration-200',
          'hover:scale-105',
          selected && 'ring-4 ring-primary ring-offset-2'
        )}
        style={{
          width: 80,
          height: 80,
          transform: 'rotate(45deg)',
          backgroundColor,
          border: `2px solid ${backgroundColor}`,
          opacity,
        }}
      >
        {/* Label (counter-rotated to be readable) */}
        <div
          className="absolute inset-0 flex items-center justify-center text-white font-medium text-sm"
          style={{
            transform: 'rotate(-45deg)',
          }}
        >
          <span className="max-w-[60px] truncate text-center" title={data.label}>
            {data.label}
          </span>
        </div>
      </div>
    </div>
  );
});

EntityNode.displayName = 'EntityNode';
