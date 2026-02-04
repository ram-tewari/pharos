# Priority 2: Missing Tests - Implementation Plan

**Status**: In Progress  
**Estimated Effort**: Large (47 property tests + unit tests + E2E tests)

## Strategy

Given the large scope, we'll implement tests in batches:

### Batch 1: Critical Property Tests (Properties 3, 6-14) - 12 tests
**Focus**: Core graph functionality and hypothesis features

1. Property 3: Node Selection State
2. Property 6: Neighbor Count Limit
3. Property 7: Threshold Filtering
4. Property 8: Node Size Proportionality
5. Property 9: Top Connected Highlighting
6. Property 10: Hypothesis Ranking
7. Property 11: Hypothesis Path Visualization
8. Property 12: Hidden Connection Styling ✅ (already in CustomEdge)
9. Property 13: Contradiction Indicator ✅ (already in ResourceNode)
10. Property 14: Research Gap Visualization

### Batch 2: Search & Filter Tests (Properties 15-18) - 4 tests
**Focus**: Search and filtering functionality

11. Property 15: Search Filtering
12. Property 16: Search Result Highlighting
13. Property 17: Filter Application
14. Property 18: Filter Badge Count

### Batch 3: Entity & Relationship Tests (Properties 19-25) - 7 tests
**Focus**: Entity nodes and relationships

15. Property 19: Entity Node Shape Distinction
16. Property 20: Semantic Triple Display
17. Property 21: Traverse Button Visibility
18. Property 22: Traversal Path Highlighting
19. Property 23: Relationship Label Display
20. Property 24: Contradiction Icon Display ✅ (already tested)
21. Property 25: Supporting Evidence Icon Display

### Batch 4: Interaction Tests (Properties 27-30, 33) - 5 tests
**Focus**: User interactions and preferences

22. Property 27: Indicator Preference Persistence
23. Property 28: Mouse Wheel Zoom
24. Property 29: Minimap Click Navigation
25. Property 30: Keyboard Shortcut Handling
26. Property 33: Focus Mode Dimming

### Batch 5: Export & Sharing Tests (Properties 34-36) - 3 tests
**Focus**: Export and sharing functionality

27. Property 34: Export Filename Timestamp
28. Property 35: Export Progress Indicator
29. Property 36: Shareable Link State Restoration

### Batch 6: Accessibility Tests (Properties 37-44) - 8 tests
**Focus**: Accessibility compliance

30. Property 37: Touch Zoom and Pan
31. Property 38: Keyboard Navigation
32. Property 39: ARIA Label Presence
33. Property 40: Screen Reader Announcements
34. Property 41: High Contrast Mode
35. Property 42: Node Size Adjustment
36. Property 43: Reduced Motion Compliance
37. Property 44: Minimum Touch Target Size

### Batch 7: Performance Tests (Properties 45, 47-55) - 9 tests
**Focus**: Performance optimization

38. Property 45: Progressive Rendering Activation
39. Property 47: Graph Data Caching
40. Property 48: Lazy Node Details Loading
41. Property 49: Web Worker Offloading
42. Property 50: Layout Algorithm Performance
43. Property 51: Memory Usage Limit
44. Property 52: Viewport Culling
45. Property 53: Edge Bundling Activation
46. Property 54: LOD Rendering
47. Property 55: Animation Frame Budget

### Unit Tests
**Components to test**:
- GraphPage
- GraphToolbar
- GraphCanvas
- ResourceNode
- EntityNode
- CustomEdge
- FilterPanel
- NodeDetailsPanel
- HypothesisPanel ✅ (Priority 1)
- HypothesisDiscoveryModal ✅ (Priority 1)
- ExportModal
- LegendPanel

### E2E Tests
**Workflows to test**:
1. Complete graph exploration workflow
2. Hypothesis discovery workflow
3. Search and filter workflow
4. Export workflow
5. Entity traversal workflow

## Execution Plan

### Phase 1: Start with Batch 1 (Critical Tests)
- Implement 12 core property tests
- Verify all pass
- Mark tasks complete

### Phase 2: Continue with Batches 2-3
- Search/filter tests
- Entity/relationship tests

### Phase 3: Batches 4-5
- Interaction tests
- Export/sharing tests

### Phase 4: Batches 6-7
- Accessibility tests
- Performance tests

### Phase 5: Unit & E2E Tests
- Component unit tests
- Integration E2E tests

## Current Status

- ✅ 8 property tests implemented (Properties 1, 2, 4, 5, 26, 31, 32, 46)
- ⏳ 47 property tests remaining
- ⏳ Unit tests needed
- ⏳ E2E tests needed

## Next Action

**Start with Batch 1**: Implement Properties 3, 6-14 (12 critical tests)
