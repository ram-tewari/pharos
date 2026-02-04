# Design Document: Phase 6 RAG Interface

## Overview

The Phase 6 RAG Interface is a sophisticated frontend component that provides an intuitive and visually stunning interface for Neo Alexandria's Advanced RAG backend. It implements a split-pane layout with real-time streaming answers, evidence highlighting, citation previews, and comprehensive retrieval controls. The design emphasizes performance, accessibility, and user experience while maintaining clean separation of concerns.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Query Page                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Query Input Component                    │  │
│  │  [Text Input] [Parameters] [Submit] [History Toggle] │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────┬─────────────────────────────┐  │
│  │    Answer Panel         │     Evidence Panel          │  │
│  │  ┌──────────────────┐   │  ┌──────────────────────┐   │  │
│  │  │ Streaming Answer │   │  │ Chunk 1 (Score: 0.9) │   │  │
│  │  │ with [Citations] │   │  │ Chunk 2 (Score: 0.8) │   │  │
│  │  │                  │   │  │ Chunk 3 (Score: 0.7) │   │  │
│  │  │ [Copy] [Export]  │   │  │ ...                  │   │  │
│  │  └──────────────────┘   │  └──────────────────────┘   │  │
│  │  Metrics: F:0.9 R:0.8   │  Resizable Divider          │  │
│  └─────────────────────────┴─────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Query History Sidebar (Collapsible)      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
RAGQueryPage
├── QueryInputSection
│   ├── QueryTextArea
│   ├── ParameterControls
│   │   ├── TopKSlider
│   │   ├── ThresholdSlider
│   │   └── RetrievalModeSelect
│   ├── SubmitButton
│   └── HistoryToggleButton
├── SplitPaneLayout
│   ├── AnswerPanel
│   │   ├── StreamingAnswerDisplay
│   │   │   ├── MarkdownRenderer
│   │   │   └── CitationLink (multiple)
│   │   ├── EvaluationMetricsBadges
│   │   └── ActionButtons
│   │       ├── CopyButton
│   │       └── ExportButton
│   └── EvidencePanel
│       ├── ChunkList
│       │   └── ChunkCard (multiple)
│       │       ├── ChunkText
│       │       ├── ResourceMetadata
│       │       └── RelevanceScore
│       └── EmptyState
└── QueryHistorySidebar
    ├── HistoryList
    │   └── HistoryItem (multiple)
    └── ClearHistoryButton
```

### State Management

**Zustand Store Structure:**

```typescript
interface RAGStore {
  // Query state
  currentQuery: string;
  isQuerying: boolean;
  queryError: string | null;
  
  // Answer state
  streamingAnswer: string;
  isStreaming: boolean;
  fullAnswer: string | null;
  citations: Citation[];
  
  // Evidence state
  chunks: Chunk[];
  highlightedChunkId: string | null;
  
  // Evaluation metrics
  metrics: {
    faithfulness: number | null;
    relevance: number | null;
    contextPrecision: number | null;
  };
  
  // Parameters
  parameters: {
    topK: number;
    threshold: number;
    retrievalMode: 'hybrid' | 'vector' | 'keyword' | 'graph';
  };
  
  // History
  queryHistory: QueryHistoryItem[];
  
  // UI state
  splitPaneSize: number;
  isHistorySidebarOpen: boolean;
  
