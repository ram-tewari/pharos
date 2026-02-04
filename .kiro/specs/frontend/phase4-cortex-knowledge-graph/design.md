# Design Document: Phase 4 - Cortex Knowledge Graph

## Overview

The Cortex Knowledge Graph is a sophisticated interactive visualization system built with React 18, TypeScript, and React Flow (or D3.js). It transforms the backend graph API into an intuitive visual interface that enables researchers to explore connections, discover hidden relationships through Literature-Based Discovery, and analyze citation networks.

The system consists of multiple view modes (Mind Map, Global Overview, Entity View, Hypothesis Discovery), each optimized for different exploration patterns. The design emphasizes performance, accessibility, and visual polish following the standards in frontend-polish.md.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Graph Page Component                      │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Toolbar       │  │  Graph Canvas│  │  Side Panel     │ │
│  │  - Mode Select │  │  - Nodes     │  │  - Node Details │ │
│  │  - Search      │  │  - Edges     │  │  - Filters      │ │
│  │  - Zoom        │  │  - Minimap   │  │  - Hypotheses   │ │
│  │  - Export      │  │              │  │                 │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    State Management (Zustand)                │
│  - Graph data (nodes, edges)                                 │
│  - View mode (mind-map, global, entity, hypothesis)          │
│  - Selected nodes/edges                                      │
│  - Filters (type, date, quality)                             │
│  - Viewport state (zoom, pan)                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Client Layer                          │
│  - getNeighbors(resourceId)                                  │
│  - getOverview(threshold)                                    │
│  - discoverHypotheses(entityA, entityC)                      │
│  - getEntities()                                             │
│  - getEntityRelationships(entityId)                          │
│  - traverseGraph(startEntity, depth)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend Graph API                         │
│  /api/graph/resource/{id}/neighbors                          │
│  /api/graph/overview                                         │
│  /api/graph/discover                                         │
│  /api/graph/entities                                         │
│  /api/graph/entities/{id}/relationships                      │
│  /api/graph/traverse                                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
GraphPage
├── GraphToolbar
│   ├── ModeSelector (mind-map, global, entity, hypothesis)
│   ├── SearchBar
│   ├── ZoomControls
│   ├── ExportButton
│   └── FilterButton
├── GraphCanvas (React Flow or D3.js)
│   ├── ResourceNode (custom node component)
│   ├── EntityNode (custom node component)
│   ├── CustomEdge (custom edge component)
│   ├── Minimap
│   └── Controls
├── SidePanel
│   ├── NodeDetailsPanel
│   ├── FilterPanel
│   ├── HypothesisPanel
│   └── LegendPanel
└── GraphModals
    ├── ExportModal
    ├── HypothesisDiscoveryModal
    └── SaveViewModal
```

## Components and Interfaces

### 1. GraphPage Component

**Purpose**: Main container component that orchestrates the graph visualization

**Props**: None (uses route params and Zustand store)

**State Management**:
```typescript
interface GraphStore {
  // Data
  nodes: GraphNode[];
  edges: GraphEdge[];
  entities: Entity[];
  
  // View state
  viewMode: 'mind-map' | 'global' | 'entity' | 'hypothesis';
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  
  // Filters
  filters: {
    resourceTypes: ResourceType[];
    dateRange: [Date, Date] | null;
    minQuality: number;
    searchQuery: string;
  };
  
  // Viewport
  viewport: {
    zoom: number;
    x: number;
    y: number;
  };
  
  // Hypotheses
  hypotheses: Hypothesis[];
  
  // Actions
  setViewMode: (mode: ViewMode) => void;
  selectNode: (nodeId: string) => void;
  updateFilters: (filters: Partial<Filters>) => void;
  setViewport: (viewport: Viewport) => void;
  loadNeighbors: (resourceId: string) => Promise<void>;
  loadOverview: (threshold: number) => Promise<void>;
  discoverHypotheses: (entityA: string, entityC: string) => Promise<void>;
}
```

**Responsibilities**:
- Initialize graph data based on view mode
- Handle route parameters (e.g., /graph?resource=123&mode=mind-map)
- Coordinate between toolbar, canvas, and side panel
- Manage keyboard shortcuts
- Handle browser history integration

### 2. GraphCanvas Component

**Purpose**: Renders the interactive graph visualization using React Flow

**Technology Choice**: React Flow (recommended over D3.js for React integration)

**Props**:
```typescript
interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick: (node: GraphNode) => void;
  onEdgeClick: (edge: GraphEdge) => void;
  onViewportChange: (viewport: Viewport) => void;
  selectedNodeId: string | null;
  viewMode: ViewMode;
}
```

**Custom Node Types**:
```typescript
// Resource Node
interface ResourceNodeData {
  id: string;
  title: string;
  resourceType: 'paper' | 'article' | 'book' | 'code';
  qualityScore: number;
  citationCount: number;
  hasContradiction: boolean;
  isHypothesisNode: boolean;
}

