# Cortex Knowledge Graph Feature

## Overview

The Cortex Knowledge Graph is an interactive visualization system that enables researchers to explore connections between resources, discover hidden relationships through Literature-Based Discovery (LBD), and analyze citation networks.

## Architecture

```
cortex/
├── components/          # React components
│   ├── GraphPage.tsx           # Main page orchestrator
│   ├── GraphCanvas.tsx         # React Flow canvas
│   ├── GraphToolbar.tsx        # Toolbar with controls
│   ├── ResourceNode.tsx        # Resource node component
│   ├── EntityNode.tsx          # Entity node component
│   └── CustomEdge.tsx          # Custom edge component
├── hooks/              # Custom hooks (planned)
├── stores/             # Feature-specific stores (planned)
├── types/              # TypeScript types
├── utils/              # Utility functions (planned)
└── __tests__/          # Tests
    └── graph.properties.test.ts
```

## Components

### GraphPage
Main container component that orchestrates the graph visualization.

**Features**:
- Loads graph data from API
- Applies layout algorithms
- Handles keyboard shortcuts (+, -, 0)
- Manages loading and error states

**Usage**:
```tsx
import { GraphPage } from '@/features/cortex/components';

// Rendered at /cortex route
<GraphPage />
```

### GraphCanvas
React Flow canvas for rendering the graph.

**Props**:
- `nodes` - Array of graph nodes
- `edges` - Array of graph edges
- `onNodeClick` - Node click handler
- `onEdgeClick` - Edge click handler
- `selectedNodeId` - Currently selected node ID

**Features**:
- Custom node types (resource, entity)
- Custom edge rendering
- Minimap
- Zoom/pan controls
- Background grid

### GraphToolbar
Toolbar with controls for mode selection, search, zoom, and export.

**Props**:
- `viewMode` - Current visualization mode
- `onViewModeChange` - Mode change handler
- `searchQuery` - Current search query
- `onSearchChange` - Search change handler
- `zoom` - Current zoom level
- `onZoomIn/Out/FitView` - Zoom handlers
- `onExport` - Export handler
- `onToggleFilters` - Filter toggle handler
- `activeFilterCount` - Number of active filters

### ResourceNode
Custom node component for resources (papers, articles, books, code).

**Features**:
- Color-coded by resource type
- Quality score badge
- Contradiction indicator
- Size based on citation count
- Hover and selected states

**Colors**:
- Paper: Blue (#3B82F6)
- Article: Green (#10B981)
- Book: Purple (#8B5CF6)
- Code: Orange (#F59E0B)

### EntityNode
Custom node component for entities (people, concepts, organizations, locations).

**Features**:
- Diamond shape
- Color-coded by entity type
- Label inside diamond
- Hover and selected states

**Colors**:
- Person: Pink (#EC4899)
- Concept: Indigo (#6366F1)
- Organization: Teal (#14B8A6)
- Location: Orange (#F97316)

### CustomEdge
Custom edge component for relationships.

**Features**:
- Thickness based on relationship strength
- Color-coded by relationship type
- Special styles for hidden connections, contradictions, research gaps
- Supporting evidence icons
- Relationship labels

**Colors**:
- Citation: Gray (#6B7280)
- Semantic: Blue (#3B82F6)
- Entity: Purple (#8B5CF6)
- Hypothesis: Green (#10B981)

## State Management

Uses Zustand store (`useGraphStore`) for graph state:

```tsx
import { useGraphStore } from '@/stores/graph';

const {
  nodes,
  edges,
  selectedNodes,
  visualizationMode,
  zoomLevel,
  setGraphData,
  selectNode,
  zoomIn,
  zoomOut,
} = useGraphStore();
```

## API Integration

Uses Graph API client for data fetching:

```tsx
import { graphAPI } from '@/lib/api/graph';

// Get neighbors
const data = await graphAPI.getNeighbors('resource_123');

// Get overview
const data = await graphAPI.getOverview(0.5);

// Discover hypotheses
const hypotheses = await graphAPI.discoverHypotheses('entity_a', 'entity_c');
```

## Layout Algorithms

Multiple layout algorithms for different view modes:

```tsx
import { applyLayout, applyRadialLayout } from '@/lib/graph/layouts';

// Force-directed layout
const layoutedNodes = applyLayout(nodes, edges, 'force_directed');

// Radial layout for mind map
const layoutedNodes = applyRadialLayout(nodes, edges, centerNodeId);

// Hierarchical layout
const layoutedNodes = applyLayout(nodes, edges, 'hierarchical');
```

## Keyboard Shortcuts

- `+` or `=` - Zoom in
- `-` or `_` - Zoom out
- `0` - Fit to screen / Reset zoom

## Testing

### Property-Based Tests

Uses fast-check for property-based testing:

```bash
npm test -- graph.properties.test.ts
```

**Properties Tested**:
1. Node Color Mapping
2. Edge Thickness Proportionality
4. Mind Map Center Node
5. Radial Neighbor Layout
26. Quality Score Color Mapping
31. Zoom Level Display
32. Virtual Rendering Activation
46. Search Input Debouncing

## Visualization Modes

### City Map (Default)
High-level clusters showing knowledge domains.

### Blast Radius
Refactoring impact analysis showing affected nodes.

### Dependency Waterfall
Data flow DAG showing dependencies.

### Hypothesis
Literature-Based Discovery with A→B→C paths.

## Future Enhancements

### Planned Features
- [ ] Side panel with node details
- [ ] Filter panel (resource type, date, quality)
- [ ] Hypothesis discovery UI
- [ ] Search filtering and highlighting
- [ ] Export functionality (PNG, SVG, JSON)
- [ ] Entity traversal
- [ ] Focus mode
- [ ] Virtual rendering for large graphs
- [ ] Mobile touch controls

### Advanced Features
- [ ] Contradiction detection
- [ ] Research gap identification
- [ ] Supporting evidence visualization
- [ ] Community detection
- [ ] Centrality metrics
- [ ] Path analysis

## Performance

### Optimizations
- React.memo for all components
- Debounced search (300ms)
- Planned: Virtual rendering for >1000 nodes
- Planned: Web worker for layout computation
- Planned: Progressive rendering for >500 nodes

### Targets
- <500ms render time for <100 nodes
- <2s render time for 100-500 nodes
- 60fps for pan/zoom operations

## Accessibility

### Planned Features
- Keyboard navigation (Tab, Arrow keys, Enter)
- ARIA labels for all interactive elements
- ARIA live regions for announcements
- High contrast mode support
- Reduced motion support
- Minimum 44x44px touch targets

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (touch controls planned)

## Dependencies

- `reactflow` - Graph visualization library
- `d3` - Force-directed layout
- `dagre` - Hierarchical layout
- `fast-check` - Property-based testing
- `zustand` - State management

## Related Documentation

- [Phase 4 Spec](.kiro/specs/frontend/phase4-cortex-knowledge-graph/)
- [Implementation Summary](../../PHASE4_IMPLEMENTATION_SUMMARY.md)
- [Graph Types](../../types/graph.ts)
- [Graph Store](../../stores/graph.ts)
