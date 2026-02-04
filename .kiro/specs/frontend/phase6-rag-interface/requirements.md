# Requirements Document: Phase 6 RAG Interface

## Introduction

The Phase 6 RAG Interface provides a stunning frontend for Neo Alexandria's Advanced RAG backend (Phase 17.5). It enables researchers to ask natural language questions about their knowledge base and receive AI-generated answers with evidence, citations, and evaluation metrics. The interface features a split-pane layout with streaming answers, evidence highlighting, citation previews, and comprehensive retrieval controls.

## Glossary

- **RAG_System**: The Retrieval-Augmented Generation system that combines document retrieval with AI answer generation
- **Answer_Panel**: The left pane displaying the streaming AI-generated answer with inline citations
- **Evidence_Panel**: The right pane displaying retrieved document chunks with relevance scores
- **Citation**: An inline reference in the answer linking to a specific evidence chunk
- **Chunk**: A segment of a document used as evidence for answer generation
- **Relevance_Score**: A numerical value (0-1) indicating how relevant a chunk is to the query
- **Streaming_Response**: Real-time delivery of answer text as it's generated (typewriter effect)
- **Retrieval_Parameters**: User-configurable settings (top-k, threshold, mode) controlling evidence retrieval
- **Evaluation_Metrics**: Quality scores (faithfulness, relevance, context precision) from RAGAS framework
- **Query_History**: A chronological list of previous queries and their answers

## Requirements

### Requirement 1: RAG Query Interface

**User Story:** As a researcher, I want to ask natural language questions about my knowledge base, so that I can get AI-generated answers with evidence.

#### Acceptance Criteria

1. WHEN a user types a query and submits it, THE RAG_System SHALL send the query to the backend RAG endpoint
2. WHEN the query is submitted, THE Answer_Panel SHALL display a loading indicator
3. WHEN the backend returns a response, THE Answer_Panel SHALL display the answer with inline citations
4. WHEN the query fails, THE RAG_System SHALL display an error message with retry option
5. THE RAG_System SHALL support queries up to 500 characters in length

### Requirement 2: Streaming Answer Display

**User Story:** As a researcher, I want to see the answer stream in real-time, so that I can start reading before the full response is complete.

#### Acceptance Criteria

1. WHEN the backend streams answer chunks, THE Answer_Panel SHALL display each chunk with a typewriter effect
2. WHEN streaming is in progress, THE Answer_Panel SHALL show a pulsing cursor at the end of the text
3. WHEN streaming completes, THE Answer_Panel SHALL remove the cursor and enable interaction
4. WHEN streaming fails mid-response, THE RAG_System SHALL display the partial answer with an error indicator
5. THE Streaming_Response SHALL render at a rate of 20-50 characters per second for readability

### Requirement 3: Split-Pane Layout

**User Story:** As a researcher, I want to see the answer and evidence side-by-side, so that I can verify claims while reading.

#### Acceptance Criteria

1. THE RAG_System SHALL display a split-pane layout with Answer_Panel on the left and Evidence_Panel on the right
2. WHEN a user drags the divider, THE RAG_System SHALL resize both panes smoothly
3. WHEN the window width is below 768px, THE RAG_System SHALL stack panes vertically
4. THE Answer_Panel SHALL occupy 50-70% of the width by default
5. THE RAG_System SHALL persist the divider position in local storage

### Requirement 4: Citation Hover Preview

**User Story:** As a researcher, I want to preview citations on hover, so that I can quickly check sources without leaving the page.

#### Acceptance Criteria

1. WHEN a user hovers over a Citation, THE RAG_System SHALL display a tooltip with source metadata
2. THE tooltip SHALL include the chunk text, resource title, author, and relevance score
3. WHEN a user clicks a Citation, THE Evidence_Panel SHALL scroll to and highlight the corresponding chunk
4. WHEN a user hovers over a Citation, THE corresponding chunk in Evidence_Panel SHALL highlight with a subtle background color
5. THE tooltip SHALL appear within 200ms of hover and dismiss on mouse leave

### Requirement 5: Evidence Panel Display

**User Story:** As a researcher, I want to see the retrieved chunks with relevance scores, so that I can understand how the answer was generated.

#### Acceptance Criteria

1. WHEN evidence is retrieved, THE Evidence_Panel SHALL display all chunks in descending order of relevance
2. WHEN displaying a chunk, THE Evidence_Panel SHALL show the chunk text, resource title, relevance score, and chunk metadata
3. WHEN a chunk is clicked, THE RAG_System SHALL navigate to the full resource with the chunk highlighted
4. WHEN no evidence is retrieved, THE Evidence_Panel SHALL display an empty state message
5. THE Evidence_Panel SHALL support scrolling for more than 10 chunks

### Requirement 6: Copy Answer Functionality

**User Story:** As a researcher, I want to copy the answer with citations, so that I can use it in my research.

#### Acceptance Criteria

1. WHEN a user clicks the copy button, THE RAG_System SHALL copy the answer text with citations to the clipboard
2. WHEN the copy succeeds, THE RAG_System SHALL display a success toast notification
3. THE copied text SHALL include inline citations in Markdown format [1], [2], etc.
4. THE copied text SHALL include a references section at the end with full citation details
5. WHEN the copy fails, THE RAG_System SHALL display an error toast

### Requirement 7: Retrieval Parameter Controls

**User Story:** As a researcher, I want to adjust retrieval parameters, so that I can control answer quality.

#### Acceptance Criteria

