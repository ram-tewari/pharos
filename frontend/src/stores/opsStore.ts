/**
 * Ops Store
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * State management for ops dashboard UI controls
 */

import { create } from 'zustand';

export type TimeRange = '1h' | '6h' | '24h' | '7d';
export type ModuleFilter = 'all' | 'healthy' | 'degraded' | 'down';

interface OpsStore {
  // UI State
  timeRange: TimeRange;
  autoRefresh: boolean;
  moduleFilter: ModuleFilter;
  
  // Actions
  setTimeRange: (range: TimeRange) => void;
  toggleAutoRefresh: () => void;
  setModuleFilter: (filter: ModuleFilter) => void;
}

export const useOpsStore = create<OpsStore>((set) => ({
  // Initial state
  timeRange: '24h',
  autoRefresh: true,
  moduleFilter: 'all',
  
  // Actions
  setTimeRange: (range) => set({ timeRange: range }),
  toggleAutoRefresh: () => set((state) => ({ autoRefresh: !state.autoRefresh })),
  setModuleFilter: (filter) => set({ moduleFilter: filter }),
}));
