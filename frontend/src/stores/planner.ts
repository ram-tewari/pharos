/**
 * Phase 5: Implementation Planner - Zustand Store
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Plan, Task } from '@/types/planner';

interface PlannerState {
  // State
  currentPlan: Plan | null;
  savedPlans: Plan[];
  isGenerating: boolean;
  error: string | null;
  
  // Actions
  setCurrentPlan: (plan: Plan | null) => void;
  addPlan: (plan: Plan) => void;
  updatePlan: (planId: string, updates: Partial<Plan>) => void;
  deletePlan: (planId: string) => void;
  toggleTask: (taskId: string) => void;
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
  removeTask: (taskId: string) => void;
  setGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

const STORAGE_KEY = 'neo-alexandria-plans';

export const usePlannerStore = create<PlannerState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentPlan: null,
      savedPlans: [],
      isGenerating: false,
      error: null,

      // Actions
      setCurrentPlan: (plan) => set({ currentPlan: plan }),

      addPlan: (plan) => set((state) => ({
        savedPlans: [...state.savedPlans, plan],
        currentPlan: plan,
      })),

      updatePlan: (planId, updates) => set((state) => {
        const updatedPlans = state.savedPlans.map((p) =>
          p.id === planId ? { ...p, ...updates, updatedAt: new Date() } : p
        );
        const updatedCurrent = state.currentPlan?.id === planId
          ? { ...state.currentPlan, ...updates, updatedAt: new Date() }
          : state.currentPlan;

        return {
          savedPlans: updatedPlans,
          currentPlan: updatedCurrent,
        };
      }),

      deletePlan: (planId) => set((state) => ({
        savedPlans: state.savedPlans.filter((p) => p.id !== planId),
        currentPlan: state.currentPlan?.id === planId ? null : state.currentPlan,
      })),

      toggleTask: (taskId) => set((state) => {
        if (!state.currentPlan) return state;

        const updatedTasks = state.currentPlan.tasks.map((task) =>
          task.id === taskId
            ? { ...task, completed: !task.completed, updatedAt: new Date() }
            : task
        );

        const completedCount = updatedTasks.filter((t) => t.completed).length;
        const progress = (completedCount / updatedTasks.length) * 100;

        const updatedPlan: Plan = {
          ...state.currentPlan,
          tasks: updatedTasks,
          metadata: {
            ...state.currentPlan.metadata,
            completedTasks: completedCount,
            progress,
          },
          updatedAt: new Date(),
        };

        // Update in savedPlans too
        const updatedSavedPlans = state.savedPlans.map((p) =>
          p.id === updatedPlan.id ? updatedPlan : p
        );

        return {
          currentPlan: updatedPlan,
          savedPlans: updatedSavedPlans,
        };
      }),

      addTask: (taskData) => set((state) => {
        if (!state.currentPlan) return state;

        const newTask: Task = {
          ...taskData,
          id: `task-${Date.now()}`,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const updatedTasks = [...state.currentPlan.tasks, newTask];
        const completedCount = updatedTasks.filter((t) => t.completed).length;

        const updatedPlan: Plan = {
          ...state.currentPlan,
          tasks: updatedTasks,
          metadata: {
            totalTasks: updatedTasks.length,
            completedTasks: completedCount,
            progress: (completedCount / updatedTasks.length) * 100,
          },
          updatedAt: new Date(),
        };

        const updatedSavedPlans = state.savedPlans.map((p) =>
          p.id === updatedPlan.id ? updatedPlan : p
        );

        return {
          currentPlan: updatedPlan,
          savedPlans: updatedSavedPlans,
        };
      }),

      removeTask: (taskId) => set((state) => {
        if (!state.currentPlan) return state;

        const updatedTasks = state.currentPlan.tasks.filter((t) => t.id !== taskId);
        const completedCount = updatedTasks.filter((t) => t.completed).length;

        const updatedPlan: Plan = {
          ...state.currentPlan,
          tasks: updatedTasks,
          metadata: {
            totalTasks: updatedTasks.length,
            completedTasks: completedCount,
            progress: updatedTasks.length > 0 ? (completedCount / updatedTasks.length) * 100 : 0,
          },
          updatedAt: new Date(),
        };

        const updatedSavedPlans = state.savedPlans.map((p) =>
          p.id === updatedPlan.id ? updatedPlan : p
        );

        return {
          currentPlan: updatedPlan,
          savedPlans: updatedSavedPlans,
        };
      }),

      setGenerating: (isGenerating) => set({ isGenerating }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: STORAGE_KEY,
      // Only persist plans, not loading/error states
      partialize: (state) => ({
        currentPlan: state.currentPlan,
        savedPlans: state.savedPlans,
      }),
    }
  )
);
