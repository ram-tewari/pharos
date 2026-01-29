import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCurationStore } from '../curationStore';
import type { CurationStatus } from '@/types/curation';

describe('Curation Store', () => {
  beforeEach(() => {
    const { result } = renderHook(() => useCurationStore());
    act(() => {
      result.current.clearSelection();
      result.current.setStatusFilter('all');
      result.current.setQualityThreshold(0.5);
      result.current.setCurrentPage(1);
    });
  });

  describe('Initial State', () => {
    it('should have empty selected IDs initially', () => {
      const { result } = renderHook(() => useCurationStore());
      expect(result.current.selectedIds.size).toBe(0);
    });

    it('should have "all" status filter initially', () => {
      const { result } = renderHook(() => useCurationStore());
      expect(result.current.statusFilter).toBe('all');
    });

    it('should have default quality threshold', () => {
      const { result } = renderHook(() => useCurationStore());
      expect(result.current.qualityThreshold).toBe(0.5);
    });

    it('should start at page 1', () => {
      const { result } = renderHook(() => useCurationStore());
      expect(result.current.currentPage).toBe(1);
    });
  });

  describe('Selection Management', () => {
    it('should toggle selection', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.toggleSelection('id-1');
      });

      expect(result.current.selectedIds.has('id-1')).toBe(true);

      act(() => {
        result.current.toggleSelection('id-1');
      });

      expect(result.current.selectedIds.has('id-1')).toBe(false);
    });

    it('should select all', () => {
      const { result } = renderHook(() => useCurationStore());
      const allIds = ['id-1', 'id-2', 'id-3', 'id-4', 'id-5'];
      
      act(() => {
        result.current.selectAll(allIds);
      });

      expect(result.current.selectedIds.size).toBe(5);
      allIds.forEach(id => {
        expect(result.current.selectedIds.has(id)).toBe(true);
      });
    });

    it('should clear selection', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.toggleSelection('id-1');
        result.current.toggleSelection('id-2');
        result.current.clearSelection();
      });

      expect(result.current.selectedIds.size).toBe(0);
    });
  });

  describe('Filter Management', () => {
    it('should set status filter', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.setStatusFilter('pending');
      });

      expect(result.current.statusFilter).toBe('pending');
    });

    it('should accept all valid status filters', () => {
      const { result } = renderHook(() => useCurationStore());
      const validStatuses: (CurationStatus | 'all')[] = [
        'all',
        'pending',
        'assigned',
        'approved',
        'rejected',
        'flagged',
      ];

      validStatuses.forEach((status) => {
        act(() => {
          result.current.setStatusFilter(status);
        });
        expect(result.current.statusFilter).toBe(status);
      });
    });

    it('should set quality threshold', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.setQualityThreshold(0.7);
      });

      expect(result.current.qualityThreshold).toBe(0.7);
    });

    it('should set quality range', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.setQualityRange(0.3, 0.8);
      });

      expect(result.current.minQuality).toBe(0.3);
      expect(result.current.maxQuality).toBe(0.8);
    });
  });

  describe('Pagination', () => {
    it('should set current page', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.setCurrentPage(3);
      });

      expect(result.current.currentPage).toBe(3);
    });
  });

  describe('Tab Management', () => {
    it('should set current tab', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.setCurrentTab('low-quality');
      });

      expect(result.current.currentTab).toBe('low-quality');
    });

    it('should accept all valid tabs', () => {
      const { result } = renderHook(() => useCurationStore());
      const validTabs = ['queue', 'low-quality', 'analytics'];

      validTabs.forEach((tab) => {
        act(() => {
          result.current.setCurrentTab(tab as any);
        });
        expect(result.current.currentTab).toBe(tab);
      });
    });
  });

  describe('Batch Operations', () => {
    it('should track multiple selections', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.toggleSelection('id-1');
        result.current.toggleSelection('id-2');
        result.current.toggleSelection('id-3');
      });

      expect(result.current.selectedIds.size).toBe(3);
    });

    it('should clear selection after batch operation', () => {
      const { result } = renderHook(() => useCurationStore());
      
      act(() => {
        result.current.selectAll(['id-1', 'id-2', 'id-3']);
        result.current.clearSelection();
      });

      expect(result.current.selectedIds.size).toBe(0);
    });
  });
});
