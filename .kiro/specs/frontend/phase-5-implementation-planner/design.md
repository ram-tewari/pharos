# Phase 5: Implementation Planner - Design

## Architecture Overview

The Implementation Planner is a standalone feature within the Neo Alexandria workbench that provides AI-powered task breakdown and progress tracking.

**Design Approach**: Option A - Clean & Fast (⭐⭐ Low Complexity)

### Component Hierarchy

```
PlannerPage
├── PlannerHeader
│   ├── PlanInput (natural language input)
│   └── PlanActions (save, load, delete)
├── PlannerProgress
│   ├── ProgressBar
│   └── ProgressSummary
└── PlannerContent
    ├── TaskList
    │   └── TaskItem (repeating)
    │       ├── TaskCheckbox
    │       ├── TaskTitle
    │       ├── TaskDescription
    │       ├── TaskLinks
    │       └── TaskDetails (expandable)
    └── EmptyState (when no plan)
```

## UI Components

### 1. PlannerPage (Main Container)

**Purpose**: Root container for the planner feature

**Layout**:
```
┌─────────────────────────────────────────────┐
│ PlannerHeader                               │
│ ┌─────────────────────────────────────────┐ │
│ │ "What do you want to build?"            │ │
│ │ [Generate Plan]                         │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ PlannerProgress                             │
│ ████████░░░░░░░░░░░░░░░░░░░░░░ 30%         │
│ 3 of 10 tasks complete                      │
├─────────────────────────────────────────────┤
│ PlannerContent                              │
│ ☑ Task 1: Set up project structure          │
│ ☑ Task 2: Create database schema            │
│ ☑ Task 3: Implement authentication          │
│ ☐ Task 4: Build payment API                 │
│ ☐ Task 5: Add error handling                │
│ ...                                         │
└─────────────────────────────────────────────┘
```

**Props**:
```typescript
interface PlannerPageProps {
  // No props - manages its own state
}
```

**State**:
```typescript
interface PlannerState {
  currentPlan: Plan | null;
  isGenerating: boolean;
  error: string | null;
  savedPlans: Plan[];
}
```

### 2. PlanInput (Natural Language Input)

**Purpose**: Accepts natural language description of what to build

**Component**: shadcn-ui `Textarea` + `Button`

**Props**:
```typescript
interface PlanInputProps {
  onGenerate: (description: string) => Promise<void>;
  isLoading: boolean;
}
```

**Behavior**:
- User types description (e.g., "Plan Payment Service")
- Click "Generate Plan" or press Cmd+Enter
- Shows loading state while generating
- Displays error if generation fails

**Example**:
```tsx
<div className="space-y-4">
  <Textarea
    placeholder="Describe what you want to build..."
    value={description}
    onChange={(e) => setDescription(e.target.value)}
    rows={4}
  />
  <Button onClick={handleGenerate} disabled={isLoading}>
    {isLoading ? "Generating..." : "Generate Plan"}
  </Button>
</div>
```

### 3. ProgressBar (Visual Progress)

**Purpose**: Shows completion percentage visually

**Component**: shadcn-ui `Progress`

**Props**:
```typescript
interface ProgressBarProps {
  completed: number;
  total: number;
}
```

**Behavior**:
- Calculates percentage: `(completed / total) * 100`
- Updates in real-time as tasks are checked
- Color-coded:
  - 0-33%: Red/destructive
  - 34-66%: Yellow/warning
  - 67-100%: Green/success

**Example**:
```tsx
<Progress 
  value={(completed / total) * 100} 
  className={getProgressColor(completed, total)}
/>
```

### 4. TaskList (Checklist)

**Purpose**: Displays all tasks in a scannable list

**Component**: Custom component using shadcn-ui primitives

**Props**:
```typescript
interface TaskListProps {
  tasks: Task[];
  onTaskToggle: (taskId: string) => void;
  onTaskExpand: (taskId: string) => void;
}
```

**Behavior**:
- Renders tasks in order
- Supports keyboard navigation (arrow keys)
- Supports bulk expand/collapse
- Smooth animations on check/uncheck