// Entity Node
interface EntityNodeData {
  id: string;
  name: string;
  entityType: 'person' | 'concept' | 'organization' | 'location';
  mentionCount: number;
}
```

**Custom Edge Types**:
```typescript
interface CustomEdgeData {
  id: string;
  source: string;
  target: string;
  relationshipType: 'citation' | 'semantic' | 'entity' | 'hypothesis';
  strength: number; // 0.0 - 1.0
  isContradiction: boolean;
  isHiddenConnection: boolean;
  isResearchGap: boolean;
}
```

**Layout Algorithms**:
- **Mind Map**: Radial layout (center node with neighbors in circles)
- **Global Overview**: Force-directed layout (d3-force or React Flow's built-in)
- **Entity View**: Hierarchical layout (entities at top, resources below)
- **Hypothesis**: Custom layout highlighting A→B→C paths

**Performance Optimizations**:
- Virtual rendering for >1000 nodes
- Web worker for layout computation
- Memoized node/edge components
- Debounced viewport updates
- Progressive rendering with loading states

### 3. GraphToolbar Component

**Purpose**: Provides controls for mode selection, search, zoom, and export

**Props**:
```typescript
interface GraphToolbarProps {
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onExport: (format: 'png' | 'svg' | 'json') => void;
  onToggleFilters: () => void;
  activeFilterCount: number;
}
```

**Subcomponents**:

**ModeSelector**:
- Dropdown or tab-style selector
- Icons for each mode (mind-map: brain, global: globe, entity: network, hypothesis: lightbulb)
- Keyboard shortcuts (1-4 for modes)

**SearchBar**:
- Debounced input (300ms)
- Clear button
- Search icon
- Placeholder: "Search resources, entities, or tags..."
- Keyboard shortcut: Cmd/Ctrl + K

**ZoomControls**:
- Zoom in button (+)
- Zoom out button (-)
- Fit to screen button (⊡)
- Zoom percentage display (e.g., "75%")
- Keyboard shortcuts: +, -, 0

**ExportButton**:
- Dropdown menu with options: PNG, SVG, JSON
- Shows export progress modal
- Generates filename with timestamp

**FilterButton**:
- Badge showing active filter count
- Toggles filter panel slide-in
- Icon changes when filters are active

### 4. SidePanel Component

**Purpose**: Displays contextual information based on selection and view mode

**Props**:
```typescript
interface SidePanelProps {
  selectedNode: GraphNode | null;
  selectedEdge: GraphEdge | null;
  viewMode: ViewMode;
  filters: Filters;
  onFiltersChange: (filters: Partial<Filters>) => void;
  hypotheses: Hypothesis[];
  onHypothesisClick: (hypothesis: Hypothesis) => void;
}
```

**Panels**:

**NodeDetailsPanel** (shown when node is selected):
- Resource title and metadata
- Quality score with color-coded badge
- Citation count
- Tags
- "View Details" button (navigates to resource page)
- "View in Mind Map" button (switches to mind-map mode)
- Related entities list

**FilterPanel** (shown when filter button is clicked):
- Resource type checkboxes (paper, article, book, code)
- Date range picker (publication year)
- Quality score slider (0.0 - 1.0)
- "Clear All" button
- "Apply" button
- Slide-in animation from right

**HypothesisPanel** (shown in hypothesis mode):
- List of discovered hypotheses
- Each hypothesis shows:
  - A→B→C path description
  - Confidence score (progress bar)
  - Evidence strength meter
  - Contradiction indicators
  - Research gap indicators
  - "View in Graph" button
- "Discover New" button (opens discovery modal)

**LegendPanel** (always visible, collapsible):
- Node color legend (resource types)
- Edge style legend (relationship types)
- Icon legend (contradiction, research gap, supporting evidence)
- Quality score color gradient

### 5. Custom Node Components

**ResourceNode**:
```typescript
interface ResourceNodeProps {
  data: ResourceNodeData;
  selected: boolean;
}
```

**Visual Design**:
- Circle shape (radius based on citation count)
- Color by resource type:
  - Paper: #3B82F6 (blue)
  - Article: #10B981 (green)
  - Book: #8B5CF6 (purple)
  - Code: #F59E0B (orange)
- Border: 2px solid, thicker when selected
- Quality badge in top-right corner (colored dot)
- Contradiction icon in top-left (red exclamation) if applicable
- Label below node (truncated title)
- Hover: scale(1.05), shadow elevation
- Selected: glow effect, thicker border

**EntityNode**:
```typescript
interface EntityNodeProps {
  data: EntityNodeData;
  selected: boolean;
}
```

**Visual Design**:
- Diamond shape
- Color by entity type:
  - Person: #EC4899 (pink)
  - Concept: #6366F1 (indigo)
  - Organization: #14B8A6 (teal)
  - Location: #F97316 (orange)
- Border: 2px solid
- Label inside diamond
- Hover: scale(1.05)
- Selected: glow effect

### 6. Custom Edge Components

**CustomEdge**:
```typescript
interface CustomEdgeProps {
  data: CustomEdgeData;
  selected: boolean;
}
```

**Visual Design**:
- Stroke width based on strength (1px - 5px)
- Color by relationship type:
  - Citation: #6B7280 (gray)
  - Semantic: #3B82F6 (blue)
  - Entity: #8B5CF6 (purple)
  - Hypothesis: #10B981 (green)
- Style by special type:
  - Hidden connection: dashed line, green
  - Research gap: dotted line, gray
  - Contradiction: solid line, red
- Arrow marker at target end
- Label at midpoint (relationship type)
- Hover: thicker stroke, tooltip
- Selected: animated dash offset

### 7. Minimap Component

**Purpose**: Provides overview of full graph and current viewport

**Props**:
```typescript
interface MinimapProps {
  nodes: GraphNode[];
  viewport: Viewport;
  onViewportChange: (viewport: Viewport) => void;
}
```

**Visual Design**:
- Fixed position in bottom-right corner
- 200x150px size
- Semi-transparent background (backdrop-blur)
- Simplified node rendering (small circles)
- Viewport rectangle (blue border)
- Click to pan to location
- Drag viewport rectangle to pan

### 8. Modal Components

**ExportModal**:
- Format selection (PNG, SVG, JSON)
- Options: full graph vs. current view
- Resolution selection for PNG (1x, 2x, 4x)
- Progress bar during export
- Download button
- Cancel button

**HypothesisDiscoveryModal**:
- Entity A selector (autocomplete)
- Entity C selector (autocomplete)
- "Discover" button
- Loading state with spinner
- Results display (list of hypotheses)
- "View in Graph" for each result

**SaveViewModal**:
- View name input
- Description textarea
- "Save" button
- "Cancel" button
- Saves to local storage or backend

## Data Models

### GraphNode

```typescript
interface GraphNode {
  id: string;
  type: 'resource' | 'entity';
  data: ResourceNodeData | EntityNodeData;
  position: { x: number; y: number };
  style?: React.CSSProperties;
}
```

### GraphEdge

```typescript
interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'citation' | 'semantic' | 'entity' | 'hypothesis';
  data: CustomEdgeData;
  style?: React.CSSProperties;
  animated?: boolean;
}
```

### Hypothesis

```typescript
interface Hypothesis {
  id: string;
  entityA: Entity;
  entityB: Entity[];
  entityC: Entity;
  confidence: number; // 0.0 - 1.0
  evidenceStrength: number; // 0.0 - 1.0
  hasContradiction: boolean;
  isResearchGap: boolean;
  path: {
    aToB: Relationship[];
    bToC: Relationship[];
  };
  description: string;
}
```

### Entity

```typescript
interface Entity {
  id: string;
  name: string;
  type: 'person' | 'concept' | 'organization' | 'location';
  mentionCount: number;
  resources: string[]; // resource IDs
}
```

### Relationship

```typescript
interface Relationship {
  id: string;
  subject: string; // entity ID
  predicate: string; // relationship type
  object: string; // entity ID
  confidence: number;
  sourceChunkId: string;
}
```

### Filters

```typescript
interface Filters {
  resourceTypes: ('paper' | 'article' | 'book' | 'code')[];
  dateRange: [Date, Date] | null;
  minQuality: number;
  searchQuery: string;
}
```

### Viewport

```typescript
interface Viewport {
  zoom: number; // 0.1 - 2.0
  x: number;
  y: number;
}
```

## API Integration

### Graph API Client

```typescript
class GraphAPIClient {
  async getNeighbors(resourceId: string): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    const response = await fetch(`/api/graph/resource/${resourceId}/neighbors`);
    const data = await response.json();
    return transformToGraphData(data);
  }

  async getOverview(threshold: number = 0.5): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    const response = await fetch(`/api/graph/overview?threshold=${threshold}`);
    const data = await response.json();
    return transformToGraphData(data);
  }

  async discoverHypotheses(entityA: string, entityC: string): Promise<Hypothesis[]> {
    const response = await fetch('/api/graph/discover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_a: entityA, entity_c: entityC })
    });
    return response.json();
  }

  async getEntities(): Promise<Entity[]> {
    const response = await fetch('/api/graph/entities');
    return response.json();
  }

  async getEntityRelationships(entityId: string): Promise<Relationship[]> {
    const response = await fetch(`/api/graph/entities/${entityId}/relationships`);
    return response.json();
  }

  async traverseGraph(startEntity: string, depth: number = 2): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    const response = await fetch(`/api/graph/traverse?start=${startEntity}&depth=${depth}`);
    const data = await response.json();
    return transformToGraphData(data);
  }
}
```

### Data Transformation

```typescript
function transformToGraphData(apiData: any): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = apiData.nodes.map((node: any) => ({
    id: node.id,
    type: node.type,
    data: {
      ...node,
      // Add computed properties
      hasContradiction: checkForContradictions(node),
      isHypothesisNode: false
    },
    position: { x: 0, y: 0 } // Will be computed by layout algorithm
  }));

  const edges: GraphEdge[] = apiData.edges.map((edge: any) => ({
    id: `${edge.source}-${edge.target}`,
    source: edge.source,
    target: edge.target,
    type: edge.relationship_type,
    data: {
      ...edge,
      strength: edge.weight || 0.5,
      isContradiction: edge.is_contradiction || false,
      isHiddenConnection: false,
      isResearchGap: false
    }
  }));

  return { nodes, edges };
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

