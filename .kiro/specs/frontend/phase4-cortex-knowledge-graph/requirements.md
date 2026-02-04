# Requirements Document: Phase 4 - Cortex Knowledge Graph

## Introduction

The Cortex Knowledge Graph is an interactive visualization system that enables researchers to explore connections between resources, discover hidden relationships through Literature-Based Discovery (LBD), and analyze citation networks. This feature transforms the backend graph API into a stunning, interactive visual interface that reveals the semantic structure of a researcher's knowledge base.

## Glossary

- **Knowledge_Graph**: A network of resources, entities, and their relationships represented as nodes and edges
- **Resource_Node**: A visual representation of a resource (paper, article, book, code) in the graph
- **Entity_Node**: A visual representation of a semantic entity (person, concept, organization) extracted from content
- **Edge**: A visual connection between nodes representing relationships (citations, semantic similarity, shared entities)
- **Mind_Map_View**: A focused visualization showing a resource and its immediate neighbors
- **Global_Overview**: A visualization of the strongest connections across the entire knowledge base
- **LBD_Mode**: Literature-Based Discovery mode using ABC pattern (A→B, B→C, discover A→C)
- **Hypothesis**: A potential hidden connection discovered through LBD analysis
- **Contradiction**: Two resources with conflicting claims or findings
- **Research_Gap**: A missing connection or unexplored area identified by the system
- **Semantic_Triple**: A subject-predicate-object relationship extracted from text
- **Graph_Traversal**: Navigation through the graph following entity relationships
- **Hybrid_Neighbor**: A resource connected through multiple relationship types (citations, semantic similarity, shared entities)

## Requirements

### Requirement 1: Interactive Graph Visualization

**User Story:** As a researcher, I want to visualize the knowledge graph of my library, so that I can see connections between resources and understand the structure of my knowledge base.

#### Acceptance Criteria

1. WHEN the graph page loads, THE System SHALL render an interactive graph visualization with all resources as nodes
2. WHEN displaying resource nodes, THE System SHALL color-code nodes by resource type (paper: blue, article: green, book: purple, code: orange)
3. WHEN displaying edges, THE System SHALL vary edge thickness based on relationship strength (0.1-1.0 scale)
4. WHEN a user hovers over a node, THE System SHALL highlight the node and display a tooltip with resource title and metadata
5. WHEN a user clicks a node, THE System SHALL select it and display detailed information in a side panel
6. WHEN a user hovers over an edge, THE System SHALL display a tooltip with relationship type and strength
7. THE System SHALL provide zoom controls (zoom in, zoom out, fit to screen)
8. THE System SHALL provide pan controls (drag to pan, mouse wheel to zoom)
9. WHEN the graph layout changes, THE System SHALL animate transitions smoothly over 300-500ms
10. THE System SHALL render graphs with up to 1000 nodes without performance degradation

### Requirement 2: Mind Map View

**User Story:** As a researcher, I want to explore neighbors of a resource in a mind-map view, so that I can discover related content and understand local connections.

#### Acceptance Criteria

1. WHEN a user selects "Mind Map" mode and chooses a resource, THE System SHALL fetch hybrid neighbors from the API
2. WHEN displaying the mind map, THE System SHALL place the selected resource at the center
3. WHEN displaying neighbors, THE System SHALL arrange them in a radial layout around the center
4. WHEN displaying neighbor connections, THE System SHALL show relationship types (citation, semantic similarity, shared entity)
5. WHEN a user clicks a neighbor node, THE System SHALL re-center the mind map on that resource
6. WHEN the mind map updates, THE System SHALL animate the transition with smooth node movements
7. THE System SHALL limit the mind map to 20 neighbors by default with an option to expand
8. WHEN no neighbors exist, THE System SHALL display an empty state with a helpful message

### Requirement 3: Global Overview

**User Story:** As a researcher, I want to see the global overview of strongest connections, so that I can identify key resources and central topics in my knowledge base.

#### Acceptance Criteria

1. WHEN a user selects "Global Overview" mode, THE System SHALL fetch the overview from the API
2. WHEN displaying the overview, THE System SHALL show only resources with connection strength above a threshold (default: 0.5)
3. WHEN displaying the overview, THE System SHALL use a force-directed layout algorithm
4. WHEN displaying nodes, THE System SHALL size nodes proportionally to their connection count (degree centrality)
5. WHEN displaying the overview, THE System SHALL cluster related resources visually
6. THE System SHALL provide a slider to adjust the connection strength threshold
7. WHEN the threshold changes, THE System SHALL update the graph with smooth fade-in/fade-out animations
8. THE System SHALL highlight the top 10 most connected resources with a subtle glow effect

### Requirement 4: Hypothesis Discovery (LBD Mode)