### 5. TaskItem (Individual Task)

**Purpose**: Displays a single task with checkbox, title, and expandable details

**Component**: shadcn-ui `Checkbox` + `Accordion`

**Props**:
```typescript
interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onExpand: () => void;
  isExpanded: boolean;
}

interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  links: TaskLink[];
  details: TaskDetail[];
}

interface TaskLink {
  label: string;
  url: string;
  type: 'doc' | 'code' | 'external';
}

interface TaskDetail {
  type: 'text' | 'code' | 'command';
  content: string;
  language?: string; // for code blocks
}
```

**Layout**:
```
┌─────────────────────────────────────────────┐
│ ☐ Task 4: Build payment API                 │
│   Implement Stripe integration with webhooks│
│   📄 Architecture Doc  💻 Sample Code       │
│   [▼ Show Details]                          │
│                                             │
│   Details (when expanded):                  │
│   1. Install Stripe SDK                     │
│      $ npm install stripe                   │
│   2. Create payment endpoint                │
│      ```typescript                          │
│      app.post('/api/payment', ...)          │
│      ```                                    │
│   3. Set up webhook handler                 │
│      ...                                    │
└─────────────────────────────────────────────┘
```

**Example**:
```tsx
<Accordion type="single" collapsible>
  <AccordionItem value={task.id}>
    <div className="flex items-start gap-3">
      <Checkbox 
        checked={task.completed}
        onCheckedChange={onToggle}
      />
      <div className="flex-1">
        <AccordionTrigger>
          <h3 className={task.completed ? "line-through" : ""}>
            {task.title}
          </h3>
        </AccordionTrigger>
        <p className="text-sm text-muted-foreground">
          {task.description}
        </p>
        <div className="flex gap-2 mt-2">
          {task.links.map(link => (
            <a href={link.url} target="_blank">
              {getLinkIcon(link.type)} {link.label}
            </a>
          ))}
        </div>
      </div>
    </div>
    <AccordionContent>
      {task.details.map(detail => (
        <TaskDetailBlock detail={detail} />
      ))}
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

## Data Models

### Plan

```typescript
interface Plan {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  tasks: Task[];
  metadata: {
    totalTasks: number;
    completedTasks: number;
    progress: number; // 0-100
  };
}
```

### Task

```typescript
interface Task {
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
```

### TaskLink

```typescript
interface TaskLink {
  id: string;
  taskId: string;
  label: string;
  url: string;
  type: 'doc' | 'code' | 'external';
}
```

### TaskDetail

```typescript
interface TaskDetail {
  id: string;
  taskId: string;
  type: 'text' | 'code' | 'command';
  content: string;
  language?: string; // for code blocks (typescript, bash, etc.)
  order: number;
}
```

## State Management

### Zustand Store

```typescript
interface PlannerStore {
  // State
  currentPlan: Plan | null;
  savedPlans: Plan[];
  isGenerating: boolean;
  error: string | null;
  
