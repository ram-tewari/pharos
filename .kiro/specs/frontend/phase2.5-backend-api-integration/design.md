# Design Document: Phase 2.5 - Backend API Integration

## Overview

Phase 2.5 integrates the frontend components from Phase 1 and Phase 2 with the live backend API. This design focuses on creating a robust API client layer, updating Zustand stores to fetch real data, implementing proper error handling, and ensuring type safety across the frontend-backend boundary.

**Key Design Principles:**
- **Type Safety**: All API interactions are fully typed with TypeScript
- **Error Resilience**: Graceful degradation with retry logic and fallbacks
- **Performance**: Intelligent caching and request deduplication
- **Developer Experience**: Clear error messages and debugging tools
- **Testability**: Comprehensive mocks and integration tests

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Components                        │
│  (WorkbenchLayout, MonacoEditor, AnnotationPanel, etc.)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Zustand Stores                            │
│  (editor, annotation, chunk, quality, workbench, etc.)      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  TanStack Query Layer                       │
│         (useQuery, useMutation, queryClient)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Client Layer                         │
│  (axios instance, interceptors, retry logic)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend API (pharos.onrender.com)              │
│  (FastAPI, 90+ endpoints, JWT auth, rate limiting)          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Patterns

**Pattern 1: Simple Read (GET)**
```
Component → useQuery → API Client → Backend → Cache → Component
```

**Pattern 2: Mutation with Optimistic Update (POST/PUT/DELETE)**
```
Component → useMutation → Optimistic Update → API Client → Backend
                                                    ↓
                                              Success/Failure
                                                    ↓
                                          Confirm or Revert Update
```

**Pattern 3: Polling (Status Checks)**
```
Component → useQuery (refetchInterval) → API Client → Backend → Component
```



## Components and Interfaces

### 1. API Client Core (`frontend/src/core/api/client.ts`)

**Purpose**: Central axios instance with interceptors and configuration

**Interface**:
```typescript
// Configuration
interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

// Axios instance with interceptors
export const apiClient: AxiosInstance;

// Helper functions
export function setAuthToken(token: string): void;
export function clearAuthToken(): void;
export function getAuthToken(): string | null;
```

**Key Features**:
- Base URL from environment variable (`VITE_API_BASE_URL`)
- Request interceptor adds JWT token to Authorization header
- Response interceptor handles common errors (401, 403, 429, 500)
- Retry logic with exponential backoff (3 attempts, 1s → 2s → 4s)
- Request/response logging in development mode

### 2. API Client Modules

**Phase 1 API Client** (`frontend/src/lib/api/workbench.ts`):
```typescript
export const workbenchApi = {
  // Auth endpoints
  getCurrentUser: () => Promise<User>,
  getRateLimit: () => Promise<RateLimitStatus>,
  
  // Resource endpoints
  getResources: (params?: ResourceListParams) => Promise<Resource[]>,
  
  // Health endpoints
  getSystemHealth: () => Promise<HealthStatus>,
  getAuthHealth: () => Promise<ModuleHealth>,
  getResourcesHealth: () => Promise<ModuleHealth>,
};
```

**Phase 2 API Client** (`frontend/src/lib/api/editor.ts`):
```typescript
export const editorApi = {
  // Resource content
  getResource: (resourceId: string) => Promise<Resource>,
  getResourceStatus: (resourceId: string) => Promise<ProcessingStatus>,
  
  // Chunks
  getChunks: (resourceId: string) => Promise<SemanticChunk[]>,
  getChunk: (chunkId: string) => Promise<SemanticChunk>,
  triggerChunking: (resourceId: string) => Promise<ChunkingTask>,
  
  // Annotations
  createAnnotation: (resourceId: string, data: AnnotationCreate) => Promise<Annotation>,
  getAnnotations: (resourceId: string) => Promise<Annotation[]>,
  updateAnnotation: (annotationId: string, data: AnnotationUpdate) => Promise<Annotation>,
  deleteAnnotation: (annotationId: string) => Promise<void>,
  searchAnnotationsFulltext: (params: SearchParams) => Promise<Annotation[]>,
  searchAnnotationsSemantic: (params: SearchParams) => Promise<Annotation[]>,
  searchAnnotationsByTags: (tags: string[]) => Promise<Annotation[]>,
  exportAnnotationsMarkdown: (resourceId?: string) => Promise<string>,
  exportAnnotationsJSON: (resourceId?: string) => Promise<AnnotationExport>,
  
  // Quality
  recalculateQuality: (resourceId: string) => Promise<QualityDetails>,
  getQualityOutliers: (params?: PaginationParams) => Promise<QualityOutlier[]>,
  getQualityDegradation: (days: number) => Promise<QualityDegradation>,
  getQualityDistribution: (bins: number) => Promise<QualityDistribution>,
  getQualityTrends: (granularity: 'daily' | 'weekly' | 'monthly') => Promise<QualityTrend[]>,
  getQualityDimensions: () => Promise<QualityDimensionScores>,
  getQualityReviewQueue: (params?: PaginationParams) => Promise<ReviewQueueItem[]>,
  
  // Graph/Hover
  getHoverInfo: (params: HoverParams) => Promise<HoverInfo>,
};
```