**User Story:** As a researcher, I want to discover hidden connections using ABC pattern (Literature-Based Discovery), so that I can generate research hypotheses and find novel insights.

#### Acceptance Criteria

1. WHEN a user selects "Hypothesis Discovery" mode, THE System SHALL display a form to select A and C entities
2. WHEN a user submits the discovery request, THE System SHALL call the /api/graph/discover endpoint
3. WHEN hypotheses are returned, THE System SHALL display them in a ranked list with confidence scores
4. WHEN displaying a hypothesis, THE System SHALL visualize the A→B→C path in the graph
5. WHEN displaying hypothesis paths, THE System SHALL use dashed green lines for hidden connections
6. WHEN a hypothesis involves contradictions, THE System SHALL mark them with red exclamation icons
7. WHEN a hypothesis reveals a research gap, THE System SHALL highlight the missing connection with a dotted line
8. WHEN a user clicks a hypothesis, THE System SHALL zoom to the relevant subgraph with smooth animation
9. THE System SHALL provide an evidence strength meter (progress bar) for each hypothesis
10. THE System SHALL allow users to save promising hypotheses for later review

### Requirement 5: Search and Filtering

**User Story:** As a researcher, I want to filter and search the graph, so that I can focus on specific topics, resource types, or time periods.

#### Acceptance Criteria

1. WHEN a user types in the search box, THE System SHALL filter nodes by title, author, or tags
2. WHEN search results are found, THE System SHALL highlight matching nodes with a pulse animation
3. WHEN no search results are found, THE System SHALL display a message and suggest clearing filters
4. THE System SHALL provide filter controls for resource type (paper, article, book, code)
5. THE System SHALL provide filter controls for date range (publication year)
6. THE System SHALL provide filter controls for quality score (minimum threshold)
7. WHEN filters are applied, THE System SHALL fade out non-matching nodes and edges
8. WHEN filters are cleared, THE System SHALL fade in all nodes with smooth animation
9. THE System SHALL display a filter panel that slides in from the right with smooth animation
10. THE System SHALL show active filter count as a badge on the filter button

### Requirement 6: Entity-Relationship View

**User Story:** As a researcher, I want to see entity relationships and traverse the graph, so that I can understand semantic connections and explore knowledge at a conceptual level.

#### Acceptance Criteria

1. WHEN a user selects "Entity View" mode, THE System SHALL fetch entities from the API
2. WHEN displaying entities, THE System SHALL render them as distinct node shapes (circles for resources, diamonds for entities)
3. WHEN a user clicks an entity node, THE System SHALL fetch its relationships from the API
4. WHEN displaying entity relationships, THE System SHALL show semantic triples (subject-predicate-object)
5. WHEN a user selects a starting entity, THE System SHALL provide a "Traverse" button
6. WHEN a user clicks "Traverse", THE System SHALL call the /api/graph/traverse endpoint
7. WHEN displaying traversal results, THE System SHALL highlight the path with animated edges
8. THE System SHALL display relationship labels on edges (e.g., "authored_by", "cites", "mentions")
9. WHEN a user hovers over a relationship edge, THE System SHALL display the predicate in a tooltip
10. THE System SHALL allow users to expand/collapse entity neighborhoods

### Requirement 7: Visual Indicators and Annotations

**User Story:** As a researcher, I want to see contradictions, supporting evidence, and research gaps highlighted in the graph, so that I can quickly identify important patterns and anomalies.

#### Acceptance Criteria

1. WHEN a contradiction is detected, THE System SHALL mark the involved nodes with red exclamation icons
2. WHEN a user hovers over a contradiction icon, THE System SHALL display a tooltip explaining the conflict
3. WHEN supporting evidence exists, THE System SHALL mark edges with green checkmark icons
4. WHEN a research gap is identified, THE System SHALL display a dotted line with a question mark icon
5. WHEN a user clicks a research gap indicator, THE System SHALL suggest related resources to fill the gap
6. THE System SHALL use color-coded badges for node metadata (quality score, citation count)
7. WHEN displaying quality scores, THE System SHALL use a color gradient (green >0.8, yellow 0.5-0.8, red <0.5)
8. THE System SHALL display a legend explaining all visual indicators and color codes
9. WHEN a user toggles indicators on/off, THE System SHALL update the graph with smooth fade animations
10. THE System SHALL persist indicator preferences in local storage

### Requirement 8: Graph Controls and Navigation

**User Story:** As a researcher, I want intuitive controls for navigating the graph, so that I can efficiently explore large knowledge bases without getting lost.

#### Acceptance Criteria

