/**
 * Batch Confirm Dialog
 * 
 * Phase 9: Content Curation Dashboard
 * Confirmation dialog for batch operations
 */

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useState } from 'react';
import { useCurationStore } from '@/stores/curationStore';
import { useBatchReview, useBatchTag, useBatchAssign, useBulkQualityCheck } from '@/lib/hooks/useCuration';
import { useToast } from '@/hooks/use-toast';
import type { BatchAction } from './BatchActionsDropdown';

interface BatchConfirmDialogProps {
  open: boolean;
  action: BatchAction;
  count: number;
  onClose: () => void;
}

export function BatchConfirmDialog({ open, action, count, onClose }: BatchConfirmDialogProps) {
  const { selectedIds, clearSelection } = useCurationStore();
  const { toast } = useToast();
  const [notes, setNotes] = useState('');
  const [tags, setTags] = useState('');
  const [curatorId, setCuratorId] = useState('');
  
  const batchReview = useBatchReview();
  const batchTag = useBatchTag();
  const batchAssign = useBatchAssign();
  const bulkQualityCheck = useBulkQualityCheck();
  
  const handleConfirm = async () => {
    const resourceIds = Array.from(selectedIds);
    
    try {
      let result;
      
      switch (action) {
        case 'approve':
        case 'reject':
        case 'flag':
          result = await batchReview.mutateAsync({
            resource_ids: resourceIds,
            action,
            reviewer_id: 'current-user', // TODO: Get from auth context
            notes: notes || undefined,
          });
          break;
        
        case 'tag':
          result = await batchTag.mutateAsync({
            resource_ids: resourceIds,
            tags: tags.split(',').map((t) => t.trim()).filter(Boolean),
          });
          break;
        
        case 'assign':
          result = await batchAssign.mutateAsync({
            resource_ids: resourceIds,
            curator_id: curatorId,
          });
          break;
        
        case 'recalculate':
          result = await bulkQualityCheck.mutateAsync(resourceIds);
          break;
      }
      
      if (result) {
        toast({
          title: 'Success',
          description: `${result.updated_count} resources updated successfully`,
        });
        
        if (result.failed_count > 0) {
          toast({
            title: 'Partial Failure',
            description: `${result.failed_count} resources failed to update`,
            variant: 'destructive',
          });
        }
      }
      
      clearSelection();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to perform batch operation',
        variant: 'destructive',
      });
    }
  };
  
  const getTitle = () => {
    switch (action) {
      case 'approve': return `Approve ${count} resources`;
      case 'reject': return `Reject ${count} resources`;
      case 'flag': return `Flag ${count} resources`;
      case 'tag': return `Add tags to ${count} resources`;
      case 'assign': return `Assign ${count} resources`;
      case 'recalculate': return `Recalculate quality for ${count} resources`;
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{getTitle()}</DialogTitle>
          <DialogDescription>
            This action will affect {count} selected resource{count !== 1 ? 's' : ''}.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {(action === 'approve' || action === 'reject' || action === 'flag') && (
            <div>
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add review notes..."
              />
            </div>
          )}
          
          {action === 'tag' && (
            <div>
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="reviewed, high-quality, featured"
              />
            </div>
          )}
          
          {action === 'assign' && (
            <div>
              <Label htmlFor="curator">Curator ID</Label>
              <Input
                id="curator"
                value={curatorId}
                onChange={(e) => setCuratorId(e.target.value)}
                placeholder="curator-123"
              />
            </div>
          )}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleConfirm}>
            Confirm
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