### 3. TanStack Query Hooks

**Workbench Hooks** (`frontend/src/lib/hooks/useWorkbenchData.ts`):
```typescript
export function useCurrentUser() {
  return useQuery({
    queryKey: ['user', 'current'],
    queryFn: workbenchApi.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useResources(params?: ResourceListParams) {
  return useQuery({
    queryKey: ['resources', params],
    queryFn: () => workbenchApi.getResources(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['health', 'system'],
    queryFn: workbenchApi.getSystemHealth,
    refetchInterval: 30 * 1000, // Poll every 30 seconds
  });
}
```

**Editor Hooks** (`frontend/src/lib/hooks/useEditorData.ts`):
```typescript
export function useResource(resourceId: string) {
  return useQuery({
    queryKey: ['resource', resourceId],
    queryFn: () => editorApi.getResource(resourceId),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useChunks(resourceId: string) {
  return useQuery({
    queryKey: ['chunks', resourceId],
    queryFn: () => editorApi.getChunks(resourceId),
    staleTime: 10 * 60 * 1000,
  });
}

export function useAnnotations(resourceId: string) {
  return useQuery({
    queryKey: ['annotations', resourceId],
    queryFn: () => editorApi.getAnnotations(resourceId),
    staleTime: 5 * 60 * 1000,
  });
}

// Mutations
export function useCreateAnnotation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ resourceId, data }: { resourceId: string; data: AnnotationCreate }) =>
      editorApi.createAnnotation(resourceId, data),
    onMutate: async ({ resourceId, data }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['annotations', resourceId] });
      const previous = queryClient.getQueryData(['annotations', resourceId]);
      
      queryClient.setQueryData(['annotations', resourceId], (old: Annotation[]) => [
        ...old,
        { ...data, id: 'temp-' + Date.now(), created_at: new Date().toISOString() },
      ]);
      
      return { previous };
    },
    onError: (err, variables, context) => {
      // Revert optimistic update
      queryClient.setQueryData(['annotations', variables.resourceId], context?.previous);
    },
    onSettled: (data, error, variables) => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['annotations', variables.resourceId] });
    },
  });
}
```

### 4. Zustand Store Updates

**Editor Store** (`frontend/src/stores/editor.ts`):
```typescript
interface EditorStore {
  // State
  currentResourceId: string | null;
  content: string | null;
  isLoading: boolean;
  error: Error | null;
  
  // Actions
  loadResource: (resourceId: string) => Promise<void>;
  clearResource: () => void;
  setError: (error: Error | null) => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  currentResourceId: null,
  content: null,
  isLoading: false,
  error: null,
  
  loadResource: async (resourceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const resource = await editorApi.getResource(resourceId);
      set({
        currentResourceId: resourceId,
        content: resource.content,
        isLoading: false,
      });
    } catch (error) {
      set({ error: error as Error, isLoading: false });
    }
  },
  
  clearResource: () => set({ currentResourceId: null, content: null }),
  setError: (error) => set({ error }),
}));
```

**Annotation Store** (`frontend/src/stores/annotation.ts`):
```typescript
interface AnnotationStore {
  // State
  annotations: Map<string, Annotation>;
  selectedAnnotationId: string | null;
  isCreating: boolean;
  
  // Actions (now use TanStack Query mutations)
  selectAnnotation: (id: string | null) => void;
  clearAnnotations: () => void;
}

// Note: CRUD operations moved to TanStack Query hooks
export const useAnnotationStore = create<AnnotationStore>((set) => ({
  annotations: new Map(),
  selectedAnnotationId: null,
  isCreating: false,
  
  selectAnnotation: (id) => set({ selectedAnnotationId: id }),
  clearAnnotations: () => set({ annotations: new Map(), selectedAnnotationId: null }),
}));
```