1. THE System SHALL provide a toolbar with zoom in, zoom out, and fit-to-screen buttons
2. THE System SHALL support mouse wheel zoom with smooth scaling transitions
3. THE System SHALL support click-and-drag panning
4. THE System SHALL provide a minimap showing the current viewport position in the full graph
5. WHEN a user clicks in the minimap, THE System SHALL pan to that location with smooth animation
6. THE System SHALL provide a "Reset View" button to return to the default layout
7. THE System SHALL provide keyboard shortcuts (+ for zoom in, - for zoom out, 0 for fit-to-screen)
8. THE System SHALL display current zoom level as a percentage in the toolbar
9. WHEN the graph is too large, THE System SHALL enable virtual rendering to maintain performance
10. THE System SHALL provide a "Focus Mode" that dims non-selected nodes and edges

### Requirement 9: Export and Sharing

**User Story:** As a researcher, I want to export the graph as an image or data file, so that I can share visualizations in presentations or publications.

#### Acceptance Criteria

1. THE System SHALL provide an "Export" button in the toolbar
2. WHEN a user clicks "Export as PNG", THE System SHALL generate a high-resolution image of the current view
3. WHEN a user clicks "Export as SVG", THE System SHALL generate a scalable vector graphic
4. WHEN a user clicks "Export as JSON", THE System SHALL export the graph data structure
5. WHEN exporting, THE System SHALL include a timestamp and graph metadata in the filename
6. THE System SHALL provide options to export the full graph or current viewport only
7. WHEN exporting, THE System SHALL show a progress indicator for large graphs
8. THE System SHALL allow users to copy a shareable link to the current graph view
9. WHEN a shareable link is opened, THE System SHALL restore the exact view state (zoom, pan, filters)
10. THE System SHALL provide an option to export selected nodes and their connections only

### Requirement 10: Responsive Design and Accessibility

**User Story:** As a researcher, I want the graph to work on different devices and be accessible, so that I can explore my knowledge base anywhere and ensure inclusive access.

#### Acceptance Criteria

1. WHEN viewed on mobile devices, THE System SHALL provide touch-friendly controls (pinch to zoom, swipe to pan)
2. WHEN viewed on tablets, THE System SHALL optimize the layout for medium-sized screens
3. WHEN viewed on desktop, THE System SHALL utilize the full screen with side panels
4. THE System SHALL support keyboard navigation (Tab to focus nodes, Enter to select, Arrow keys to pan)
5. THE System SHALL provide ARIA labels for all interactive elements
6. THE System SHALL announce graph updates to screen readers using ARIA live regions
7. THE System SHALL support high contrast mode for visually impaired users
8. THE System SHALL allow users to adjust node and text sizes for readability
9. WHEN a user enables reduced motion, THE System SHALL disable animations
10. THE System SHALL maintain a minimum touch target size of 44x44px for mobile interactions

### Requirement 11: Performance and Scalability

**User Story:** As a researcher, I want the graph to load quickly and remain responsive, so that I can work efficiently with large knowledge bases.

#### Acceptance Criteria

1. WHEN loading a graph with <100 nodes, THE System SHALL render within 500ms
2. WHEN loading a graph with 100-500 nodes, THE System SHALL render within 2 seconds
3. WHEN loading a graph with >500 nodes, THE System SHALL use progressive rendering with a loading indicator
4. THE System SHALL implement virtual rendering for graphs with >1000 nodes
5. WHEN panning or zooming, THE System SHALL maintain 60fps performance
6. THE System SHALL debounce search input to avoid excessive API calls (300ms delay)
7. THE System SHALL cache graph data in memory to avoid redundant API requests
8. WHEN the graph layout is computed, THE System SHALL use a web worker to avoid blocking the UI
9. THE System SHALL lazy-load node details when a node is selected
10. THE System SHALL provide a performance mode that disables animations for very large graphs

### Requirement 12: Integration with Other Features

**User Story:** As a researcher, I want the graph to integrate with other Neo Alexandria features, so that I can seamlessly navigate between different views of my knowledge base.

#### Acceptance Criteria

1. WHEN a user clicks a resource node, THE System SHALL provide a "View Details" button that navigates to the resource detail page
2. WHEN viewing a resource detail page, THE System SHALL provide a "View in Graph" button that opens the graph centered on that resource
3. WHEN a user creates an annotation, THE System SHALL update the graph to reflect new semantic connections
4. WHEN a user adds a resource to a collection, THE System SHALL update the graph to show collection membership
5. WHEN a user performs a search, THE System SHALL provide an option to "View Results in Graph"
6. WHEN viewing search results in the graph, THE System SHALL highlight matching nodes
7. THE System SHALL sync graph state with browser history (back/forward navigation)
8. WHEN a user bookmarks a graph view, THE System SHALL restore the exact state when revisited
9. THE System SHALL provide a "Recent Views" dropdown showing the last 5 graph explorations
10. THE System SHALL allow users to open multiple graph views in separate browser tabs
