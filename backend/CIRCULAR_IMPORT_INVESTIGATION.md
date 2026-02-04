# Circular Import Investigation - 2026-02-02

## Problem
App initialization hangs indefinitely during test mode, preventing test execution.

## Root Cause Analysis

### Initial Hypothesis: Lifespan Events
- **TESTED**: Lifespan function with embedding warmup and Redis initialization
- **RESULT**: ✓ Works fine when tested in isolation
- **FIX APPLIED**: Skip heavy initialization in test mode (embedding warmup, Redis)

### Second Hypothesis: Search Module Circular Import
- **TESTED**: Search module imports
- **RESULT**: ✗ Search module hangs on import
- **CIRCULAR DEPENDENCY FOUND**:
  ```
  search_service.py → modules.search.rrf
  modules.search.__init__.py → modules.search.router  
  modules.search.router → services.search_service
  ```
- **FIX APPLIED**: 
  - Made `AdvancedSearchService` import lazy in search router
  - Made `SearchService` import lazy in search router
  - Changed module registration to import router directly
- **RESULT**: ✗ Still hangs - even search.schema hangs on import

### Third Hypothesis: Module Registration
- **TESTED**: Individual module imports (collections, resources, auth)
- **RESULT**: ✓ All modules import fine individually
- **TESTED**: `register_all_modules()` function
- **RESULT**: ✗ Hangs even with minimal modules (collections, resources, auth)

### Current Status
- **BLOCKER**: `register_all_modules()` hangs even with minimal module set
- **MODULES TESTED**: collections ✓, resources ✓, auth ✓
- **ISSUE**: Something in the module registration loop is causing infinite hang
- **NEXT STEP**: Add debug logging to `register_all_modules()` to identify exact hang point

## Files Modified
1. `backend/app/__init__.py`:
   - Added test mode check in lifespan to skip heavy initialization
   - Temporarily disabled search module registration
   - Temporarily disabled most modules to isolate issue

2. `backend/app/modules/search/router.py`:
   - Made `AdvancedSearchService` import lazy
   - Made `SearchService` import lazy
   - Replaced all usages with lazy import functions

## Recommendations
1. Add detailed logging to `register_all_modules()` to identify hang point
2. Consider using `importlib` with timeout for module imports
3. May need to refactor module registration to avoid blocking imports
4. Consider using background threads for module registration
5. Investigate if there's a deadlock in the import system

## Time Spent
- Lifespan investigation: 30 min
- Circular import investigation: 60 min
- Module registration investigation: 30 min
- **Total**: 2 hours

## Impact
- **Tests blocked**: Cannot run any tests that require app initialization
- **Affected tests**: ~300+ tests that use `async_client` or `client` fixtures
- **Workaround**: Tests that don't need full app can still run (e.g., service tests)