### 5. TypeScript Type Definitions

**API Types** (`frontend/src/types/api.ts`):
```typescript
// User types
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_premium: boolean;
  tier: 'free' | 'premium' | 'admin';
  created_at: string;
}

// Resource types
export interface Resource {
  id: string;
  title: string;
  content: string;
  content_type: 'code' | 'pdf' | 'markdown' | 'text';
  language?: string;
  file_path?: string;
  url?: string;
  created_at: string;
  updated_at: string;
  quality_overall?: number;
  quality_dimensions?: QualityDimensions;
}

// Annotation types
export interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];
  created_at: string;
  updated_at: string;
}

// Chunk types
export interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: ChunkMetadata;
  embedding_id?: string;
  created_at: string;
}

export interface ChunkMetadata {
  function_name?: string;
  class_name?: string;
  start_line: number;
  end_line: number;
  language: string;
  node_type?: string;
}

// Quality types
export interface QualityDimensions {
  accuracy: number;
  completeness: number;
  consistency: number;
  timeliness: number;
  relevance: number;
}

export interface QualityDetails {
  resource_id: string;
  quality_dimensions: QualityDimensions;
  quality_overall: number;
  quality_weights: QualityDimensions;
  quality_last_computed: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
}

// Error types
export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'VALIDATION_ERROR';

export interface ApiError {
  code: ApiErrorCode;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}
```



## Data Models

### Environment Configuration

```typescript
// frontend/.env
VITE_API_BASE_URL=https://pharos.onrender.com
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000
```

### Request/Response Flow

**Example: Create Annotation**

1. **User Action**: User highlights text and clicks "Add Note"
2. **Optimistic Update**: UI immediately shows new annotation with temp ID
3. **API Request**: POST `/annotations` with annotation data
4. **Backend Processing**: Backend validates, saves to DB, returns annotation with real ID
5. **Success**: Replace temp annotation with real annotation from backend
6. **Failure**: Revert optimistic update, show error toast

**Example: Load Resource**

1. **User Action**: User clicks on a resource in the repository switcher
2. **Loading State**: Show skeleton loader in editor
3. **API Request**: GET `/resources/{resource_id}`
4. **Parallel Requests**: 
   - GET `/resources/{resource_id}/chunks` (semantic chunks)
   - GET `/annotations?resource_id={resource_id}` (annotations)
5. **Backend Processing**: Backend fetches resource, chunks, and annotations
6. **Success**: Render content in Monaco editor with overlays
7. **Failure**: Show error message with retry button

### Caching Strategy