1. THE RAG_System SHALL provide controls for top-k (number of chunks), threshold (minimum relevance), and retrieval mode
2. WHEN a user changes a parameter, THE RAG_System SHALL update the UI immediately
3. WHEN a user submits a query, THE RAG_System SHALL use the current parameter values
4. THE RAG_System SHALL validate parameter values (top-k: 1-20, threshold: 0-1)
5. THE RAG_System SHALL persist parameter values in local storage

### Requirement 8: Evaluation Metrics Display

**User Story:** As a researcher, I want to see evaluation metrics, so that I can assess answer quality.

#### Acceptance Criteria

1. WHEN an answer is generated, THE RAG_System SHALL display faithfulness, relevance, and context precision scores
2. THE Evaluation_Metrics SHALL be displayed as colored badges (green >0.8, yellow 0.5-0.8, red <0.5)
3. WHEN a user hovers over a metric, THE RAG_System SHALL display a tooltip explaining the metric
4. WHEN metrics are unavailable, THE RAG_System SHALL display "N/A" instead of a score
5. THE Evaluation_Metrics SHALL update in real-time as the answer streams

### Requirement 9: Query History

**User Story:** As a researcher, I want to save queries and answers, so that I can revisit them later.

#### Acceptance Criteria

1. WHEN a query completes, THE RAG_System SHALL save the query, answer, and evidence to Query_History
2. WHEN a user opens the history sidebar, THE RAG_System SHALL display all saved queries in reverse chronological order
3. WHEN a user clicks a history item, THE RAG_System SHALL load the query, answer, and evidence
4. WHEN a user deletes a history item, THE RAG_System SHALL remove it from storage
5. THE Query_History SHALL persist in local storage and support up to 100 entries

### Requirement 10: Export Functionality

**User Story:** As a researcher, I want to export answers as Markdown or PDF, so that I can share them with collaborators.

#### Acceptance Criteria

1. WHEN a user clicks the export button, THE RAG_System SHALL display export format options (Markdown, PDF, JSON)
2. WHEN Markdown is selected, THE RAG_System SHALL generate a Markdown file with answer, citations, and metadata
3. WHEN PDF is selected, THE RAG_System SHALL generate a PDF with formatted answer, citations, and metadata
4. WHEN JSON is selected, THE RAG_System SHALL generate a JSON file with the complete query response
5. THE exported file SHALL include a timestamp and query text in the filename

### Requirement 11: Code Snippet Highlighting

**User Story:** As a researcher, I want to see code snippets highlighted in the answer, so that I can read code more easily.

#### Acceptance Criteria

1. WHEN the answer contains code blocks, THE Answer_Panel SHALL apply syntax highlighting
2. THE RAG_System SHALL detect the programming language automatically or use a default
3. WHEN a user hovers over a code block, THE RAG_System SHALL display a copy button
4. WHEN the copy button is clicked, THE RAG_System SHALL copy the code to the clipboard
5. THE code highlighting SHALL support at least 10 common languages (Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL, HTML, CSS)

### Requirement 12: Responsive Design

**User Story:** As a researcher, I want to use the RAG interface on any device, so that I can query my knowledge base anywhere.

#### Acceptance Criteria

1. WHEN the viewport width is below 768px, THE RAG_System SHALL stack the Answer_Panel and Evidence_Panel vertically
2. WHEN on mobile, THE RAG_System SHALL provide a tab interface to switch between answer and evidence
3. WHEN on mobile, THE RAG_System SHALL hide the query history sidebar by default
4. WHEN on mobile, THE RAG_System SHALL provide a hamburger menu to access controls
5. THE RAG_System SHALL maintain functionality on screen widths from 320px to 2560px

### Requirement 13: Accessibility

**User Story:** As a researcher with disabilities, I want to use the RAG interface with assistive technologies, so that I can access the same features as other users.

#### Acceptance Criteria

1. THE RAG_System SHALL support keyboard navigation for all interactive elements
2. WHEN a user tabs through the interface, THE RAG_System SHALL provide visible focus indicators
3. THE RAG_System SHALL provide ARIA labels for all icons and icon-only buttons
4. WHEN the answer streams, THE RAG_System SHALL announce updates to screen readers using ARIA live regions
5. THE RAG_System SHALL maintain a color contrast ratio of at least 4.5:1 for all text

### Requirement 14: Performance

**User Story:** As a researcher, I want the RAG interface to respond quickly, so that I can work efficiently.

#### Acceptance Criteria

1. WHEN a query is submitted, THE RAG_System SHALL display the first answer chunk within 2 seconds
2. WHEN resizing the split pane, THE RAG_System SHALL update the layout within 16ms (60fps)
3. WHEN scrolling the Evidence_Panel, THE RAG_System SHALL maintain smooth scrolling at 60fps
4. WHEN loading query history, THE RAG_System SHALL display the list within 500ms
5. THE RAG_System SHALL support up to 100 concurrent chunks in the Evidence_Panel without performance degradation

### Requirement 15: Error Handling

**User Story:** As a researcher, I want clear error messages when something goes wrong, so that I can understand and resolve issues.

#### Acceptance Criteria

1. WHEN the backend is unreachable, THE RAG_System SHALL display a connection error with retry option
2. WHEN a query times out, THE RAG_System SHALL display a timeout error with option to increase timeout
3. WHEN the query is invalid, THE RAG_System SHALL display validation errors inline
4. WHEN streaming fails, THE RAG_System SHALL display the partial answer with an error indicator
5. THE RAG_System SHALL log all errors to the browser console for debugging