  // Actions
  submitQuery: (query: string) => Promise<void>;
  updateStreamingAnswer: (chunk: string) => void;
  setChunks: (chunks: Chunk[]) => void;
  highlightChunk: (chunkId: string | null) => void;
  updateParameters: (params: Partial<Parameters>) => void;
  saveToHistory: () => void;
  loadFromHistory: (id: string) => void;
  clearHistory: () => void;
  setSplitPaneSize: (size: number) => void;
  toggleHistorySidebar: () => void;
}
```

### Data Flow

1. **Query Submission:**
   ```
   User Input → QueryInputSection → RAGStore.submitQuery()
   → API Call (POST /api/search/rag_query)
   → Streaming Response → RAGStore.updateStreamingAnswer()
   → AnswerPanel renders incrementally
   ```

2. **Citation Interaction:**
   ```
   User Hovers Citation → CitationLink.onMouseEnter
   → RAGStore.highlightChunk(chunkId)
   → EvidencePanel highlights corresponding chunk
   → Tooltip displays chunk preview
   ```

3. **Evidence Display:**
   ```
   API Response → RAGStore.setChunks(chunks)
   → EvidencePanel.ChunkList renders
   → Chunks sorted by relevance score
   → Click chunk → Navigate to resource with highlight
   ```

4. **History Management:**
   ```
   Query Complete → RAGStore.saveToHistory()
   → LocalStorage.setItem('rag-history', history)
   → HistorySidebar displays updated list
   → Click history item → RAGStore.loadFromHistory(id)
   ```

## Components and Interfaces

### 1. RAGQueryPage

**Purpose:** Main container component for the RAG interface

**Props:**
```typescript
interface RAGQueryPageProps {
  // No props - uses Zustand store
}
```

**Responsibilities:**
- Initialize RAG store
- Manage layout (split pane, sidebar)
- Handle keyboard shortcuts (Cmd+K for query focus, Cmd+H for history)
- Persist UI state to localStorage

### 2. QueryInputSection

**Purpose:** Query input with parameter controls

**Props:**
```typescript
interface QueryInputSectionProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}
```

**Responsibilities:**
- Render textarea with character count (max 500)
- Render parameter controls (top-k, threshold, mode)
- Validate input before submission
- Show loading state during query
- Handle Enter key submission (Shift+Enter for newline)

### 3. ParameterControls

**Purpose:** Retrieval parameter configuration

**Props:**
```typescript
interface ParameterControlsProps {
  topK: number;
  threshold: number;
  retrievalMode: 'hybrid' | 'vector' | 'keyword' | 'graph';
  onChange: (params: Partial<Parameters>) => void;
}
```

**Responsibilities:**
- Render sliders for top-k (1-20) and threshold (0-1)
- Render dropdown for retrieval mode
- Validate parameter ranges
- Show tooltips explaining each parameter
- Persist parameters to localStorage

### 4. SplitPaneLayout

**Purpose:** Resizable split-pane container

**Props:**
```typescript
interface SplitPaneLayoutProps {
  leftPane: React.ReactNode;
  rightPane: React.ReactNode;
  defaultSize: number; // percentage (50-70)
  minSize: number; // minimum percentage (30)
  maxSize: number; // maximum percentage (80)
  onResize: (size: number) => void;
}
```

**Responsibilities:**
- Render resizable divider between panes
- Handle drag events for resizing
- Persist pane size to localStorage
- Switch to vertical stack on mobile (<768px)
- Smooth resize animations (60fps)

**Implementation:** Use `react-split-pane` or custom implementation with `useResizeObserver`

### 5. AnswerPanel

**Purpose:** Display streaming answer with citations

**Props:**
```typescript
interface AnswerPanelProps {
  answer: string;
  isStreaming: boolean;
  citations: Citation[];
  metrics: EvaluationMetrics;
  onCitationHover: (citationId: string | null) => void;
  onCitationClick: (citationId: string) => void;
}
```

**Responsibilities:**
- Render Markdown answer with syntax highlighting
- Render inline citations as clickable links
- Show typewriter cursor during streaming
- Display evaluation metrics badges
- Render copy and export buttons
- Handle citation hover/click events

### 6. StreamingAnswerDisplay

**Purpose:** Render streaming text with typewriter effect

**Props:**
```typescript
interface StreamingAnswerDisplayProps {
  text: string;
  isStreaming: boolean;
  renderDelay: number; // ms per character (20-50)
}
```

**Responsibilities:**
- Render text incrementally with typewriter effect
- Show pulsing cursor during streaming
- Parse Markdown and apply syntax highlighting
- Handle code blocks with copy button
- Smooth scroll to bottom as text appears

**Implementation:** Use `react-markdown` with `remark-gfm` and `react-syntax-highlighter`

### 7. CitationLink

**Purpose:** Inline citation with hover preview

**Props:**
```typescript
interface CitationLinkProps {
  citationNumber: number;
  chunkId: string;
  onHover: (chunkId: string | null) => void;
  onClick: (chunkId: string) => void;
}
```

**Responsibilities:**
- Render citation as superscript link [1]
- Show tooltip on hover with chunk preview
- Highlight corresponding chunk in evidence panel
- Scroll evidence panel to chunk on click
- Accessible keyboard navigation

**Tooltip Content:**
- Chunk text (first 200 characters)
- Resource title and author
- Relevance score
- Chunk metadata (page number, section)

### 8. EvaluationMetricsBadges

**Purpose:** Display RAGAS evaluation metrics

**Props:**
```typescript
interface EvaluationMetricsBadgesProps {
  faithfulness: number | null;
  relevance: number | null;
  contextPrecision: number | null;
}
```

**Responsibilities:**
- Render colored badges (green >0.8, yellow 0.5-0.8, red <0.5)
- Show tooltips explaining each metric
- Handle null values (display "N/A")
- Animate badge appearance
- Update in real-time during streaming

**Metric Definitions:**
- **Faithfulness:** How well the answer is grounded in the evidence
- **Relevance:** How relevant the answer is to the query
- **Context Precision:** How precise the retrieved context is

### 9. EvidencePanel

**Purpose:** Display retrieved chunks with relevance scores

**Props:**
```typescript
interface EvidencePanelProps {
  chunks: Chunk[];
  highlightedChunkId: string | null;
  onChunkClick: (chunkId: string) => void;
}
```

**Responsibilities:**
- Render list of chunks sorted by relevance
- Highlight chunk when citation is hovered
- Scroll to chunk when citation is clicked
- Show empty state when no chunks
- Handle chunk click (navigate to resource)

### 10. ChunkCard

**Purpose:** Display individual chunk with metadata

**Props:**
```typescript
interface ChunkCardProps {
  chunk: Chunk;
  isHighlighted: boolean;
  onClick: () => void;
}
```

**Responsibilities:**
- Render chunk text (truncated to 300 characters)
- Display resource title, author, and metadata
- Show relevance score as colored badge
- Highlight background when hovered citation
- Smooth scroll-into-view animation
- Expand/collapse full chunk text

### 11. QueryHistorySidebar

**Purpose:** Display and manage query history

**Props:**
```typescript
interface QueryHistorySidebarProps {
  isOpen: boolean;
  history: QueryHistoryItem[];
  onLoadHistory: (id: string) => void;
  onClearHistory: () => void;
  onClose: () => void;
}
```

**Responsibilities:**
- Render collapsible sidebar with history list
- Display query text, timestamp, and preview
- Load query on click
- Delete individual history items
- Clear all history with confirmation
- Persist to localStorage (max 100 items)

### 12. ActionButtons

**Purpose:** Copy and export functionality

**Props:**
```typescript
interface ActionButtonsProps {
  answer: string;
  citations: Citation[];
  chunks: Chunk[];
  query: string;
  metrics: EvaluationMetrics;
}
```

**Responsibilities:**
- Copy answer with citations to clipboard
- Export as Markdown, PDF, or JSON
- Show success/error toasts
- Generate formatted exports with metadata
- Handle export errors gracefully

## Data Models

### Core Types

```typescript
interface Citation {
  id: string;
  number: number; // [1], [2], etc.
  chunkId: string;
  text: string; // citation text in answer
  startIndex: number; // position in answer
  endIndex: number;
}

