# Implementation Plan: Phase 6 RAG Interface

## Overview

This implementation plan breaks down the Phase 6 RAG Interface into discrete, incremental coding tasks. Each task builds on previous work, with property-based tests integrated throughout to catch errors early. The plan follows a bottom-up approach: core utilities → state management → basic components → advanced features → integration.

## Tasks

- [ ] 1. Set up project structure and core types
  - Create directory structure: `src/components/features/rag/`, `src/lib/api/rag.ts`, `src/lib/hooks/rag/`, `src/lib/stores/ragStore.ts`
  - Define TypeScript interfaces for Citation, Chunk, EvaluationMetrics, Parameters, QueryHistoryItem, RAGQueryRequest, RAGQueryResponse
  - Set up test directories: `tests/unit/components/rag/`, `tests/properties/rag/`, `tests/integration/rag/`
  - Install dependencies: `react-split-pane`, `react-markdown`, `remark-gfm`, `react-syntax-highlighter`, `fast-check`
  - _Requirements: All requirements (foundation)_

- [ ] 2. Implement RAG API client
  - [ ] 2.1 Create RAGAPIClient class with submitQuery method
    - Implement POST /api/search/rag_query with streaming support
    - Handle ReadableStream response with TextDecoder
    - Parse Server-Sent Events (SSE) format
    - _Requirements: 1.1_
  
  - [ ] 2.2 Write property test for API client
    - **Property 1: Query API Integration**
    - **Validates: Requirements 1.1, 7.3**
  
  - [ ] 2.3 Implement streaming response handler
    - Create handleStreamingResponse function
    - Parse SSE data chunks (type: 'chunk', 'complete', 'error')
    - Handle stream interruption and errors
    - _Requirements: 2.1, 2.4_
  
  - [ ] 2.4 Write property test for streaming handler
    - **Property 5: Incremental Answer Display**
    - **Property 7: Partial Answer Preservation**
    - **Validates: Requirements 2.1, 2.4**

- [ ] 3. Implement Zustand store for RAG state
  - [ ] 3.1 Create RAGStore with state and actions
    - Define state: currentQuery, isQuerying, streamingAnswer, fullAnswer, citations, chunks, metrics, parameters, queryHistory, UI state
    - Implement actions: submitQuery, updateStreamingAnswer, setChunks, highlightChunk, updateParameters, saveToHistory, loadFromHistory
    - Integrate API client for query submission
    - _Requirements: 1.1, 1.2, 2.1, 7.2, 9.1_
  
  - [ ] 3.2 Write property test for query submission
    - **Property 3: Loading State Display**
    - **Property 4: Error Handling with Retry**
    - **Validates: Requirements 1.2, 1.4**
  
  - [ ] 3.3 Implement parameter validation and persistence
    - Validate topK (1-20), threshold (0-1)
    - Save/load parameters from localStorage
    - _Requirements: 7.4, 7.5_
  
  - [ ] 3.4 Write property test for parameter management
    - **Property 21: Parameter Validation**
    - **Property 22: Parameter Persistence and Application**
    - **Validates: Requirements 7.4, 7.5**

- [ ] 4. Checkpoint - Ensure core infrastructure works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement query input components
  - [ ] 5.1 Create QueryTextArea component
    - Implement textarea with character count (max 500)
    - Handle Enter key submission (Shift+Enter for newline)
    - Display validation errors inline
    - _Requirements: 1.5, 15.3_
  
  - [ ] 5.2 Write property test for query validation
    - **Property 2: Query Validation**
    - **Validates: Requirements 1.5, 15.3**
  
  - [ ] 5.3 Create ParameterControls component
    - Implement sliders for topK (1-20) and threshold (0-1)
    - Implement dropdown for retrievalMode
    - Add tooltips explaining each parameter
    - _Requirements: 7.1, 7.2_
  
  - [ ] 5.4 Create QueryInputSection component
    - Compose QueryTextArea and ParameterControls
    - Implement submit button with loading state
    - Handle form submission
    - _Requirements: 1.1, 1.2_

