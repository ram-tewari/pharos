/**
 * Graph Page Component
 * 
 * Main page component for graph visualization.
 * Orchestrates toolbar, canvas, and side panels.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 1 Foundation
 * Task: 1.1
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useGraphStore, selectSelectedNodes } from '@/stores/graph';
import { graphAPI } from '@/lib/api/graph';
import { applyLayout } from '@/lib/graph/layouts';
import { useGraphFilters } from '../hooks/useGraphFilters';
import { useViewMode } from '../hooks/useViewMode';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { useFocusMode } from '../hooks/useFocusMode';
import { useDebounce } from '@/hooks/useDebounce';
import { GraphToolbar } from './GraphToolbar';
import { GraphCanvas } from './GraphCanvas';
import { FilterPanel, type GraphFilters } from './FilterPanel';
import { NodeDetailsPanel } from './NodeDetailsPanel';
import { HypothesisPanel } from './HypothesisPanel';
import { HypothesisDiscoveryModal } from './HypothesisDiscoveryModal';
import { ExportModal } from './ExportModal';
import { LegendPanel } from './LegendPanel';
import { toast } from 'sonner';
import type { GraphNode, LayoutAlgorithm, Hypothesis } from '@/types/graph';

// ============================================================================
// Component
// ============================================================================

export function GraphPage() {
  const {
    nodes,
    edges,
    visualizationMode,
    zoomLevel,
    selectedNodes,
    setGraphData,
    setVisualizationMode,
    selectNode,
    clearSelection,
    zoomIn,
    zoomOut,
    resetZoom,
  } = useGraphStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showNodeDetails, setShowNodeDetails] = useState(false);
  const [showHypotheses, setShowHypotheses] = useState(false);
  const [showDiscoveryModal, setShowDiscoveryModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showIndicators, setShowIndicators] = useState(true);
  const [isFocusMode, setIsFocusMode] = useState(false);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [filters, setFilters] = useState<GraphFilters>({
    resourceTypes: ['paper', 'article', 'book', 'code'],
    minQuality: 0,
    dateRange: null,
  });

  // Debounce search query (300ms)
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  // Apply filters and search
  const { filteredNodes, filteredEdges, matchingNodeIds } = useGraphFilters(
    nodes,
    edges,
    debouncedSearchQuery,
    filters
  );

  // Use view mode hook for layout management
  const { applyViewModeLayout } = useViewMode();

  // Apply focus mode
  const selectedNodeId = selectedNodes.size > 0 ? Array.from(selectedNodes)[0] : null;
  const { nodes: focusedNodes, edges: focusedEdges } = useFocusMode(
    filteredNodes,
    filteredEdges,
    selectedNodeId,
    isFocusMode
  );

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onZoomIn: zoomIn,
    onZoomOut: zoomOut,
    onResetZoom: resetZoom,
    onClearSelection: () => {
      clearSelection();
      setShowFilters(false);
      setShowNodeDetails(false);
    },
    onToggleFilters: () => setShowFilters((prev) => !prev),
    onToggleFocusMode: () => setIsFocusMode((prev) => !prev),
  });

  // Get selected node
  const selectedNodesList = useGraphStore(selectSelectedNodes);
  const selectedNode = selectedNodesList[0] || null;

  // Load initial graph data
  useEffect(() => {
    loadGraphData();
  }, [visualizationMode]);

  // Show node details when a node is selected
  useEffect(() => {
    if (selectedNodes.size > 0) {
      setShowNodeDetails(true);
      setShowFilters(false);
    }
  }, [selectedNodes]);

  const loadGraphData = async () => {
    setIsLoading(true);
    try {
      // Load overview by default
      const data = await graphAPI.getOverview(0.5);
      
      // Apply layout based on visualization mode
      const algorithm: LayoutAlgorithm = 'force_directed';
      const layoutedNodes = applyLayout(data.nodes, data.edges, algorithm);
      
      setGraphData({
        ...data,
        nodes: layoutedNodes,
      });
    } catch (error) {
      console.error('Failed to load graph:', error);
      toast.error('Failed to load graph data');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle node click
  const handleNodeClick = useCallback((node: GraphNode) => {
    selectNode(node.id);
  }, [selectNode]);

  // Handle search with debouncing
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Handle filters change
  const handleFiltersChange = useCallback((newFilters: GraphFilters) => {
    setFilters(newFilters);
    toast.success('Filters applied');
  }, []);

  // Handle export
  const handleExport = useCallback(() => {
    setShowExportModal(true);
  }, []);

  // Handle filter toggle
  const handleToggleFilters = useCallback(() => {
    setShowFilters((prev) => !prev);
    if (!showFilters) {
      setShowNodeDetails(false);
      setShowHypotheses(false);
      clearSelection();
    }
  }, [showFilters, clearSelection]);

  // Handle node details close
  const handleNodeDetailsClose = useCallback(() => {
    setShowNodeDetails(false);
    clearSelection();
  }, [clearSelection]);

  // Handle hypothesis click
  const handleHypothesisClick = useCallback((hypothesis: Hypothesis) => {
    // Zoom to hypothesis subgraph
    const hypothesisNodes = hypothesis.nodes;
    if (hypothesisNodes.length > 0) {
      // Select first node in hypothesis
      selectNode(hypothesisNodes[0]);
      toast.info('Viewing hypothesis in graph');
    }
  }, [selectNode]);

  // Handle discover new hypotheses
  const handleDiscoverNew = useCallback(() => {
    setShowDiscoveryModal(true);
  }, []);

  // Handle hypotheses discovered
  const handleHypothesesDiscovered = useCallback((newHypotheses: Hypothesis[]) => {
    setHypotheses(newHypotheses);
    setShowHypotheses(true);
    setShowFilters(false);
    setShowNodeDetails(false);
  }, []);

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.resourceTypes.length < 4) count++;
    if (filters.minQuality > 0) count++;
    if (filters.dateRange) count++;
    return count;
  }, [filters]);

  // Remove old keyboard shortcuts effect (now handled by hook)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading graph...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <GraphToolbar
        viewMode={visualizationMode}
        onViewModeChange={setVisualizationMode}
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        zoom={zoomLevel}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onFitView={resetZoom}
        onExport={handleExport}
        onToggleFilters={handleToggleFilters}
        activeFilterCount={activeFilterCount}
        showIndicators={showIndicators}
        onToggleIndicators={() => setShowIndicators((prev) => !prev)}
      />

      {/* Main Content */}
      <div className="flex-1 relative flex">
        {/* Canvas */}
        <div className="flex-1 relative">
          <GraphCanvas
            nodes={focusedNodes}
            edges={focusedEdges}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedNodeId}
            showIndicators={showIndicators}
            className="w-full h-full"
          />
          
          {/* Legend Panel */}
          <LegendPanel />
          
          {/* Focus Mode Indicator */}
          {isFocusMode && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-medium shadow-lg">
              Focus Mode Active (Shift+F to toggle)
            </div>
          )}
        </div>

        {/* Side Panels */}
        {showFilters && (
          <div className="w-80 shrink-0">
            <FilterPanel
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onClose={() => setShowFilters(false)}
            />
          </div>
        )}

        {showNodeDetails && (
          <div className="w-80 shrink-0">
            <NodeDetailsPanel
              node={selectedNode}
              onClose={handleNodeDetailsClose}
            />
          </div>
        )}

        {showHypotheses && (
          <div className="w-80 shrink-0">
            <HypothesisPanel
              hypotheses={hypotheses}
              onHypothesisClick={handleHypothesisClick}
              onDiscoverNew={handleDiscoverNew}
              onClose={() => setShowHypotheses(false)}
            />
          </div>
        )}
      </div>

      {/* Empty State */}
      {filteredNodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <p className="text-lg font-medium text-muted-foreground mb-2">
              No nodes match your filters
            </p>
            <p className="text-sm text-muted-foreground">
              Try adjusting your search or filters
            </p>
          </div>
        </div>
      )}

      {/* Modals */}
      <HypothesisDiscoveryModal
        open={showDiscoveryModal}
        onOpenChange={setShowDiscoveryModal}
        onHypothesesDiscovered={handleHypothesesDiscovered}
      />

      <ExportModal
        open={showExportModal}
        onOpenChange={setShowExportModal}
        graphData={{ nodes, edges, metadata: undefined }}
      />
    </div>
  );
}