interface Chunk {
  id: string;
  text: string;
  resourceId: string;
  resourceTitle: string;
  resourceAuthor: string | null;
  relevanceScore: number; // 0-1
  metadata: {
    pageNumber?: number;
    section?: string;
    chunkIndex: number;
    parentChunkId?: string;
  };
}

interface EvaluationMetrics {
  faithfulness: number | null; // 0-1
  relevance: number | null; // 0-1
  contextPrecision: number | null; // 0-1
}

interface Parameters {
  topK: number; // 1-20
  threshold: number; // 0-1
  retrievalMode: 'hybrid' | 'vector' | 'keyword' | 'graph';
}

interface QueryHistoryItem {
  id: string;
  query: string;
  answer: string;
  citations: Citation[];
  chunks: Chunk[];
  metrics: EvaluationMetrics;
  parameters: Parameters;
  timestamp: number;
}

interface RAGQueryRequest {
  query: string;
  top_k: number;
  threshold: number;
  retrieval_mode: string;
}

interface RAGQueryResponse {
  answer: string;
  citations: Citation[];
  chunks: Chunk[];
  metrics: EvaluationMetrics;
}
```

### API Integration

```typescript
// API Client
class RAGAPIClient {
  async submitQuery(request: RAGQueryRequest): Promise<ReadableStream<string>> {
    const response = await fetch('/api/search/rag_query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Query failed: ${response.statusText}`);
    }
    
    return response.body!;
  }
  