- [ ] 6. Implement answer panel components
  - [ ] 6.1 Create StreamingAnswerDisplay component
    - Implement typewriter effect with configurable delay (20-50ms per char)
    - Show pulsing cursor during streaming
    - Use react-markdown with remark-gfm for rendering
    - Integrate react-syntax-highlighter for code blocks
    - _Requirements: 2.1, 2.2, 2.3, 11.1_
  
  - [ ] 6.2 Write property test for streaming display
    - **Property 6: Streaming Cursor Visibility**
    - **Property 8: Answer Rendering with Citations**
    - **Validates: Requirements 2.2, 2.3, 1.3**
  
  - [ ] 6.3 Create CitationLink component
    - Render citation as superscript link [1]
    - Implement hover tooltip with chunk preview
    - Handle click to scroll evidence panel
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 6.4 Write property test for citation interaction
    - **Property 12: Citation Tooltip Display**
    - **Property 13: Citation-Chunk Synchronization**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  
  - [ ] 6.5 Create EvaluationMetricsBadges component
    - Render colored badges (green >0.8, yellow 0.5-0.8, red <0.5)
    - Handle null values (display "N/A")
    - Add tooltips explaining each metric
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 6.6 Write property test for metrics display
    - **Property 23: Metrics Display with Color Coding**
    - **Property 24: Metrics Tooltip Explanation**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
  
  - [ ] 6.7 Create AnswerPanel component
    - Compose StreamingAnswerDisplay, CitationLink, EvaluationMetricsBadges
    - Add copy and export buttons
    - Handle citation hover/click events
    - _Requirements: 1.3, 2.1, 4.1, 6.1, 8.1_

- [ ] 7. Implement evidence panel components
  - [ ] 7.1 Create ChunkCard component
    - Display chunk text (truncated to 300 characters)
    - Show resource title, author, relevance score
    - Implement expand/collapse for full text
    - Handle highlight state
    - _Requirements: 5.2_
  
  - [ ] 7.2 Create EvidencePanel component
    - Render list of ChunkCard components
    - Sort chunks by relevance score (descending)
    - Implement scroll-to-chunk on citation click
    - Handle empty state
    - _Requirements: 5.1, 5.2, 5.4, 5.5_
  
  - [ ] 7.3 Write property test for evidence panel
    - **Property 14: Chunk Sorting by Relevance**
    - **Property 15: Chunk Content Completeness**
    - **Property 17: Evidence Panel Scrolling**
    - **Validates: Requirements 5.1, 5.2, 5.5**
  
  - [ ] 7.4 Implement chunk navigation
    - Handle chunk click to navigate to resource detail
    - Pass chunk ID as URL parameter for highlighting
    - _Requirements: 5.3_
  
  - [ ] 7.5 Write property test for chunk navigation
    - **Property 16: Chunk Navigation**
    - **Validates: Requirements 5.3**

- [ ] 8. Checkpoint - Ensure basic UI components work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement split-pane layout
  - [ ] 9.1 Create SplitPaneLayout component
    - Integrate react-split-pane library
    - Set default size to 60% (answer) / 40% (evidence)
    - Set min/max sizes (30% / 80%)
    - Handle resize events
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ] 9.2 Write property test for pane resize
    - **Property 9: Pane Resize Synchronization**
    - **Validates: Requirements 3.2**
  
  - [ ] 9.3 Implement pane size persistence
    - Save pane size to localStorage on resize
    - Load pane size from localStorage on mount
    - _Requirements: 3.5_
  
  - [ ] 9.4 Write property test for pane persistence
    - **Property 11: Pane Size Persistence**
    - **Validates: Requirements 3.5**
  
  - [ ] 9.5 Implement responsive layout
    - Detect viewport width (<768px)
    - Switch to vertical stack on mobile
    - Implement tab interface for mobile
    - _Requirements: 3.3, 12.1, 12.2_
  
  - [ ] 9.6 Write property test for responsive layout
    - **Property 10: Responsive Layout Transformation**
    - **Property 35: Mobile UI Adaptation**
    - **Validates: Requirements 3.3, 12.1, 12.2**

- [ ] 10. Implement copy and export functionality
  - [ ] 10.1 Create clipboard utility functions
    - Implement copyAnswerWithCitations function
    - Format answer with inline citations [1], [2]
    - Add references section at end
    - Handle clipboard API errors
    - _Requirements: 6.1, 6.3, 6.4_
  
  - [ ] 10.2 Write property test for clipboard copy
    - **Property 18: Clipboard Copy with Citations**
    - **Property 19: Copy Success Feedback**
    - **Property 20: Copy Error Handling**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  
  - [ ] 10.3 Create export utility functions
    - Implement exportAsMarkdown function
    - Implement exportAsPDF function (using jspdf)
    - Implement exportAsJSON function
    - Generate filename with timestamp and query
    - _Requirements: 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 10.4 Write property test for export functionality
    - **Property 31: Export Format Generation**
    - **Property 32: Export Filename Format**
    - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**
  
  - [ ] 10.5 Create ActionButtons component
    - Add copy button with success/error toast
    - Add export button with format dropdown
    - Handle button states (loading, disabled)
    - _Requirements: 6.1, 6.2, 6.5, 10.1_

