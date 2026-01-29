/**
 * Annotation Panel Component
 * 
 * Side panel for viewing, creating, editing, and deleting annotations.
 * Uses TanStack Query hooks for data fetching and mutations.
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 6.3 - Update annotation store to use real data
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.9, 4.10
 */

import { useEffect, useState, useMemo } from 'react';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorStore } from '@/stores/editor';
import {
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
} from '@/lib/hooks/useEditorData';
import type { AnnotationCreate, AnnotationUpdate, Annotation } from '@/features/editor/types';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  PlusIcon,
  FileTextIcon,
  SaveIcon,
  XIcon,
  EditIcon,
  TrashIcon,
  SearchIcon,
  AlertCircleIcon,
  Loader2Icon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnnotationPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  resourceId: string;
}

type ViewMode = 'list' | 'create' | 'edit';

const PRESET_COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
];

export function AnnotationPanel({
  open,
  onOpenChange,
  resourceId,
}: AnnotationPanelProps) {
  // ==========================================================================
  // Store State
  // ==========================================================================
  
  const {
    selectedAnnotationId,
    selectAnnotation,
    setIsCreating,
  } = useAnnotationStore();

  const { updateCursorPosition, selection } = useEditorStore();

  // ==========================================================================
  // Data Fetching with TanStack Query
  // ==========================================================================
  
  // Fetch annotations for the current resource
  const {
    data: annotations = [],
    isLoading,
    error: fetchError,
  } = useAnnotations(resourceId, {
    enabled: open && !!resourceId,
  });

  // Mutations for CRUD operations
  const createMutation = useCreateAnnotation();
  const updateMutation = useUpdateAnnotation();
  const deleteMutation = useDeleteAnnotation();

  // ==========================================================================
  // Local State
  // ==========================================================================
  
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [formData, setFormData] = useState({
    note: '',
    tags: '',
    color: PRESET_COLORS[0],
  });
  const [searchQuery, setSearchQuery] = useState('');

  // ==========================================================================
  // Computed Values
  // ==========================================================================
  
  // Find selected annotation from the list
  const selectedAnnotation = useMemo(() => {
    return annotations.find((a) => a.id === selectedAnnotationId) || null;
  }, [annotations, selectedAnnotationId]);

  // ==========================================================================
  // Effects
  // ==========================================================================
  
  // Reset form when switching modes
  useEffect(() => {
    if (viewMode === 'create') {
      setFormData({
        note: '',
        tags: '',
        color: PRESET_COLORS[0],
      });
    } else if (viewMode === 'edit' && selectedAnnotation) {
      setFormData({
        note: selectedAnnotation.note || '',
        tags: selectedAnnotation.tags?.join(', ') || '',
        color: selectedAnnotation.color,
      });
    }
  }, [viewMode, selectedAnnotation]);

  // ==========================================================================
  // Event Handlers
  // ==========================================================================
  
  // Handle annotation click - scroll to annotation in editor
  const handleAnnotationClick = (annotationId: string) => {
    selectAnnotation(annotationId);
    
    // Find the annotation to get its position
    const annotation = annotations.find((a) => a.id === annotationId);
    if (annotation) {
      // Calculate line number from start_offset
      // This is a simplified calculation - in reality we'd need the full file content
      // For now, we'll just set a cursor position
      updateCursorPosition({ line: 1, column: annotation.start_offset });
    }
  };

  // Handle create new annotation
  const handleCreateNew = () => {
    setViewMode('create');
  };

  // Handle edit annotation
  const handleEdit = (annotationId: string) => {
    selectAnnotation(annotationId);
    setViewMode('edit');
  };

  // Handle save (create or update)
  const handleSave = async () => {
    try {
      const tags = formData.tags
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0);

      if (viewMode === 'create') {
        // For create, we need selection from editor
        if (!selection) {
          alert('Please select text in the editor first');
          return;
        }

        const annotationData: AnnotationCreate = {
          start_offset: selection.start.column,
          end_offset: selection.end.column,
          highlighted_text: 'Selected text', // TODO: Get actual selected text
          note: formData.note || undefined,
          tags: tags.length > 0 ? tags : undefined,
          color: formData.color,
        };

        await createMutation.mutateAsync({
          resourceId,
          data: annotationData,
        });
      } else if (viewMode === 'edit' && selectedAnnotation) {
        const updateData: AnnotationUpdate = {
          note: formData.note || undefined,
          tags: tags.length > 0 ? tags : undefined,
          color: formData.color,
        };

        await updateMutation.mutateAsync({
          annotationId: selectedAnnotation.id,
          resourceId: selectedAnnotation.resource_id,
          data: updateData,
        });
      }

      // Return to list view
      setViewMode('list');
      selectAnnotation(null);
    } catch (error) {
      console.error('Failed to save annotation:', error);
      // Error is already handled by mutation error state
    }
  };

  // Handle cancel
  const handleCancel = () => {
    setViewMode('list');
    selectAnnotation(null);
  };

  // Handle delete with confirmation
  const handleDelete = async (annotationId: string) => {
    if (!confirm('Are you sure you want to delete this annotation?')) {
      return;
    }

    try {
      const annotation = annotations.find((a) => a.id === annotationId);
      if (!annotation) return;

      await deleteMutation.mutateAsync({
        annotationId,
        resourceId: annotation.resource_id,
      });
      
      selectAnnotation(null);
    } catch (error) {
      console.error('Failed to delete annotation:', error);
      // Error is already handled by mutation error state
    }
  };

  // ==========================================================================
  // Render Helpers
  // ==========================================================================
  
  // Filter annotations based on search query
  const filteredAnnotations = annotations.filter((annotation) => {
    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    
    // Search in highlighted text
    if (annotation.highlighted_text.toLowerCase().includes(query)) {
      return true;
    }
    
    // Search in note
    if (annotation.note?.toLowerCase().includes(query)) {
      return true;
    }
    
    // Search in tags
    if (annotation.tags?.some((tag) => tag.toLowerCase().includes(query))) {
      return true;
    }
    
    return false;
  });

  // Determine if any mutation is in progress
  const isSaving = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  // Get error message from mutations or fetch
  const errorMessage = 
    createMutation.error?.message ||
    updateMutation.error?.message ||
    deleteMutation.error?.message ||
    (fetchError as Error)?.message;

  // Render list view
  const renderListView = () => (
    <>
      {/* Error display */}
      {errorMessage && (
        <Alert variant="destructive">
          <AlertCircleIcon className="h-4 w-4" />
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Create new annotation button */}
      <Button
        onClick={handleCreateNew}
        className="w-full"
        variant="outline"
      >
        <PlusIcon className="mr-2 h-4 w-4" />
        Create New Annotation
      </Button>

      {/* Search input */}
      {annotations.length > 0 && (
        <div className="relative">
          <Input
            placeholder="Search annotations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
          <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        </div>
      )}

      {/* Annotations list */}
      <ScrollArea className="flex-1 h-[calc(100vh-250px)]">
        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
            Loading annotations...
          </div>
        ) : filteredAnnotations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <FileTextIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              {searchQuery ? 'No matching annotations' : 'No annotations yet'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {searchQuery
                ? 'Try a different search term'
                : 'Select text in the editor to create your first annotation'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAnnotations.map((annotation) => (
              <div
                key={annotation.id}
                className={cn(
                  'relative p-3 rounded-lg border transition-colors',
                  'hover:bg-accent hover:border-accent-foreground/20',
                  selectedAnnotationId === annotation.id &&
                    'bg-accent border-accent-foreground/20'
                )}
              >
                {/* Color indicator */}
                <div
                  className="w-1 h-full absolute left-0 top-0 rounded-l-lg"
                  style={{ backgroundColor: annotation.color }}
                />

                {/* Content - clickable */}
                <button
                  onClick={() => handleAnnotationClick(annotation.id)}
                  className="w-full text-left"
                >
                  {/* Highlighted text */}
                  <div className="font-medium text-sm mb-2 pl-3">
                    "{annotation.highlighted_text}"
                  </div>

                  {/* Note */}
                  {annotation.note && (
                    <div className="text-sm text-muted-foreground mb-2 pl-3 line-clamp-2">
                      {annotation.note}
                    </div>
                  )}

                  {/* Tags */}
                  {annotation.tags && annotation.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 pl-3 mb-2">
                      {annotation.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="text-xs text-muted-foreground pl-3">
                    {new Date(annotation.created_at).toLocaleDateString()}
                  </div>
                </button>

                {/* Action buttons */}
                <div className="flex gap-1 mt-2 pl-3">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleEdit(annotation.id)}
                    disabled={isSaving}
                  >
                    <EditIcon className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDelete(annotation.id)}
                    className="text-destructive hover:text-destructive"
                    disabled={isSaving}
                  >
                    {deleteMutation.isPending && deleteMutation.variables?.annotationId === annotation.id ? (
                      <Loader2Icon className="h-3 w-3 animate-spin" />
                    ) : (
                      <TrashIcon className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </>
  );

  // Render form view (create or edit)
  const renderFormView = () => (
    <div className="flex flex-col gap-4">
      {/* Error display */}
      {errorMessage && (
        <Alert variant="destructive">
          <AlertCircleIcon className="h-4 w-4" />
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Note field */}
      <div className="space-y-2">
        <Label htmlFor="note">Note</Label>
        <Textarea
          id="note"
          placeholder="Add your thoughts about this code..."
          value={formData.note}
          onChange={(e) => setFormData({ ...formData, note: e.target.value })}
          rows={4}
          disabled={isSaving}
        />
      </div>

      {/* Tags field */}
      <div className="space-y-2">
        <Label htmlFor="tags">Tags (comma-separated)</Label>
        <Input
          id="tags"
          placeholder="bug, todo, question"
          value={formData.tags}
          onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
          disabled={isSaving}
        />
      </div>

      {/* Color picker */}
      <div className="space-y-2">
        <Label>Color</Label>
        <div className="flex gap-2">
          {PRESET_COLORS.map((color) => (
            <button
              key={color}
              onClick={() => setFormData({ ...formData, color })}
              className={cn(
                'w-8 h-8 rounded-full border-2 transition-all',
                formData.color === color
                  ? 'border-foreground scale-110'
                  : 'border-transparent hover:scale-105'
              )}
              style={{ backgroundColor: color }}
              aria-label={`Select color ${color}`}
              disabled={isSaving}
            />
          ))}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 mt-4">
        <Button onClick={handleSave} className="flex-1" disabled={isSaving}>
          {isSaving ? (
            <>
              <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <SaveIcon className="mr-2 h-4 w-4" />
              Save
            </>
          )}
        </Button>
        <Button onClick={handleCancel} variant="outline" className="flex-1" disabled={isSaving}>
          <XIcon className="mr-2 h-4 w-4" />
          Cancel
        </Button>
      </div>
    </div>
  );

  return (
    <Sheet open={open} onOpenChange={onOpenChange} modal={false}>
      <SheetContent side="right" className="w-full sm:max-w-md" hideOverlay>
        <SheetHeader>
          <SheetTitle>
            {viewMode === 'list'
              ? 'Annotations'
              : viewMode === 'create'
              ? 'Create Annotation'
              : 'Edit Annotation'}
          </SheetTitle>
          <SheetDescription>
            {viewMode === 'list'
              ? 'View and manage your annotations for this file'
              : viewMode === 'create'
              ? 'Add a note and tags to your selected text'
              : 'Update your annotation'}
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-4 mt-4">
          {viewMode === 'list' ? renderListView() : renderFormView()}
        </div>
      </SheetContent>
    </Sheet>
  );
}
