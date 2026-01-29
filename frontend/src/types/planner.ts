/**
 * Phase 5: Implementation Planner - Type Definitions
 */

export interface Plan {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  tasks: Task[];
  metadata: PlanMetadata;
}

export interface PlanMetadata {
  totalTasks: number;
  completedTasks: number;
  progress: number; // 0-100
}

export interface Task {
  id: string;
  planId: string;
  title: string;
  description: string;
  completed: boolean;
  order: number;
  links: TaskLink[];
  details: TaskDetail[];
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskLink {
  id: string;
  taskId: string;
  label: string;
  url: string;
  type: 'doc' | 'code' | 'external';
}

export interface TaskDetail {
  id: string;
  taskId: string;
  type: 'text' | 'code' | 'command';
  content: string;
  language?: string; // for code blocks
  order: number;
}

// API Request/Response types
export interface GeneratePlanRequest {
  description: string;
  context?: {
    repository?: string;
    existingArchitecture?: string[];
  };
}

export interface GeneratePlanResponse {
  id: string;
  name: string;
  description: string;
  tasks: Task[];
  metadata: PlanMetadata;
}

export interface UpdateTaskRequest {
  completed: boolean;
}
