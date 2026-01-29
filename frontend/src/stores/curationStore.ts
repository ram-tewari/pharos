/**
 * Curation Store
 * 
 * Phase 9: Content Curation Dashboard
 * State management for curation UI
 */

import { create } from 'zustand';
import type { CurationStatus } from '@/types/curation';

export type CurationTab = 'queue' | 'low-quality' | 'analytics';

interface CurationStore {
  // Filters
  statusFilter: CurationStatus | 'all';
  minQuality: number;
  maxQuality: number;
  assignedToFilter: string | null;
  
  // Selection
  selectedIds: Set<string>;
  
  // UI State
  currentTab: CurationTab;
  qualityThreshold: number;
  
  // Pagination
  currentPage: number;
  pageSize: number;
  
  // Actions
  setStatusFilter: (status: CurationStatus | 'all') => void;
  setQualityRange: (min: number, max: number) => void;
  setAssignedToFilter: (curator: string | null) => void;
  toggleSelection: (id: string) => void;
  selectAll: (ids: string[]) => void;
  clearSelection: () => void;
  setCurrentTab: (tab: CurationTab) => void;
  setQualityThreshold: (threshold: number) => void;
  setCurrentPage: (page: number) => void;
}

export const useCurationStore = create<CurationStore>((set) => ({
  // Initial state
  statusFilter: 'all',
  minQuality: 0,
  maxQuality: 1,
  assignedToFilter: null,
  selectedIds: new Set(),
  currentTab: 'queue',
  qualityThreshold: 0.5,
  currentPage: 0,
  pageSize: 25,
  
  // Actions
  setStatusFilter: (status) => set({ statusFilter: status }),
  setQualityRange: (min, max) => set({ minQuality: min, maxQuality: max }),
  setAssignedToFilter: (curator) => set({ assignedToFilter: curator }),
  
  toggleSelection: (id) => set((state) => {
    const newSet = new Set(state.selectedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    return { selectedIds: newSet };
  }),
  
  selectAll: (ids) => set({ selectedIds: new Set(ids) }),
  clearSelection: () => set({ selectedIds: new Set() }),
  setCurrentTab: (tab) => set({ currentTab: tab, selectedIds: new Set() }),
  setQualityThreshold: (threshold) => set({ qualityThreshold: threshold }),
  setCurrentPage: (page) => set({ currentPage: page }),
}));