- [ ] 11. Implement query history
  - [ ] 11.1 Create history persistence utilities
    - Implement saveToHistory function
    - Implement loadFromHistory function
    - Implement deleteHistoryItem function
    - Implement clearHistory function
    - Handle localStorage quota exceeded
    - Enforce 100-item limit
    - _Requirements: 9.1, 9.3, 9.4, 9.5_
  
  - [ ] 11.2 Write property test for history persistence
    - **Property 26: History Persistence**
    - **Property 29: History Item Deletion**
    - **Property 30: History Size Limit**
    - **Validates: Requirements 9.1, 9.4, 9.5**
  
  - [ ] 11.3 Create HistoryItem component
    - Display query text (truncated)
    - Show timestamp (relative: "2 hours ago")
    - Show answer preview (first 100 chars)
    - Handle click to load history
    - Handle delete button
    - _Requirements: 9.2, 9.3, 9.4_
  
  - [ ] 11.4 Create QueryHistorySidebar component
    - Render collapsible sidebar
    - Display history list sorted by timestamp (descending)
    - Implement clear all button with confirmation
    - Handle empty state
    - _Requirements: 9.2, 9.3, 9.4_
  
  - [ ] 11.5 Write property test for history management
    - **Property 27: History Chronological Ordering**
    - **Property 28: History Item Loading**
    - **Validates: Requirements 9.2, 9.3**

- [ ] 12. Checkpoint - Ensure advanced features work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement code highlighting and copy
  - [ ] 13.1 Enhance StreamingAnswerDisplay with code features
    - Detect code blocks in Markdown
    - Apply syntax highlighting with react-syntax-highlighter
    - Auto-detect language or use default
    - Support 10+ common languages (Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL, HTML, CSS)
    - _Requirements: 11.1, 11.2, 11.5_
  
  - [ ] 13.2 Write property test for code highlighting
    - **Property 33: Code Block Syntax Highlighting**
    - **Validates: Requirements 11.1, 11.2**
  
  - [ ] 13.3 Add copy button to code blocks
    - Show copy button on hover
    - Copy code to clipboard on click
    - Show success toast
    - _Requirements: 11.3, 11.4_
  
  - [ ] 13.4 Write property test for code copy
    - **Property 34: Code Copy Functionality**
    - **Validates: Requirements 11.3, 11.4**

- [ ] 14. Implement accessibility features
  - [ ] 14.1 Add keyboard navigation support
    - Implement keyboard shortcuts (Cmd+K, Cmd+H, Escape)
    - Ensure all interactive elements are focusable
    - Add visible focus indicators
    - Implement focus trap in modals
    - _Requirements: 13.1, 13.2_
  
  - [ ] 14.2 Write property test for keyboard navigation
    - **Property 37: Keyboard Navigation Support**
    - **Validates: Requirements 13.1, 13.2**
  
  - [ ] 14.3 Add ARIA labels and live regions
    - Add ARIA labels to all icons and icon-only buttons
    - Add ARIA live regions for streaming updates
    - Use semantic HTML (header, nav, main, article)
    - _Requirements: 13.3, 13.4_
  
  - [ ] 14.4 Write property test for ARIA support
    - **Property 38: ARIA Label Completeness**
    - **Property 39: Screen Reader Announcements**
    - **Validates: Requirements 13.3, 13.4**
  
  - [ ] 14.5 Ensure color contrast compliance
    - Verify all text meets 4.5:1 contrast ratio
    - Add icons/text alongside color indicators
    - Test with color blindness simulators
    - _Requirements: 13.5_
  
  - [ ] 14.6 Write property test for color contrast
    - **Property 40: Color Contrast Compliance**
    - **Validates: Requirements 13.5**

- [ ] 15. Implement mobile optimizations
  - [ ] 15.1 Add mobile-specific UI components
    - Create mobile tab interface for answer/evidence
    - Create hamburger menu for controls
    - Hide history sidebar by default on mobile
    - Implement bottom sheet for parameters
    - _Requirements: 12.2, 12.3, 12.4_
  
  - [ ] 15.2 Optimize touch interactions
    - Ensure 44x44px minimum touch targets
    - Add adequate spacing between elements (8px)
    - Implement swipe gestures for tabs
    - _Requirements: 12.1, 12.2_
  
  - [ ] 15.3 Write property test for mobile support
    - **Property 36: Viewport Range Support**
    - **Validates: Requirements 12.5**