**Redundancy Analysis**:
1. Multiple properties about "UI element presence" (buttons, controls, panels) can be tested as examples rather than properties
2. Hover interactions (nodes, edges, icons) follow the same pattern and can be consolidated
3. Filter application and clearing follow the same visibility pattern
4. Export format options (PNG, SVG, JSON) are variations of the same export functionality
5. API call triggers (mode selection, button clicks) are integration points, not properties
6. Performance requirements (render time, fps) are not testable as properties
7. Animation smoothness and visual polish are subjective, not testable as properties

**Consolidated Properties**:
- Node styling properties (color, size, badges) → Single property about node visual attributes
- Edge styling properties (thickness, color, style) → Single property about edge visual attributes
- Filter properties (type, date, quality) → Single property about filter application
- Keyboard shortcuts → Single property about keyboard event handling
- Accessibility features (ARIA, screen reader, high contrast) → Grouped accessibility properties

### Core Properties

**Property 1: Node Color Mapping**

*For any* resource node in the graph, the node color SHALL match its resource type according to the color scheme (paper: blue, article: green, book: purple, code: orange).

**Validates: Requirements 1.2**

**Property 2: Edge Thickness Proportionality**

*For any* edge in the graph, the stroke width SHALL be proportional to the relationship strength value (0.0-1.0 scale mapped to 1px-5px).

