/**
 * Phase 5: Task List Component
 */

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { TaskItem } from './TaskItem';
import type { Task } from '@/types/planner';

interface TaskListProps {
  tasks: Task[];
  planId: string;
  onTaskToggle: (taskId: string) => void;
  onTaskRemove: (taskId: string) => void;
  onTaskAdd: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
}

export function TaskList({ tasks, planId, onTaskToggle, onTaskRemove, onTaskAdd }: TaskListProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');

  const handleAddTask = () => {
    if (newTaskTitle.trim()) {
      onTaskAdd({
        planId,
        title: newTaskTitle.trim(),
        description: newTaskDescription.trim(),
        completed: false,
        order: tasks.length + 1,
        links: [],
        details: [],
      });
      setNewTaskTitle('');
      setNewTaskDescription('');
      setIsAdding(false);
    }
  };

  if (tasks.length === 0 && !isAdding) {
    return (
      <div className="space-y-3">
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            No tasks yet. Add your first task to get started.
          </p>
          <Button onClick={() => setIsAdding(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Task
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={() => onTaskToggle(task.id)}
          onRemove={() => onTaskRemove(task.id)}
        />
      ))}

      {isAdding ? (
        <div className="rounded-lg border bg-card p-4 space-y-3">
          <Input
            placeholder="Task title..."
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            autoFocus
          />
          <Textarea
            placeholder="Task description (optional)..."
            value={newTaskDescription}
            onChange={(e) => setNewTaskDescription(e.target.value)}
            rows={2}
          />
          <div className="flex gap-2">
            <Button onClick={handleAddTask} disabled={!newTaskTitle.trim()}>
              Add Task
            </Button>
            <Button variant="outline" onClick={() => {
              setIsAdding(false);
              setNewTaskTitle('');
              setNewTaskDescription('');
            }}>
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <Button variant="outline" onClick={() => setIsAdding(true)} className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          Add Task
        </Button>
      )}
    </div>
  );
}
