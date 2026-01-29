import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePlannerStore } from '../planner';
import type { Plan, Task } from '@/types/planner';

describe('Planner Store', () => {
  beforeEach(() => {
    const { result } = renderHook(() => usePlannerStore());
    act(() => {
      result.current.setCurrentPlan(null);
      result.current.savedPlans = [];
      result.current.setError(null);
    });
  });

  describe('Initial State', () => {
    it('should have null currentPlan initially', () => {
      const { result } = renderHook(() => usePlannerStore());
      expect(result.current.currentPlan).toBeNull();
    });

    it('should have empty savedPlans initially', () => {
      const { result } = renderHook(() => usePlannerStore());
      expect(result.current.savedPlans).toEqual([]);
    });

    it('should not be generating initially', () => {
      const { result } = renderHook(() => usePlannerStore());
      expect(result.current.isGenerating).toBe(false);
    });

    it('should have no error initially', () => {
      const { result } = renderHook(() => usePlannerStore());
      expect(result.current.error).toBeNull();
    });
  });

  describe('Plan Management', () => {
    const mockPlan: Plan = {
      id: 'plan-1',
      name: 'Test Plan',
      description: 'Test Description',
      createdAt: new Date(),
      updatedAt: new Date(),
      tasks: [],
      metadata: {
        totalTasks: 0,
        completedTasks: 0,
        progress: 0,
      },
    };

    it('should set current plan', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setCurrentPlan(mockPlan);
      });

      expect(result.current.currentPlan).toEqual(mockPlan);
    });

    it('should add plan to saved plans', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.addPlan(mockPlan);
      });

      expect(result.current.savedPlans).toHaveLength(1);
      expect(result.current.savedPlans[0]).toEqual(mockPlan);
      expect(result.current.currentPlan).toEqual(mockPlan);
    });

    it('should update plan', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.addPlan(mockPlan);
        result.current.updatePlan('plan-1', { name: 'Updated Plan' });
      });

      expect(result.current.savedPlans[0].name).toBe('Updated Plan');
    });

    it('should delete plan', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.addPlan(mockPlan);
        result.current.deletePlan('plan-1');
      });

      expect(result.current.savedPlans).toHaveLength(0);
      expect(result.current.currentPlan).toBeNull();
    });
  });

  describe('Task Management', () => {
    const mockTask: Task = {
      id: 'task-1',
      planId: 'plan-1',
      title: 'Test Task',
      description: 'Test Description',
      completed: false,
      order: 1,
      links: [],
      details: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const mockPlan: Plan = {
      id: 'plan-1',
      name: 'Test Plan',
      description: 'Test Description',
      createdAt: new Date(),
      updatedAt: new Date(),
      tasks: [mockTask],
      metadata: {
        totalTasks: 1,
        completedTasks: 0,
        progress: 0,
      },
    };

    it('should toggle task completion', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setCurrentPlan(mockPlan);
        result.current.toggleTask('task-1');
      });

      expect(result.current.currentPlan?.tasks[0].completed).toBe(true);
      expect(result.current.currentPlan?.metadata.completedTasks).toBe(1);
      expect(result.current.currentPlan?.metadata.progress).toBe(100);
    });

    it('should add task', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setCurrentPlan(mockPlan);
        result.current.addTask({
          planId: 'plan-1',
          title: 'New Task',
          description: 'New Description',
          completed: false,
          order: 2,
          links: [],
          details: [],
        });
      });

      expect(result.current.currentPlan?.tasks).toHaveLength(2);
      expect(result.current.currentPlan?.metadata.totalTasks).toBe(2);
    });

    it('should remove task', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setCurrentPlan(mockPlan);
        result.current.removeTask('task-1');
      });

      expect(result.current.currentPlan?.tasks).toHaveLength(0);
      expect(result.current.currentPlan?.metadata.totalTasks).toBe(0);
    });
  });

  describe('Loading State', () => {
    it('should set generating state', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setGenerating(true);
      });

      expect(result.current.isGenerating).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should set error', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setError('Test error');
      });

      expect(result.current.error).toBe('Test error');
    });

    it('should clear error', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      act(() => {
        result.current.setError('Test error');
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Progress Calculation', () => {
    it('should calculate progress correctly', () => {
      const { result } = renderHook(() => usePlannerStore());
      
      const plan: Plan = {
        id: 'plan-1',
        name: 'Test Plan',
        description: 'Test',
        createdAt: new Date(),
        updatedAt: new Date(),
        tasks: [
          { id: '1', planId: 'plan-1', title: 'Task 1', description: '', completed: true, order: 1, links: [], details: [], createdAt: new Date(), updatedAt: new Date() },
          { id: '2', planId: 'plan-1', title: 'Task 2', description: '', completed: false, order: 2, links: [], details: [], createdAt: new Date(), updatedAt: new Date() },
          { id: '3', planId: 'plan-1', title: 'Task 3', description: '', completed: true, order: 3, links: [], details: [], createdAt: new Date(), updatedAt: new Date() },
          { id: '4', planId: 'plan-1', title: 'Task 4', description: '', completed: false, order: 4, links: [], details: [], createdAt: new Date(), updatedAt: new Date() },
        ],
        metadata: {
          totalTasks: 4,
          completedTasks: 2,
          progress: 50,
        },
      };

      act(() => {
        result.current.setCurrentPlan(plan);
      });

      expect(result.current.currentPlan?.metadata.progress).toBe(50);
    });
  });
});