**Validates: Requirements 1.3**

**Property 3: Node Selection State**

*For any* node, when clicked, the node SHALL be marked as selected and the side panel SHALL display its details.

**Validates: Requirements 1.5**

**Property 4: Mind Map Center Node**

*For any* mind map view, the selected resource SHALL be positioned at the center of the layout.

**Validates: Requirements 2.2**

**Property 5: Radial Neighbor Layout**

*For any* mind map with N neighbors, the neighbors SHALL be arranged in a circular pattern around the center node with equal angular spacing (360/N degrees).

**Validates: Requirements 2.3**

**Property 6: Neighbor Count Limit**

*For any* mind map view, the number of displayed neighbors SHALL not exceed the configured limit (default: 20) unless explicitly expanded.

**Validates: Requirements 2.7**

**Property 7: Threshold Filtering**

*For any* global overview with threshold T, all displayed nodes SHALL have a connection strength >= T.

**Validates: Requirements 3.2**

**Property 8: Node Size Proportionality**

*For any* node in global overview mode, the node size SHALL be proportional to its degree centrality (connection count).

**Validates: Requirements 3.4**

**Property 9: Top Connected Highlighting**

*For any* global overview, the 10 nodes with the highest degree centrality SHALL have the highlight style applied.

**Validates: Requirements 3.8**

**Property 10: Hypothesis Ranking**

*For any* list of hypotheses, they SHALL be sorted in descending order by confidence score.

**Validates: Requirements 4.3**

**Property 11: Hypothesis Path Visualization**

*For any* selected hypothesis, the A→B→C path nodes and edges SHALL be highlighted in the graph visualization.

**Validates: Requirements 4.4**

**Property 12: Hidden Connection Styling**

*For any* hypothesis edge representing a hidden connection, the edge SHALL use a dashed green line style.

**Validates: Requirements 4.5**

**Property 13: Contradiction Indicator**

*For any* hypothesis involving contradictions, the affected nodes SHALL display red exclamation icons.

**Validates: Requirements 4.6**

**Property 14: Research Gap Visualization**

*For any* hypothesis revealing a research gap, the missing connection SHALL be displayed as a dotted line.

**Validates: Requirements 4.7**

**Property 15: Search Filtering**

*For any* search query Q, only nodes whose title, author, or tags contain Q (case-insensitive) SHALL be visible.

**Validates: Requirements 5.1**

**Property 16: Search Result Highlighting**

*For any* search query with matching results, the matching nodes SHALL have the highlight style (pulse animation) applied.

**Validates: Requirements 5.2**

**Property 17: Filter Application**

*For any* set of active filters F, only nodes matching ALL filter criteria in F SHALL be visible (AND logic).

**Validates: Requirements 5.7**

**Property 18: Filter Badge Count**

*For any* filter state, the badge count SHALL equal the number of active filters (non-default values).

**Validates: Requirements 5.10**

**Property 19: Entity Node Shape Distinction**

*For any* node in entity view mode, resource nodes SHALL be rendered as circles and entity nodes SHALL be rendered as diamonds.

**Validates: Requirements 6.2**

**Property 20: Semantic Triple Display**

*For any* entity relationship, it SHALL be displayed in subject-predicate-object format.

**Validates: Requirements 6.4**

**Property 21: Traverse Button Visibility**

*For any* graph state, the "Traverse" button SHALL be visible if and only if an entity node is selected.

**Validates: Requirements 6.5**

