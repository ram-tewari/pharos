/**
 * RepositoryIngestDialog Component
 * 
 * Dialog for ingesting code repositories from GitHub/GitLab/etc.
 * Allows users to enter a repository URL and optional branch name.
 * Shows progress and status of the ingestion job.
 * 
 * Phase: 3 Living Library
 * Requirements: US-3.2 (Repository Ingestion)
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, GitBranch, AlertCircle, CheckCircle2 } from 'lucide-react';
import { libraryApi } from '@/lib/api/library';
import { toast } from 'sonner';

export interface RepositoryIngestDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function RepositoryIngestDialog({
  open,
  onOpenChange,
  onSuccess,
}: RepositoryIngestDialogProps) {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [queuePosition, setQueuePosition] = useState<number | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate URL
      if (!repoUrl.trim()) {
        throw new Error('Repository URL is required');
      }

      // Clean up URL (remove https://, trailing slashes, .git)
      let cleanUrl = repoUrl.trim();
      cleanUrl = cleanUrl.replace(/^https?:\/\//, '');
      cleanUrl = cleanUrl.replace(/\.git$/, '');
      cleanUrl = cleanUrl.replace(/\/$/, '');

      // Call ingestion API
      const result = await libraryApi.ingestRepository(
        cleanUrl,
        branch.trim() || undefined
      );

      setJobId(result.job_id);
      setQueuePosition(result.queue_position);

      toast.success('Repository ingestion started', {
        description: `Job ${result.job_id} queued at position ${result.queue_position}`,
      });

      // Call success callback after a short delay
      setTimeout(() => {
        onSuccess?.();
        handleClose();
      }, 2000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to ingest repository';
      setError(errorMessage);
      toast.error('Ingestion failed', {
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setRepoUrl('');
    setBranch('');
    setError(null);
    setJobId(null);
    setQueuePosition(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Ingest Code Repository</DialogTitle>
          <DialogDescription>
            Enter a repository URL to analyze and index the code. The repository will be
            cloned, parsed, and processed by the edge worker.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {/* Repository URL Input */}
            <div className="space-y-2">
              <Label htmlFor="repo-url">
                Repository URL <span className="text-destructive">*</span>
              </Label>
              <Input
                id="repo-url"
                placeholder="github.com/facebook/react"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                disabled={isSubmitting}
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                Examples: github.com/user/repo, gitlab.com/user/repo
              </p>
            </div>

            {/* Branch Input (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="branch" className="flex items-center gap-2">
                <GitBranch className="h-4 w-4" />
                Branch (optional)
              </Label>
              <Input
                id="branch"
                placeholder="main"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                disabled={isSubmitting}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to use the default branch (main/master)
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Success Alert */}
            {jobId && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertDescription>
                  Job {jobId} queued at position {queuePosition}. Processing will begin shortly.
                </AlertDescription>
              </Alert>
            )}

            {/* Info Alert */}
            <Alert>
              <AlertDescription className="text-xs">
                <strong>Note:</strong> Repository ingestion is processed asynchronously by the edge worker.
                Large repositories may take several minutes to complete. You can monitor progress
                in the Ops dashboard.
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || !!jobId}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : jobId ? (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Queued
                </>
              ) : (
                'Ingest Repository'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