  // Actions
  generatePlan: (description: string) => Promise<void>;
  loadPlan: (planId: string) => void;
  savePlan: (plan: Plan) => Promise<void>;
  deletePlan: (planId: string) => Promise<void>;
  toggleTask: (taskId: string) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => Promise<void>;
  clearError: () => void;
}
```

### Local Storage

Plans are persisted to localStorage for offline access:

```typescript
const STORAGE_KEY = 'neo-alexandria-plans';

// Save to localStorage
localStorage.setItem(STORAGE_KEY, JSON.stringify(plans));

// Load from localStorage
const plans = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
```

## API Integration

### Generate Plan

```typescript
async function generatePlan(description: string): Promise<Plan> {
  const response = await axios.post('/api/planning/generate', {
    description,
    context: {
      // Optional: Include codebase context
      repository: currentRepository,
      existingArchitecture: architectureDocs,
    }
  });
  
  return response.data;
}
```

**Request**:
```json
{
  "description": "Build a payment service with Stripe integration",
  "context": {
    "repository": "my-app",
    "existingArchitecture": ["docs/architecture.md"]
  }
}
```

**Response**:
```json
{
  "id": "plan-123",
  "name": "Payment Service Implementation",
  "description": "Build a payment service with Stripe integration",
  "tasks": [
    {
      "id": "task-1",
      "title": "Set up Stripe SDK",
      "description": "Install and configure Stripe SDK",
      "completed": false,
      "order": 1,
      "links": [
        {
          "label": "Stripe Docs",
          "url": "https://stripe.com/docs",
          "type": "external"
        }
      ],
      "details": [
        {
          "type": "command",
          "content": "npm install stripe",
          "order": 1
        },
        {
          "type": "code",
          "content": "import Stripe from 'stripe';\nconst stripe = new Stripe(process.env.STRIPE_KEY);",
          "language": "typescript",
          "order": 2
        }
      ]
    }
  ],
  "metadata": {
    "totalTasks": 10,
    "completedTasks": 0,
    "progress": 0
  }
}
```

### Update Task Status

```typescript
async function updateTaskStatus(taskId: string, completed: boolean): Promise<void> {
  await axios.put(`/api/planning/tasks/${taskId}`, {
    completed
  });
}
```

## Routing

### Route Definition

```typescript
// routes/planner.tsx
import { createFileRoute } from '@tanstack/react-router';
import { PlannerPage } from '@/components/features/planner/PlannerPage';

export const Route = createFileRoute('/planner')({
  component: PlannerPage,
});
```

### Navigation

Users access the planner via:
- Sidebar navigation: "Planner" menu item
- Command palette: "Open Planner" (Cmd+K → "planner")
- Direct URL: `/planner`

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+Enter` | Generate plan (when input focused) |
| `Space` | Toggle task (when task focused) |
| `↑/↓` | Navigate tasks |
| `Enter` | Expand/collapse task details |
| `Cmd+S` | Save plan |
| `Cmd+N` | New plan |

## Accessibility

- All interactive elements are keyboard-accessible
- Checkboxes have proper ARIA labels
- Progress bar has `role="progressbar"` and `aria-valuenow`
- Task expansion uses `aria-expanded` attribute
- Focus indicators are visible
- Color is not the only indicator of progress (text labels included)

## Error Handling

### Generation Errors

```typescript
try {
  const plan = await generatePlan(description);
  setPlan(plan);
} catch (error) {
  if (error.response?.status === 429) {
    setError('Rate limit exceeded. Please try again later.');
  } else if (error.response?.status === 500) {
    setError('Server error. Please try again.');
  } else {
    setError('Failed to generate plan. Please check your input.');
  }
}
```

### Offline Handling

```typescript
if (!navigator.onLine) {
  // Load from localStorage only
  const cachedPlans = loadFromLocalStorage();
  setPlans(cachedPlans);
  showWarning('You are offline. Changes will sync when online.');
}
```

## Performance Optimizations

1. **Virtualization**: Use `react-window` for large task lists (>50 tasks)
2. **Debouncing**: Debounce auto-save by 500ms
3. **Lazy Loading**: Load task details only when expanded
4. **Memoization**: Memoize task components with `React.memo`
5. **Code Splitting**: Lazy load planner page with `React.lazy`

## Testing Strategy

### Unit Tests

```typescript
describe('TaskItem', () => {
  it('renders task title and description', () => {
    render(<TaskItem task={mockTask} />);
    expect(screen.getByText(mockTask.title)).toBeInTheDocument();
  });
  
  it('calls onToggle when checkbox is clicked', () => {
    const onToggle = jest.fn();
    render(<TaskItem task={mockTask} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalled();
  });
  
  it('expands details when accordion is clicked', () => {
    render(<TaskItem task={mockTask} />);
    fireEvent.click(screen.getByRole('button', { name: /show details/i }));
    expect(screen.getByText(mockTask.details[0].content)).toBeVisible();
  });
});
```

### Integration Tests

```typescript
describe('PlannerPage', () => {
  it('generates plan from description', async () => {
    render(<PlannerPage />);
    
    const input = screen.getByPlaceholderText(/describe what you want to build/i);
    fireEvent.change(input, { target: { value: 'Build payment service' } });
    
    const button = screen.getByRole('button', { name: /generate plan/i });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/payment service implementation/i)).toBeInTheDocument();
    });
  });
  
  it('persists task completion to localStorage', async () => {
    render(<PlannerPage />);
    
    // Load plan with tasks
    const checkbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(checkbox);
    
    // Check localStorage
    const stored = JSON.parse(localStorage.getItem('neo-alexandria-plans'));
    expect(stored[0].tasks[0].completed).toBe(true);
  });
});
```

## Future Enhancements

1. **AI Task Suggestions**: Analyze codebase to suggest additional tasks
2. **Time Estimates**: Add estimated time for each task
3. **Dependencies**: Mark tasks that depend on others
4. **Templates**: Save plans as reusable templates
5. **Collaboration**: Share plans with team members
6. **GitHub Integration**: Create GitHub issues from tasks
7. **Progress Reports**: Generate weekly progress summaries
8. **Smart Reordering**: AI-powered task prioritization

## Design Mockups

### Empty State
```
┌─────────────────────────────────────────────┐
│                                             │
│              📋                             │
│                                             │
│     No implementation plan yet              │
│                                             │
│  Describe what you want to build and        │
│  I'll break it down into actionable steps   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ What do you want to build?          │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│         [Generate Plan]                     │
│                                             │
└─────────────────────────────────────────────┘
```

### Active Plan
```
┌─────────────────────────────────────────────┐
│ Payment Service Implementation              │
│ ████████████░░░░░░░░░░░░░░░░░░ 40%         │
│ 4 of 10 tasks complete                      │
├─────────────────────────────────────────────┤
│ ☑ 1. Set up Stripe SDK                      │
│     Install and configure Stripe            │
│     📄 Stripe Docs                          │
├─────────────────────────────────────────────┤
│ ☑ 2. Create payment endpoint                │
│     Implement POST /api/payment             │
│     💻 Sample Code                          │
├─────────────────────────────────────────────┤
│ ☑ 3. Add webhook handler                    │
│     Handle Stripe webhook events            │
│     📄 Webhook Guide                        │
├─────────────────────────────────────────────┤
│ ☑ 4. Implement error handling               │
│     Add try-catch and error responses       │
│     💻 Error Handling Pattern               │
├─────────────────────────────────────────────┤
│ ☐ 5. Add payment validation                 │
│     Validate payment amounts and currency   │
│     📄 Validation Guide                     │
│     [▼ Show Details]                        │
├─────────────────────────────────────────────┤
│ ☐ 6. Write unit tests                       │
│ ☐ 7. Add integration tests                  │
│ ☐ 8. Update API documentation               │
│ ☐ 9. Deploy to staging                      │
│ ☐ 10. Monitor production metrics            │
└─────────────────────────────────────────────┘
```

### Expanded Task
```
┌─────────────────────────────────────────────┐
│ ☐ 5. Add payment validation                 │
│     Validate payment amounts and currency   │
│     📄 Validation Guide  💻 Sample Code     │
│     [▲ Hide Details]                        │
│                                             │
│     Implementation Steps:                   │
│                                             │
│     1. Install validation library           │
│        $ npm install zod                    │
│                                             │
│     2. Create validation schema             │
│        ```typescript                        │
│        const PaymentSchema = z.object({     │
│          amount: z.number().positive(),     │
│          currency: z.enum(['USD', 'EUR'])   │
│        });                                  │
│        ```                                  │
│                                             │
│     3. Apply validation in endpoint         │
│        ```typescript                        │
│        app.post('/api/payment', (req) => {  │
│          const data = PaymentSchema.parse(  │
│            req.body                         │
│          );                                 │
│          // Process payment...              │
│        });                                  │
│        ```                                  │
│                                             │
│     4. Add error handling for validation    │
│        Return 400 Bad Request with details  │
│                                             │
└─────────────────────────────────────────────┘
```