**Property 22: Traversal Path Highlighting**

*For any* graph traversal result, all nodes and edges in the traversal path SHALL have the highlight style applied.

**Validates: Requirements 6.7**

**Property 23: Relationship Label Display**

*For any* entity edge, the predicate (relationship type) SHALL be displayed as a label on the edge.

**Validates: Requirements 6.8**

**Property 24: Contradiction Icon Display**

*For any* node with detected contradictions, a red exclamation icon SHALL be displayed on the node.

**Validates: Requirements 7.1**

**Property 25: Supporting Evidence Icon Display**

*For any* edge with supporting evidence, a green checkmark icon SHALL be displayed on the edge.

**Validates: Requirements 7.3**

**Property 26: Quality Score Color Mapping**

*For any* node with quality score Q, the badge color SHALL be green if Q > 0.8, yellow if 0.5 <= Q <= 0.8, and red if Q < 0.5.

**Validates: Requirements 7.7**

**Property 27: Indicator Preference Persistence**

*For any* indicator toggle state, the preference SHALL be saved to local storage and restored on page load.

**Validates: Requirements 7.10**

**Property 28: Mouse Wheel Zoom**

*For any* mouse wheel event, the zoom level SHALL increase on wheel up and decrease on wheel down.

**Validates: Requirements 8.2**

**Property 29: Minimap Click Navigation**

*For any* click in the minimap at position (x, y), the viewport SHALL pan to center on that position.

**Validates: Requirements 8.5**

**Property 30: Keyboard Shortcut Handling**

*For any* keyboard shortcut (+ for zoom in, - for zoom out, 0 for fit-to-screen), the corresponding action SHALL be triggered.

**Validates: Requirements 8.7**

**Property 31: Zoom Level Display**

*For any* viewport state, the displayed zoom percentage SHALL equal the actual zoom value * 100.

**Validates: Requirements 8.8**

**Property 32: Virtual Rendering Activation**

*For any* graph with node count > 1000, virtual rendering SHALL be enabled automatically.

**Validates: Requirements 8.9**

**Property 33: Focus Mode Dimming**

*For any* graph in focus mode with selected node S, all nodes except S and its immediate neighbors SHALL have reduced opacity (0.3).

**Validates: Requirements 8.10**

**Property 34: Export Filename Timestamp**

*For any* export operation, the generated filename SHALL include a timestamp in ISO 8601 format.

**Validates: Requirements 9.5**

**Property 35: Export Progress Indicator**

*For any* export operation in progress, a progress indicator SHALL be visible.

**Validates: Requirements 9.7**

**Property 36: Shareable Link State Restoration**

*For any* shareable link with encoded state S, opening the link SHALL restore the viewport, filters, and selected nodes to match S.

**Validates: Requirements 9.9**

**Property 37: Touch Zoom and Pan**

*For any* touch device, pinch gestures SHALL control zoom and swipe gestures SHALL control pan.

**Validates: Requirements 10.1**

**Property 38: Keyboard Navigation**

*For any* keyboard navigation event (Tab, Arrow keys, Enter), the focus SHALL move to the appropriate element and trigger the corresponding action.

**Validates: Requirements 10.4**

**Property 39: ARIA Label Presence**

*For any* interactive element (button, node, edge), an appropriate ARIA label SHALL be present.

**Validates: Requirements 10.5**

**Property 40: Screen Reader Announcements**

*For any* graph update (node added, filter applied, mode changed), an ARIA live region SHALL announce the change to screen readers.

**Validates: Requirements 10.6**

**Property 41: High Contrast Mode**

*For any* system with prefers-contrast: high, the color scheme SHALL use high contrast colors (black/white with minimal grays).

**Validates: Requirements 10.7**

**Property 42: Node Size Adjustment**

*For any* node size setting S, all nodes SHALL be rendered at scale factor S (0.5x to 2.0x).

**Validates: Requirements 10.8**

**Property 43: Reduced Motion Compliance**

*For any* system with prefers-reduced-motion: reduce, all animations SHALL be disabled or reduced to instant transitions.

**Validates: Requirements 10.9**

**Property 44: Minimum Touch Target Size**

*For any* interactive element on touch devices, the touch target size SHALL be at least 44x44px.

**Validates: Requirements 10.10**

**Property 45: Progressive Rendering Activation**

*For any* graph with node count > 500, progressive rendering SHALL be enabled with a loading indicator.

**Validates: Requirements 11.3**

**Property 46: Search Input Debouncing**

*For any* sequence of search input events, the filter function SHALL only be called after 300ms of inactivity.

**Validates: Requirements 11.6**

**Property 47: Graph Data Caching**

*For any* API request for graph data, if the data exists in cache and is less than 5 minutes old, the cached data SHALL be used instead of making a new request.

**Validates: Requirements 11.7**

**Property 48: Lazy Node Details Loading**

*For any* node selection, the detailed node information SHALL only be fetched from the API when the node is selected, not during initial graph load.

**Validates: Requirements 11.9**

**Property 49: Performance Mode Animation Disabling**