  async getResourceChunks(resourceId: string): Promise<Chunk[]> {
    const response = await fetch(`/api/resources/${resourceId}/chunks`);
    return response.json();
  }
}

// Streaming Handler
async function handleStreamingResponse(
  stream: ReadableStream<string>,
  onChunk: (chunk: string) => void,
  onComplete: (response: RAGQueryResponse) => void,
  onError: (error: Error) => void
): Promise<void> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'chunk') {
            onChunk(data.content);
          } else if (data.type === 'complete') {
            onComplete(data.response);
          }
        }
      }
    }
  } catch (error) {
    onError(error as Error);
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I've identified several areas where properties can be consolidated:

**Redundancy Analysis:**

1. **Citation Interaction (4.1, 4.3, 4.4)**: These three properties all test citation interaction. They can be combined into comprehensive citation interaction properties.

2. **Copy Functionality (6.1, 6.2, 6.3, 6.4, 6.5)**: These test different aspects of copying. Properties 6.3 and 6.4 both test clipboard format and can be combined.

3. **Parameter Persistence (7.2, 7.5)**: Both test parameter state management and can be combined.

4. **Metrics Display (8.1, 8.2, 8.4)**: These test different aspects of metrics rendering and can be combined.

5. **History Management (9.1, 9.2, 9.3, 9.4)**: These test different history operations and can be streamlined.

6. **Export Formats (10.2, 10.3, 10.4)**: These test different export formats but follow the same pattern.

7. **Responsive Layout (12.1, 12.2, 12.3, 12.4)**: These test mobile-specific UI and can be combined.

8. **Accessibility (13.1, 13.2, 13.3, 13.4, 13.5)**: These test different accessibility features and can be streamlined.

**Consolidated Properties:**

After reflection, I've reduced 75+ testable criteria to 35 unique, non-redundant properties that provide comprehensive validation coverage.

### Correctness Properties

#### Query Submission Properties

**Property 1: Query API Integration**
*For any* valid query string (1-500 characters), submitting the query should result in an API call to POST /api/search/rag_query with the correct payload including query text and current parameters.
**Validates: Requirements 1.1, 7.3**

**Property 2: Query Validation**
*For any* query string longer than 500 characters, the system should reject the submission and display a validation error.
**Validates: Requirements 1.5, 15.3**

**Property 3: Loading State Display**
*For any* query submission, while isQuerying is true, the loading indicator should be visible in the Answer Panel.
**Validates: Requirements 1.2**

**Property 4: Error Handling with Retry**
*For any* failed query (network error, timeout, server error), the system should display an error message with a retry button that allows resubmission.
**Validates: Requirements 1.4, 15.1, 15.2**

#### Streaming Answer Properties

**Property 5: Incremental Answer Display**
*For any* streaming response, each received chunk should be appended to the displayed answer text incrementally.
**Validates: Requirements 2.1**

**Property 6: Streaming Cursor Visibility**
*For any* streaming state, when isStreaming is true, a pulsing cursor should be visible at the end of the answer text, and when isStreaming becomes false, the cursor should be removed.
**Validates: Requirements 2.2, 2.3**

**Property 7: Partial Answer Preservation**
*For any* streaming failure, the partial answer received before the failure should remain visible with an error indicator.
**Validates: Requirements 2.4, 15.4**

**Property 8: Answer Rendering with Citations**
*For any* complete answer with citations, the rendered output should include all citation links in the correct positions matching the citation indices.
**Validates: Requirements 1.3**

#### Split-Pane Layout Properties

**Property 9: Pane Resize Synchronization**
*For any* drag event on the divider, both panes should resize proportionally such that their combined width equals 100% of the container.
**Validates: Requirements 3.2**

**Property 10: Responsive Layout Transformation**
*For any* viewport width below 768px, the layout should transform from horizontal split-pane to vertical stack.
**Validates: Requirements 3.3, 12.1**

**Property 11: Pane Size Persistence**
*For any* pane resize operation, the new size should be saved to localStorage and restored on page reload.
**Validates: Requirements 3.5**

#### Citation Interaction Properties

**Property 12: Citation Tooltip Display**
*For any* citation hover event, a tooltip should appear within 200ms containing chunk text, resource title, author, and relevance score.
**Validates: Requirements 4.1, 4.2**

**Property 13: Citation-Chunk Synchronization**
*For any* citation hover or click, the corresponding chunk in the Evidence Panel should be highlighted and scrolled into view.
**Validates: Requirements 4.3, 4.4**

#### Evidence Panel Properties

**Property 14: Chunk Sorting by Relevance**
*For any* set of retrieved chunks, they should be displayed in descending order of relevance score.
**Validates: Requirements 5.1**

**Property 15: Chunk Content Completeness**
*For any* displayed chunk, it should include chunk text, resource title, relevance score, and metadata (page number, section if available).
**Validates: Requirements 5.2**

**Property 16: Chunk Navigation**
*For any* chunk click event, the system should navigate to the resource detail page with the chunk highlighted.
**Validates: Requirements 5.3**

**Property 17: Evidence Panel Scrolling**
*For any* number of chunks greater than 10, the Evidence Panel should enable scrolling to access all chunks.
**Validates: Requirements 5.5**

#### Copy Functionality Properties

**Property 18: Clipboard Copy with Citations**
*For any* answer with citations, clicking the copy button should copy the answer text with inline citations in Markdown format [1], [2] and a references section at the end.
**Validates: Requirements 6.1, 6.3, 6.4**

**Property 19: Copy Success Feedback**
*For any* successful copy operation, a success toast notification should appear.
**Validates: Requirements 6.2**

**Property 20: Copy Error Handling**
*For any* failed copy operation, an error toast notification should appear.
**Validates: Requirements 6.5**

#### Parameter Control Properties

**Property 21: Parameter Validation**
*For any* parameter change, the system should validate that topK is between 1-20 and threshold is between 0-1, rejecting invalid values.
**Validates: Requirements 7.4**

**Property 22: Parameter Persistence and Application**
*For any* parameter change, the new value should be saved to localStorage, restored on reload, and included in subsequent query API calls.
**Validates: Requirements 7.2, 7.3, 7.5**

#### Evaluation Metrics Properties

**Property 23: Metrics Display with Color Coding**
*For any* evaluation metrics (faithfulness, relevance, contextPrecision), they should be displayed as colored badges: green for scores >0.8, yellow for 0.5-0.8, red for <0.5, and "N/A" for null values.
**Validates: Requirements 8.1, 8.2, 8.4**

**Property 24: Metrics Tooltip Explanation**
*For any* metric badge hover, a tooltip should appear explaining what the metric measures.
**Validates: Requirements 8.3**

**Property 25: Streaming Metrics Update**
*For any* streaming response, evaluation metrics should update in real-time as they become available.
**Validates: Requirements 8.5**

#### Query History Properties

**Property 26: History Persistence**
*For any* completed query, the query, answer, citations, chunks, metrics, and parameters should be saved to localStorage as a history item.
**Validates: Requirements 9.1**

**Property 27: History Chronological Ordering**
*For any* history list display, items should be sorted in reverse chronological order (newest first).
**Validates: Requirements 9.2**

**Property 28: History Item Loading**
*For any* history item click, the system should load and display the saved query, answer, citations, and chunks.
**Validates: Requirements 9.3**

**Property 29: History Item Deletion**
*For any* history item deletion, the item should be removed from localStorage and the UI should update immediately.
**Validates: Requirements 9.4**

**Property 30: History Size Limit**
*For any* history with more than 100 items, the oldest items should be removed to maintain the 100-item limit.
**Validates: Requirements 9.5**

#### Export Functionality Properties

**Property 31: Export Format Generation**
*For any* export format (Markdown, PDF, JSON), the system should generate a file with the answer, citations, chunks, and metadata in the correct format.
**Validates: Requirements 10.2, 10.3, 10.4**

**Property 32: Export Filename Format**
*For any* exported file, the filename should include a timestamp and truncated query text.
**Validates: Requirements 10.5**

#### Code Highlighting Properties

**Property 33: Code Block Syntax Highlighting**
*For any* code block in the answer, syntax highlighting should be applied based on the detected or specified language.
**Validates: Requirements 11.1, 11.2**

**Property 34: Code Copy Functionality**
*For any* code block hover, a copy button should appear, and clicking it should copy the code to the clipboard.
**Validates: Requirements 11.3, 11.4**

#### Responsive Design Properties

**Property 35: Mobile UI Adaptation**
*For any* viewport width below 768px, the system should display mobile-optimized UI including vertical stacking, tab interface for panes, hidden sidebar by default, and hamburger menu for controls.
**Validates: Requirements 12.1, 12.2, 12.3, 12.4**

**Property 36: Viewport Range Support**
*For any* viewport width from 320px to 2560px, all functionality should remain accessible and usable.
**Validates: Requirements 12.5**

#### Accessibility Properties

**Property 37: Keyboard Navigation Support**
*For any* interactive element, it should be accessible via keyboard (Tab, Enter, Space, Escape) with visible focus indicators.
**Validates: Requirements 13.1, 13.2**

**Property 38: ARIA Label Completeness**
*For any* icon or icon-only button, it should have an appropriate ARIA label for screen readers.
**Validates: Requirements 13.3**

**Property 39: Screen Reader Announcements**
*For any* streaming answer update, the new content should be announced to screen readers via ARIA live regions.
**Validates: Requirements 13.4**

**Property 40: Color Contrast Compliance**
*For any* text element, the color contrast ratio between text and background should be at least 4.5:1.
**Validates: Requirements 13.5**

#### Performance Properties

**Property 41: First Chunk Latency**
*For any* query submission, the first answer chunk should be displayed within 2 seconds of submission.
**Validates: Requirements 14.1**

**Property 42: History Load Performance**
*For any* history sidebar open, the history list should be displayed within 500ms.
**Validates: Requirements 14.4**

**Property 43: Large Chunk Set Rendering**
*For any* evidence set with up to 100 chunks, the Evidence Panel should render without performance degradation (no frame drops, smooth scrolling).
**Validates: Requirements 14.5**

#### Error Handling Properties

**Property 44: Error Logging**
*For any* error (network, validation, streaming, export), the error should be logged to the browser console with relevant context.
**Validates: Requirements 15.5**

## Error Handling

### Error Categories

1. **Network Errors**
   - Connection failures
   - Timeout errors
   - Server errors (5xx)
   - Handled by: Retry mechanism, error toast, console logging

2. **Validation Errors**
   - Query too long (>500 chars)
   - Invalid parameters (topK, threshold out of range)
   - Handled by: Inline error messages, input highlighting

3. **Streaming Errors**
   - Stream interruption
   - Malformed data
   - Handled by: Preserve partial answer, error indicator, retry option

4. **Export Errors**
   - File generation failure
   - Browser API errors (clipboard, download)
   - Handled by: Error toast, fallback options

5. **Storage Errors**
   - localStorage quota exceeded
   - localStorage unavailable
   - Handled by: Graceful degradation, in-memory fallback

### Error Recovery Strategies

**Automatic Retry:**
- Network errors: Exponential backoff (1s, 2s, 4s)
- Streaming errors: Resume from last successful chunk

**User-Initiated Retry:**
- Query submission errors: Retry button
- Export errors: Try again button

**Graceful Degradation:**
- localStorage unavailable: Use in-memory state (no persistence)
- Metrics unavailable: Display "N/A"
- Syntax highlighting fails: Display plain text

**Error Boundaries:**
- React Error Boundaries wrap major sections
- Fallback UI displays error message and reset button
- Errors don't crash entire application

## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests for specific examples and edge cases with property-based tests for universal properties across all inputs. Both approaches are complementary and necessary for comprehensive coverage.

**Unit Tests:**
- Specific examples demonstrating correct behavior
- Edge cases (empty states, null values, boundary conditions)
- Integration points between components
- Error conditions and recovery

**Property-Based Tests:**
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Minimum 100 iterations per property test
- Each test references its design document property

### Testing Tools

**Unit Testing:**
- Vitest for test runner
- React Testing Library for component testing
- Mock Service Worker (MSW) for API mocking
- @testing-library/user-event for user interactions

**Property-Based Testing:**
- fast-check for property-based testing in TypeScript
- Custom generators for domain objects (queries, chunks, citations)
- Minimum 100 iterations per property test

### Test Organization

```
tests/
├── unit/
│   ├── components/
│   │   ├── RAGQueryPage.test.tsx
│   │   ├── QueryInputSection.test.tsx
│   │   ├── AnswerPanel.test.tsx
│   │   ├── EvidencePanel.test.tsx
│   │   └── QueryHistorySidebar.test.tsx
│   ├── hooks/
│   │   ├── useRAGQuery.test.ts
│   │   ├── useStreamingAnswer.test.ts
│   │   └── useQueryHistory.test.ts
│   └── utils/
│       ├── clipboard.test.ts
│       ├── export.test.ts
│       └── formatting.test.ts
├── properties/
│   ├── query-submission.properties.test.ts
│   ├── streaming-answer.properties.test.ts
│   ├── citation-interaction.properties.test.ts
│   ├── evidence-panel.properties.test.ts
│   ├── copy-export.properties.test.ts
│   ├── parameters.properties.test.ts
│   ├── history.properties.test.ts
│   └── accessibility.properties.test.ts
└── integration/
    ├── rag-query-flow.test.tsx
    ├── citation-evidence-sync.test.tsx
    └── history-persistence.test.tsx
```

### Property Test Configuration

Each property test must:
- Run minimum 100 iterations
- Reference its design document property in a comment
- Use tag format: `// Feature: phase6-rag-interface, Property {number}: {property_text}`
- Generate random inputs using fast-check
- Verify the property holds for all generated inputs

**Example Property Test:**

```typescript
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';

describe('Query Submission Properties', () => {
  // Feature: phase6-rag-interface, Property 1: Query API Integration
  it('should call API with correct payload for any valid query', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 500 }),
        fc.integer({ min: 1, max: 20 }),
        fc.double({ min: 0, max: 1 }),
        async (query, topK, threshold) => {
          const mockFetch = vi.fn().mockResolvedValue({
            ok: true,
            body: new ReadableStream(),
          });
          global.fetch = mockFetch;
          
          await submitQuery(query, { topK, threshold, retrievalMode: 'hybrid' });
          
          expect(mockFetch).toHaveBeenCalledWith(
            '/api/search/rag_query',
            expect.objectContaining({
              method: 'POST',
              body: JSON.stringify({
                query,
                top_k: topK,
                threshold,
                retrieval_mode: 'hybrid',
              }),
            })
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Test Coverage Goals

- **Unit Test Coverage:** >80% line coverage
- **Property Test Coverage:** All 44 properties implemented
- **Integration Test Coverage:** All major user flows
- **Accessibility Test Coverage:** All WCAG 2.1 AA criteria

### Continuous Integration

- Run all tests on every commit
- Fail build if any test fails
- Generate coverage reports
- Run property tests with 100 iterations in CI
- Run accessibility tests with axe-core

## Implementation Notes

### Technology Choices

**Split-Pane Library:**
- Use `react-split-pane` or `allotment` for resizable layout
- Fallback: Custom implementation with `useResizeObserver`

**Markdown Rendering:**
- Use `react-markdown` with `remark-gfm` for GitHub Flavored Markdown
- Use `react-syntax-highlighter` for code blocks

**Streaming:**
- Use Fetch API with ReadableStream
- Use TextDecoder for chunk decoding
- Handle Server-Sent Events (SSE) format

**Export:**
- Markdown: Generate string and trigger download
- PDF: Use `jspdf` or `html2pdf` for client-side generation
- JSON: Use JSON.stringify and trigger download

**Clipboard:**
- Use Clipboard API (navigator.clipboard.writeText)
- Fallback: document.execCommand('copy') for older browsers

**Storage:**
- Use localStorage for persistence
- Implement size limit checks (5MB typical limit)
- Graceful degradation if unavailable

### Performance Optimizations

**Virtualization:**
- Use `react-window` or `react-virtualized` for large chunk lists (>50 items)
- Render only visible chunks in viewport

**Memoization:**
- Memoize expensive computations (Markdown parsing, syntax highlighting)
- Use React.memo for pure components
- Use useMemo for derived state

**Debouncing:**
- Debounce parameter changes (300ms)
- Debounce search in history sidebar (200ms)

**Code Splitting:**
- Lazy load export libraries (jspdf, html2pdf)
- Lazy load syntax highlighter languages
- Lazy load Monaco Editor if used

**Streaming Optimization:**
- Batch small chunks (combine chunks <50 chars)
- Throttle render updates (max 60fps)
- Use requestAnimationFrame for smooth animations

### Accessibility Considerations

**Keyboard Shortcuts:**
- Cmd/Ctrl+K: Focus query input
- Cmd/Ctrl+H: Toggle history sidebar
- Cmd/Ctrl+C: Copy answer (when answer is focused)
- Escape: Close modals/sidebars

**Screen Reader Support:**
- ARIA live regions for streaming updates (aria-live="polite")
- ARIA labels for all icons and icon-only buttons
- Semantic HTML (header, nav, main, article, aside)
- Proper heading hierarchy (h1, h2, h3)

**Focus Management:**
- Focus trap in modals
- Focus return after modal close
- Visible focus indicators (outline with brand color)
- Skip to main content link

**Color Contrast:**
- All text meets WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text)
- Don't rely on color alone for information (add icons/text)
- Test with color blindness simulators

### Mobile Considerations

**Touch Targets:**
- Minimum 44x44px touch targets
- Adequate spacing between interactive elements (8px minimum)

**Gestures:**
- Swipe to switch between answer and evidence tabs
- Pull-to-refresh for query history

**Performance:**
- Reduce animations on mobile (prefers-reduced-motion)
- Lazy load images and heavy components
- Optimize bundle size (code splitting)

**Layout:**
- Vertical stacking on mobile (<768px)
- Tab interface for answer/evidence
- Bottom sheet for parameters
- Hamburger menu for controls

## Related Documentation

- [Product Overview](../../../.kiro/steering/product.md)
- [Tech Stack](../../../.kiro/steering/tech.md)
- [Frontend Polish Checklist](../../../.kiro/steering/frontend-polish.md)
- [Backend API Documentation](../../../../backend/docs/api/search.md)
- [Advanced RAG Architecture](../../../../backend/docs/architecture/advanced-rag.md)