**TanStack Query Cache Configuration**:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes default
      cacheTime: 10 * 60 * 1000, // 10 minutes default
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});
```

**Cache Invalidation Rules**:
- **User data**: Invalidate on login/logout
- **Resources**: Invalidate on create/update/delete
- **Annotations**: Invalidate on create/update/delete
- **Chunks**: Invalidate on manual re-chunking
- **Quality**: Invalidate on recalculation
- **Health**: Auto-refresh every 30 seconds (no invalidation needed)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication Token Persistence

*For any* authenticated user session, if the user refreshes the page, then the authentication token should persist and the user should remain logged in.

**Validates: Requirements 1.2**

### Property 2: Optimistic Update Consistency

*For any* mutation operation (create, update, delete), if the API call fails, then the optimistic UI update should be reverted to the previous state.

**Validates: Requirements 4.10**

### Property 3: Request Retry Idempotency

*For any* failed API request, retrying the request should produce the same result as the original request (no duplicate side effects).

**Validates: Requirements 1.5**

### Property 4: Error Code Mapping

*For any* HTTP error status code, the frontend should map it to a user-friendly error message and appropriate action (retry, redirect, or display).

**Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7**

### Property 5: Cache Invalidation Correctness

*For any* mutation that modifies server state, all related cached queries should be invalidated to ensure data consistency.

**Validates: Requirements 2.6, 3.6, 4.10**

### Property 6: Type Safety at Runtime

*For any* API response, if the response does not match the expected TypeScript type, then the frontend should throw a validation error in development mode.

**Validates: Requirements 7.5**

### Property 7: Loading State Visibility

*For any* API request in progress, the UI should display a loading indicator until the request completes or fails.

**Validates: Requirements 8.1**

### Property 8: Debounce Consistency

*For any* debounced API call (e.g., hover requests), if multiple calls are triggered within the debounce window, then only the last call should execute.

**Validates: Requirements 6.2**

## Error Handling

### Error Classification

**1. Network Errors**
- **Cause**: No internet connection, DNS failure, timeout
- **Handling**: Display "Connection Lost" toast, enable retry button
- **Retry**: Automatic retry with exponential backoff (3 attempts)

**2. Authentication Errors (401)**
- **Cause**: Invalid or expired JWT token
- **Handling**: Clear auth token, redirect to login page
- **Retry**: No automatic retry (user must re-authenticate)

**3. Authorization Errors (403)**
- **Cause**: User lacks permission for the requested resource
- **Handling**: Display "Access Denied" message
- **Retry**: No retry (permission issue)

**4. Not Found Errors (404)**
- **Cause**: Resource does not exist
- **Handling**: Display "Resource Not Found" message
- **Retry**: No retry (resource doesn't exist)

**5. Rate Limit Errors (429)**
- **Cause**: User exceeded rate limit
- **Handling**: Display rate limit info with cooldown timer
- **Retry**: Automatic retry after cooldown period

**6. Server Errors (500, 502, 503)**
- **Cause**: Backend error or service unavailable
- **Handling**: Display "Server Error" message with retry button
- **Retry**: Automatic retry with exponential backoff (3 attempts)

**7. Validation Errors (400)**
- **Cause**: Invalid request payload
- **Handling**: Display validation error details
- **Retry**: No automatic retry (user must fix input)

### Error Recovery Strategies

**Strategy 1: Exponential Backoff**
```typescript
const retryDelay = (attemptIndex: number) => {
  return Math.min(1000 * 2 ** attemptIndex, 30000);
};
// Attempt 1: 1s delay
// Attempt 2: 2s delay
// Attempt 3: 4s delay
// Max: 30s delay
```

**Strategy 2: Circuit Breaker**
```typescript
// If 5 consecutive requests fail, stop retrying for 60 seconds
const circuitBreaker = {
  failureCount: 0,
  threshold: 5,
  timeout: 60000,
  isOpen: false,
};
```

**Strategy 3: Fallback Data**
```typescript
// Use cached data if API fails
const { data, error } = useQuery({
  queryKey: ['resource', resourceId],
  queryFn: () => editorApi.getResource(resourceId),
  placeholderData: (previousData) => previousData, // Use stale data as fallback
});
```

### Error UI Components

**Toast Notifications** (for transient errors):
- Network errors
- Rate limit warnings
- Temporary server errors

**Inline Error Messages** (for persistent errors):
- Validation errors
- Not found errors
- Access denied errors

**Error Boundaries** (for catastrophic errors):
- Unhandled exceptions
- Component render errors
- Critical API failures

## Testing Strategy

### Unit Tests

**API Client Tests** (`frontend/src/core/api/client.test.ts`):
- Test request interceptor adds auth token
- Test response interceptor handles 401/403/429/500 errors
- Test retry logic with exponential backoff
- Test timeout handling
- Test request/response logging

**TanStack Query Hook Tests** (`frontend/src/lib/hooks/useEditorData.test.ts`):
- Test query caching behavior
- Test query invalidation on mutations
- Test optimistic updates
- Test error handling
- Test loading states

**Zustand Store Tests** (`frontend/src/stores/editor.test.ts`):
- Test state updates
- Test async actions
- Test error handling
- Test state persistence

### Integration Tests

**Annotation Flow Test**:
```typescript
test('complete annotation lifecycle', async () => {
  // 1. Load resource
  const { result } = renderHook(() => useResource('resource-1'));
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  
  // 2. Create annotation
  const { result: createResult } = renderHook(() => useCreateAnnotation());
  act(() => {
    createResult.current.mutate({
      resourceId: 'resource-1',
      data: { start_offset: 0, end_offset: 10, highlighted_text: 'test' },
    });
  });
  
  // 3. Verify optimistic update
  const { result: annotationsResult } = renderHook(() => useAnnotations('resource-1'));
  expect(annotationsResult.current.data).toHaveLength(1);
  
  // 4. Wait for API confirmation
  await waitFor(() => expect(createResult.current.isSuccess).toBe(true));
  
  // 5. Update annotation
  const { result: updateResult } = renderHook(() => useUpdateAnnotation());
  act(() => {
    updateResult.current.mutate({
      annotationId: 'annotation-1',
      data: { note: 'Updated note' },
    });
  });
  
  // 6. Delete annotation
  const { result: deleteResult } = renderHook(() => useDeleteAnnotation());
  act(() => {
    deleteResult.current.mutate('annotation-1');
  });
  
  // 7. Verify deletion
  await waitFor(() => expect(annotationsResult.current.data).toHaveLength(0));
});
```

**Error Recovery Test**:
```typescript
test('recovers from API failure', async () => {
  // 1. Mock API failure
  server.use(
    rest.get('/resources/:id', (req, res, ctx) => {
      return res.once(ctx.status(500));
    })
  );
  
  // 2. Attempt to load resource
  const { result } = renderHook(() => useResource('resource-1'));
  
  // 3. Verify error state
  await waitFor(() => expect(result.current.isError).toBe(true));
  
  // 4. Mock API success
  server.use(
    rest.get('/resources/:id', (req, res, ctx) => {
      return res(ctx.json({ id: 'resource-1', content: 'test' }));
    })
  );
  
  // 5. Retry request
  act(() => {
    result.current.refetch();
  });
  
  // 6. Verify success
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
});
```

### Mock Service Worker (MSW) Updates

**Updated Handlers** (`frontend/src/test/mocks/handlers.ts`):
```typescript
export const handlers = [
  // Auth endpoints
  rest.get('/api/auth/me', (req, res, ctx) => {
    return res(ctx.json({
      id: 'user-1',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      is_premium: false,
      tier: 'free',
      created_at: '2024-01-01T00:00:00Z',
    }));
  }),
  
  // Resource endpoints
  rest.get('/resources/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(ctx.json({
      id,
      title: 'Test Resource',
      content: 'function test() { return true; }',
      content_type: 'code',
      language: 'typescript',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }));
  }),
  
  // Annotation endpoints
  rest.post('/annotations', async (req, res, ctx) => {
    const body = await req.json();
    return res(ctx.json({
      ...body,
      id: 'annotation-' + Date.now(),
      user_id: 'user-1',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }));
  }),
  
  // Error scenarios
  rest.get('/resources/error-500', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ detail: 'Internal Server Error' }));
  }),
  
  rest.get('/resources/error-404', (req, res, ctx) => {
    return res(ctx.status(404), ctx.json({ detail: 'Resource not found' }));
  }),
];
```

### Property-Based Tests

**Property Test Configuration**:
- Use `fast-check` library for property-based testing
- Minimum 100 iterations per property test
- Tag each test with property number from design document

**Example Property Test**:
```typescript
import fc from 'fast-check';