*For any* graph in performance mode, all animations SHALL be disabled (transition duration = 0ms).

**Validates: Requirements 11.10**

**Property 50: View Details Button Visibility**

*For any* selected resource node, a "View Details" button SHALL be visible in the side panel.

**Validates: Requirements 12.1**

**Property 51: Annotation Graph Update**

*For any* annotation creation event, the graph SHALL refresh to reflect new semantic connections.

**Validates: Requirements 12.3**

**Property 52: Collection Graph Update**

*For any* collection membership change, the graph SHALL update to reflect the new collection relationships.

**Validates: Requirements 12.4**

**Property 53: Search Result Graph Highlighting**

*For any* "View Results in Graph" action from search, the nodes corresponding to search results SHALL be highlighted.

**Validates: Requirements 12.6**

**Property 54: Browser History Sync**

*For any* graph state change (mode, viewport, filters), the browser URL SHALL be updated to reflect the new state.

**Validates: Requirements 12.7**

**Property 55: Bookmark State Restoration**

*For any* bookmarked graph URL, opening the bookmark SHALL restore the exact graph state (mode, viewport, filters, selected nodes).

**Validates: Requirements 12.8**

## Error Handling

### API Error Handling

**Network Errors**:
- Display toast notification: "Failed to load graph data. Please check your connection."
- Provide "Retry" button
- Cache last successful graph state
- Gracefully degrade to cached data if available

**404 Errors** (Resource not found):
- Display empty state: "Resource not found in graph"
- Suggest returning to global overview
- Provide search functionality to find similar resources

**500 Errors** (Server errors):
- Display toast notification: "Server error. Please try again later."
- Log error details for debugging
- Provide "Report Issue" button

**Timeout Errors**:
- Display toast notification: "Request timed out. The graph may be too large."
- Suggest using filters to reduce graph size
- Provide option to enable performance mode

### User Input Validation

**Search Query**:
- Trim whitespace
- Limit to 100 characters
- Sanitize special characters
- Handle empty queries gracefully (show all nodes)

**Filter Values**:
- Date range: Validate start < end, both are valid dates
- Quality score: Clamp to 0.0-1.0 range
- Resource types: Validate against allowed types

**Hypothesis Discovery**:
- Validate entity A and C are selected
- Validate entities exist in the graph
- Prevent A = C (same entity)
- Display validation errors inline

### Graph Rendering Errors

**Layout Computation Failure**:
- Fall back to simple grid layout
- Display warning: "Advanced layout unavailable, using simple layout"
- Log error for debugging

**Node Rendering Failure**:
- Skip failed node, render others
- Display placeholder for failed node
- Log error with node ID

**Edge Rendering Failure**:
- Skip failed edge, render others
- Log error with edge ID

**Memory Errors** (Too many nodes):
- Automatically enable virtual rendering
- Display warning: "Large graph detected, enabling performance mode"
- Suggest applying filters

### State Management Errors

**Invalid State**:
- Reset to default state
- Display toast: "Invalid state detected, resetting to default view"
- Log error for debugging

**Local Storage Errors**:
- Fall back to in-memory storage
- Display warning: "Unable to save preferences"
- Continue with default preferences

**URL Parameter Errors**:
- Ignore invalid parameters
- Use default values
- Display toast: "Invalid URL parameters, using defaults"

## Testing Strategy

### Dual Testing Approach

The testing strategy combines **unit tests** for specific examples and edge cases with **property-based tests** for universal properties across all inputs. Both are complementary and necessary for comprehensive coverage.

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Integration points between components
- Edge cases (empty states, no neighbors, no search results)
- Error conditions (API failures, invalid input)
- UI element presence (buttons, panels, controls)

**Property Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Visual attribute mappings (color, size, style)
- Filter and search logic
- State management consistency

### Property-Based Testing Configuration

**Library**: fast-check (JavaScript/TypeScript property-based testing library)

**Configuration**:
- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: `// Feature: phase4-cortex-knowledge-graph, Property {number}: {property_text}`

**Example Property Test**:
```typescript
import fc from 'fast-check';

// Feature: phase4-cortex-knowledge-graph, Property 1: Node Color Mapping
test('node colors match resource types', () => {
  fc.assert(
    fc.property(
      fc.record({
        id: fc.string(),
        resourceType: fc.constantFrom('paper', 'article', 'book', 'code'),
        title: fc.string()
      }),
      (resource) => {
        const node = createResourceNode(resource);
        const expectedColor = getColorForType(resource.resourceType);
        expect(node.style.backgroundColor).toBe(expectedColor);
      }
    ),
    { numRuns: 100 }
  );
});
```

### Unit Test Examples

**Component Rendering**:
```typescript
describe('GraphPage', () => {
  it('renders toolbar, canvas, and side panel', () => {
    render(<GraphPage />);
    expect(screen.getByRole('toolbar')).toBeInTheDocument();
    expect(screen.getByTestId('graph-canvas')).toBeInTheDocument();
    expect(screen.getByTestId('side-panel')).toBeInTheDocument();
  });

  it('displays empty state when no nodes exist', () => {
    render(<GraphPage />);
    expect(screen.getByText(/no resources in graph/i)).toBeInTheDocument();
  });
});
```

