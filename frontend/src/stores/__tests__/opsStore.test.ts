import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOpsStore } from '../opsStore';
import type { TimeRange, ModuleFilter } from '../opsStore';

describe('Ops Store', () => {
  beforeEach(() => {
    const { result } = renderHook(() => useOpsStore());
    act(() => {
      result.current.setTimeRange('24h');
      result.current.setModuleFilter('all');
      if (!result.current.autoRefresh) {
        result.current.toggleAutoRefresh();
      }
    });
  });

  describe('Initial State', () => {
    it('should have default time range', () => {
      const { result } = renderHook(() => useOpsStore());
      expect(result.current.timeRange).toBe('24h');
    });

    it('should have auto-refresh enabled initially', () => {
      const { result } = renderHook(() => useOpsStore());
      expect(result.current.autoRefresh).toBe(true);
    });

    it('should have "all" module filter initially', () => {
      const { result } = renderHook(() => useOpsStore());
      expect(result.current.moduleFilter).toBe('all');
    });
  });

  describe('Time Range Management', () => {
    it('should set time range', () => {
      const { result } = renderHook(() => useOpsStore());
      
      act(() => {
        result.current.setTimeRange('1h');
      });

      expect(result.current.timeRange).toBe('1h');
    });

    it('should accept all valid time ranges', () => {
      const { result } = renderHook(() => useOpsStore());
      const validRanges: TimeRange[] = ['1h', '6h', '24h', '7d'];

      validRanges.forEach((range) => {
        act(() => {
          result.current.setTimeRange(range);
        });
        expect(result.current.timeRange).toBe(range);
      });
    });
  });

  describe('Auto-Refresh', () => {
    it('should toggle auto-refresh', () => {
      const { result } = renderHook(() => useOpsStore());
      const initialState = result.current.autoRefresh;
      
      act(() => {
        result.current.toggleAutoRefresh();
      });

      expect(result.current.autoRefresh).toBe(!initialState);
    });

    it('should toggle auto-refresh multiple times', () => {
      const { result } = renderHook(() => useOpsStore());
      
      act(() => {
        result.current.toggleAutoRefresh();
        result.current.toggleAutoRefresh();
        result.current.toggleAutoRefresh();
      });

      expect(result.current.autoRefresh).toBe(false);
    });
  });

  describe('Module Filter', () => {
    it('should set module filter', () => {
      const { result } = renderHook(() => useOpsStore());
      
      act(() => {
        result.current.setModuleFilter('healthy');
      });

      expect(result.current.moduleFilter).toBe('healthy');
    });

    it('should accept all valid module filters', () => {
      const { result } = renderHook(() => useOpsStore());
      const validFilters: ModuleFilter[] = ['all', 'healthy', 'degraded', 'down'];

      validFilters.forEach((filter) => {
        act(() => {
          result.current.setModuleFilter(filter);
        });
        expect(result.current.moduleFilter).toBe(filter);
      });
    });
  });

  describe('State Persistence', () => {
    it('should maintain state across multiple operations', () => {
      const { result } = renderHook(() => useOpsStore());
      
      act(() => {
        result.current.setTimeRange('6h');
        result.current.setModuleFilter('degraded');
        result.current.toggleAutoRefresh();
      });

      expect(result.current.timeRange).toBe('6h');
      expect(result.current.moduleFilter).toBe('degraded');
      expect(result.current.autoRefresh).toBe(false);
    });
  });
});