test('Property 2: Optimistic Update Consistency', () => {
  fc.assert(
    fc.asyncProperty(
      fc.record({
        resourceId: fc.string(),
        annotation: fc.record({
          start_offset: fc.nat(),
          end_offset: fc.nat(),
          highlighted_text: fc.string(),
        }),
      }),
      async ({ resourceId, annotation }) => {
        // Feature: phase2.5-backend-api-integration, Property 2: Optimistic Update Consistency
        
        // Setup: Mock API failure
        server.use(
          rest.post('/annotations', (req, res, ctx) => {
            return res(ctx.status(500));
          })
        );
        
        // Execute: Create annotation
        const { result } = renderHook(() => useCreateAnnotation());
        const { result: annotationsResult } = renderHook(() => useAnnotations(resourceId));
        
        const initialCount = annotationsResult.current.data?.length || 0;
        
        act(() => {
          result.current.mutate({ resourceId, data: annotation });
        });
        
        // Verify: Optimistic update applied
        expect(annotationsResult.current.data).toHaveLength(initialCount + 1);
        
        // Wait for API failure
        await waitFor(() => expect(result.current.isError).toBe(true));
        
        // Verify: Optimistic update reverted
        expect(annotationsResult.current.data).toHaveLength(initialCount);
      }
    ),
    { numRuns: 100 }
  );
});
```