**User Interactions**:
```typescript
describe('Node Selection', () => {
  it('selects node and shows details on click', async () => {
    const { user } = setup(<GraphCanvas nodes={mockNodes} />);
    const node = screen.getByTestId('node-1');
    
    await user.click(node);
    
    expect(node).toHaveClass('selected');
    expect(screen.getByTestId('node-details-panel')).toBeVisible();
  });
});
```

**API Integration**:
```typescript
describe('Graph API', () => {
  it('fetches neighbors when mind map mode is selected', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ nodes: [], edges: [] });
    global.fetch = mockFetch;
    
    const { user } = setup(<GraphPage />);
    await user.selectOptions(screen.getByRole('combobox'), 'mind-map');
    
    expect(mockFetch).toHaveBeenCalledWith('/api/graph/resource/123/neighbors');
  });
});
```

### Integration Tests

**End-to-End Workflows**:
1. Load graph → Select node → View details → Navigate to resource page
2. Search → Filter results → View in graph → Export as PNG
3. Select hypothesis mode → Discover hypotheses → View path → Save hypothesis
4. Select entity view → Click entity → Traverse graph → Expand neighborhood

**Cross-Feature Integration**:
1. Create annotation → Verify graph updates with new connection
2. Add resource to collection → Verify graph shows collection membership
3. Perform search → Click "View in Graph" → Verify nodes are highlighted

### Accessibility Tests

**Keyboard Navigation**:
```typescript
describe('Keyboard Accessibility', () => {
  it('navigates nodes with Tab key', async () => {
    const { user } = setup(<GraphCanvas nodes={mockNodes} />);
    
    await user.tab();
    expect(screen.getByTestId('node-1')).toHaveFocus();
    
    await user.tab();
    expect(screen.getByTestId('node-2')).toHaveFocus();
  });

  it('zooms with + and - keys', async () => {
    const { user } = setup(<GraphCanvas />);
    const initialZoom = getZoomLevel();
    
    await user.keyboard('+');
    expect(getZoomLevel()).toBeGreaterThan(initialZoom);
    
    await user.keyboard('-');
    expect(getZoomLevel()).toBe(initialZoom);
  });
});
```

**Screen Reader Support**:
```typescript
describe('Screen Reader Accessibility', () => {
  it('announces graph updates to screen readers', async () => {
    const { user } = setup(<GraphPage />);
    
    await user.click(screen.getByText('Apply Filters'));
    
    const liveRegion = screen.getByRole('status');
    expect(liveRegion).toHaveTextContent(/filtered to \d+ nodes/i);
  });
});
```

### Performance Tests

**Render Performance**:
```typescript
describe('Graph Performance', () => {
  it('renders 100 nodes within 500ms', async () => {
    const nodes = generateMockNodes(100);
    const startTime = performance.now();
    
    render(<GraphCanvas nodes={nodes} />);
    await waitFor(() => screen.getAllByTestId(/node-/));
    
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(500);
  });

  it('enables virtual rendering for 1000+ nodes', () => {
    const nodes = generateMockNodes(1500);
    render(<GraphCanvas nodes={nodes} />);
    
    expect(screen.getByTestId('graph-canvas')).toHaveAttribute('data-virtual-rendering', 'true');
  });
});
```

### Visual Regression Tests

**Snapshot Testing**:
```typescript
describe('Graph Visual Regression', () => {
  it('matches snapshot for mind map layout', () => {
    const { container } = render(<GraphCanvas mode="mind-map" nodes={mockNodes} />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot for hypothesis mode with contradictions', () => {
    const { container } = render(<GraphCanvas mode="hypothesis" hypotheses={mockHypotheses} />);
    expect(container).toMatchSnapshot();
  });
});
```

### Test Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Property Tests**: All 55 properties implemented
- **Integration Tests**: All major workflows covered
- **Accessibility Tests**: WCAG 2.1 AA compliance
- **Performance Tests**: All performance requirements validated

## Implementation Notes

### Technology Stack

**Core Libraries**:
- React 18 with TypeScript
- React Flow (graph visualization)
- TanStack Router (routing)
- Zustand (state management)
- TanStack Query (API data fetching)

**Utility Libraries**:
- fast-check (property-based testing)
- Vitest (unit testing)
- React Testing Library (component testing)
- html-to-image (PNG export)
- file-saver (file downloads)

### React Flow Customization

**Custom Node Types**:
```typescript
const nodeTypes = {
  resource: ResourceNode,
  entity: EntityNode
};
```

**Custom Edge Types**:
```typescript
const edgeTypes = {
  citation: CustomEdge,
  semantic: CustomEdge,
  entity: CustomEdge,
  hypothesis: CustomEdge
};
```

**Layout Algorithms**:
- Use `dagre` for hierarchical layouts
- Use `d3-force` for force-directed layouts
- Implement custom radial layout for mind maps

### Performance Optimizations