- [ ] 16. Implement error handling and recovery
  - [ ] 16.1 Add error boundaries
    - Wrap major sections with React Error Boundaries
    - Create fallback UI with error message and reset button
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [ ] 16.2 Implement retry mechanisms
    - Add retry button for network errors
    - Implement exponential backoff (1s, 2s, 4s)
    - Add resume from last chunk for streaming errors
    - _Requirements: 1.4, 15.1, 15.2, 15.4_
  
  - [ ] 16.3 Write property test for error handling
    - **Property 44: Error Logging**
    - **Validates: Requirements 15.5**
  
  - [ ] 16.4 Implement graceful degradation
    - Handle localStorage unavailable (in-memory fallback)
    - Handle metrics unavailable (display "N/A")
    - Handle syntax highlighting failure (plain text)
    - _Requirements: 8.4, 11.1_

- [ ] 17. Implement performance optimizations
  - [ ] 17.1 Add virtualization for large chunk lists
    - Integrate react-window for chunk list (>50 items)
    - Render only visible chunks in viewport
    - _Requirements: 14.5_
  
  - [ ] 17.2 Write property test for large chunk sets
    - **Property 43: Large Chunk Set Rendering**
    - **Validates: Requirements 14.5**
  
  - [ ] 17.3 Add memoization and code splitting
    - Memoize expensive computations (Markdown parsing, syntax highlighting)
    - Use React.memo for pure components
    - Lazy load export libraries (jspdf)
    - Lazy load syntax highlighter languages
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [ ] 17.4 Write property test for performance
    - **Property 41: First Chunk Latency**
    - **Property 42: History Load Performance**
    - **Validates: Requirements 14.1, 14.4**

- [ ] 18. Checkpoint - Ensure all features work together
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Create main RAGQueryPage component
  - [ ] 19.1 Compose all components into RAGQueryPage
    - Integrate QueryInputSection, SplitPaneLayout, AnswerPanel, EvidencePanel, QueryHistorySidebar
    - Connect to RAGStore
    - Handle keyboard shortcuts
    - Manage layout state
    - _Requirements: All requirements_
  
  - [ ] 19.2 Add route configuration
    - Add route to TanStack Router
    - Configure route path: /rag or /query
    - Add route metadata (title, description)
    - _Requirements: All requirements_

- [ ] 20. Write integration tests
  - [ ] 20.1 Test complete RAG query flow
    - Submit query → streaming answer → evidence display → citation interaction
    - _Requirements: 1.1, 2.1, 4.1, 5.1_
  
  - [ ] 20.2 Test history persistence flow
    - Submit query → save to history → load from history → verify state
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ] 20.3 Test copy and export flow
    - Generate answer → copy to clipboard → export as Markdown/PDF/JSON
    - _Requirements: 6.1, 10.2, 10.3, 10.4_
  
  - [ ] 20.4 Test error recovery flow
    - Trigger network error → display error → retry → success
    - _Requirements: 1.4, 15.1, 15.2_

- [ ] 21. Polish UI with frontend-polish.md standards
  - [ ] 21.1 Apply color system and typography
    - Use brand colors with proper shades
    - Apply professional font (Inter, Geist)
    - Ensure proper spacing (8-point grid)
    - _Requirements: All requirements (visual polish)_
  
  - [ ] 21.2 Add animations and transitions
    - Smooth transitions (150-300ms)
    - Hover animations on cards and buttons
    - Toast notifications with slide-in
    - Modal animations with scale and fade
    - _Requirements: All requirements (visual polish)_
  
  - [ ] 21.3 Add micro-interactions
    - Button press effects
    - Icon animations on hover
    - Loading indicators with shimmer
    - Success animations (checkmark)
    - _Requirements: All requirements (visual polish)_

- [ ] 22. Final checkpoint - End-to-end testing
  - Test complete user flows on different devices and browsers
  - Verify accessibility with screen readers
  - Check performance with Chrome DevTools
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end user flows
- Follow frontend-polish.md for visual design standards
- Use TypeScript for type safety
- Use Vitest and React Testing Library for testing
- Use fast-check for property-based testing
