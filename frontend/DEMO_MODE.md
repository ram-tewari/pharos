# Demo Mode

Demo mode allows you to preview the Neo Alexandria UI with mock data when the backend is offline.

## Enabling Demo Mode

1. Create or edit `.env.local` in the frontend directory:
```bash
VITE_DEMO_MODE=true
```

2. Restart the dev server:
```bash
npm run dev
```

3. You'll see a blue banner at the top indicating demo mode is active.

## What's Included

### Phase 1: Workbench & Navigation
- ✅ Sidebar navigation
- ✅ Command palette (Cmd+K)
- ✅ Repository switcher (3 demo repos)
- ✅ Theme toggle

### Phase 2: Code Editor
- ✅ Monaco editor with syntax highlighting
- ✅ Semantic chunk overlays (AST-based)
- ✅ Quality badges with scores
- ✅ Annotation gutter with 2 demo annotations
- ✅ Reference hover cards

### Phase 2.5: API Integration
- ✅ Mock API responses with realistic delays
- ✅ TanStack Query integration
- ✅ Loading states
- ✅ Error handling

### Phase 3: Library
- ✅ Document grid with 4 demo papers
- ✅ PDF viewer (placeholder)
- ✅ Collection manager (4 demo collections)
- ✅ Equation/Table drawers
- ✅ Batch operations
- ✅ Related code/papers panels

## Demo Data

### Repositories
- `react-query` - TanStack Query library
- `zustand` - State management
- `fastapi` - Python web framework

### Documents
- Attention Is All You Need (Transformer paper)
- BERT paper
- ResNet paper
- GAN paper

### Collections
- Machine Learning
- Natural Language Processing
- Computer Vision
- Generative Models

### Code File
- `useQuery.ts` from react-query
- 3 semantic chunks
- 2 annotations
- Quality scores

## Disabling Demo Mode

Set `VITE_DEMO_MODE=false` or remove the variable from `.env.local`, then restart the dev server.

## Notes

- Demo mode simulates API delays (100-600ms) for realistic UX
- All data is static and defined in `src/lib/demo/config.ts`
- No data is persisted - refreshing resets everything
- Backend API calls are completely bypassed in demo mode