**Memoization**:
```typescript
const MemoizedResourceNode = React.memo(ResourceNode);
const MemoizedCustomEdge = React.memo(CustomEdge);
```

**Virtual Rendering**:
```typescript
// Only render nodes in viewport + buffer
const visibleNodes = nodes.filter(node => 
  isInViewport(node.position, viewport, buffer)
);
```

**Web Worker for Layout**:
```typescript
// Offload layout computation to web worker
const layoutWorker = new Worker('layout-worker.js');
layoutWorker.postMessage({ nodes, edges, algorithm: 'force' });
layoutWorker.onmessage = (e) => {
  setNodes(e.data.nodes);
};
```

**Debouncing**:
```typescript
const debouncedSearch = useMemo(
  () => debounce((query: string) => filterNodes(query), 300),
  []
);
```

### Accessibility Implementation

**ARIA Labels**:
```typescript
<button aria-label="Zoom in" onClick={handleZoomIn}>
  <PlusIcon />
</button>
```

**ARIA Live Regions**:
```typescript
<div role="status" aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>
```

**Keyboard Shortcuts**:
```typescript
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === '+') handleZoomIn();
    if (e.key === '-') handleZoomOut();
    if (e.key === '0') handleFitView();
  };
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

**Reduced Motion**:
```typescript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const transitionDuration = prefersReducedMotion ? 0 : 300;
```

### State Management with Zustand

```typescript
const useGraphStore = create<GraphStore>((set, get) => ({
  nodes: [],
  edges: [],
  viewMode: 'global',
  selectedNodeId: null,
  filters: {
    resourceTypes: ['paper', 'article', 'book', 'code'],
    dateRange: null,
    minQuality: 0,
    searchQuery: ''
  },
  viewport: { zoom: 1, x: 0, y: 0 },
  
  setViewMode: (mode) => set({ viewMode: mode }),
  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),
  updateFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),
  setViewport: (viewport) => set({ viewport }),
  
  loadNeighbors: async (resourceId) => {
    const data = await graphAPI.getNeighbors(resourceId);
    set({ nodes: data.nodes, edges: data.edges });
  },
  
  loadOverview: async (threshold) => {
    const data = await graphAPI.getOverview(threshold);
    set({ nodes: data.nodes, edges: data.edges });
  }
}));
```

### Routing with TanStack Router

```typescript
const graphRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/graph',
  component: GraphPage,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      mode: search.mode as ViewMode || 'global',
      resource: search.resource as string || null,
      filters: search.filters as string || null
    };
  }
});
```

### Export Functionality

**PNG Export**:
```typescript
import { toPng } from 'html-to-image';

async function exportAsPNG() {
  const element = document.getElementById('graph-canvas');
  const dataUrl = await toPng(element, { quality: 1.0, pixelRatio: 2 });
  const link = document.createElement('a');
  link.download = `graph-${new Date().toISOString()}.png`;
  link.href = dataUrl;
  link.click();
}
```

**SVG Export**:
```typescript
import { toSvg } from 'html-to-image';

async function exportAsSVG() {
  const element = document.getElementById('graph-canvas');
  const dataUrl = await toSvg(element);
  const link = document.createElement('a');
  link.download = `graph-${new Date().toISOString()}.svg`;
  link.href = dataUrl;
  link.click();
}
```

**JSON Export**:
```typescript
function exportAsJSON() {
  const { nodes, edges } = useGraphStore.getState();
  const data = JSON.stringify({ nodes, edges }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  saveAs(blob, `graph-${new Date().toISOString()}.json`);
}
```

### Browser History Integration

```typescript
useEffect(() => {
  const { viewMode, viewport, filters, selectedNodeId } = useGraphStore.getState();
  const params = new URLSearchParams({
    mode: viewMode,
    zoom: viewport.zoom.toString(),
    x: viewport.x.toString(),
    y: viewport.y.toString(),
    filters: JSON.stringify(filters),
    selected: selectedNodeId || ''
  });
  window.history.pushState({}, '', `?${params.toString()}`);
}, [viewMode, viewport, filters, selectedNodeId]);
```

## Future Enhancements

### Phase 4.1: Advanced Graph Analytics
- Centrality metrics (betweenness, closeness, eigenvector)
- Community detection algorithms
- Path analysis (shortest path, all paths)
- Influence propagation simulation

### Phase 4.2: Collaborative Features
- Shared graph views with real-time updates
- Collaborative annotations on graph
- Team workspaces with shared hypotheses
- Comment threads on nodes and edges

### Phase 4.3: AI-Powered Insights
- Automatic hypothesis generation
- Anomaly detection in citation patterns
- Trend analysis over time
- Predictive modeling for research directions

### Phase 4.4: Advanced Visualizations
- 3D graph visualization
- Timeline view for temporal analysis
- Heatmap overlays for metrics
- Animated graph evolution over time

### Phase 4.5: Integration Enhancements
- Zotero integration for citation management
- Mendeley integration for reference libraries
- Export to Obsidian graph format
- Import from other knowledge graph tools
