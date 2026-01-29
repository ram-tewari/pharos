import { DocumentCard } from './DocumentCard';
import { Skeleton } from '@/components/loading/Skeleton';
import { FileText, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Resource } from '@/types/library';
import { cn } from '@/lib/utils';

export interface DocumentGridProps {
  documents: Resource[];
  isLoading?: boolean;
  selectedIds?: Set<string>;
  onDocumentClick?: (document: Resource) => void;
  onDocumentSelect?: (documentId: string, selected: boolean) => void;
  onDocumentDelete?: (documentId: string) => void;
  onDocumentAddToCollection?: (documentId: string) => void;
  onUploadClick?: () => void;
  className?: string;
}

function DocumentCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  );
}

export function DocumentGrid({
  documents,
  isLoading = false,
  selectedIds = new Set(),
  onDocumentClick,
  onDocumentSelect,
  onDocumentDelete,
  onDocumentAddToCollection,
  onUploadClick,
  className,
}: DocumentGridProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4', className)}>
        {Array.from({ length: 8 }).map((_, i) => (
          <DocumentCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  // Empty state
  if (documents.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-16', className)}>
        <div className="rounded-full bg-muted p-6 mb-4">
          <FileText className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
        <p className="text-sm text-muted-foreground mb-6 text-center max-w-sm">
          Get started by uploading your first document or importing from a repository
        </p>
        {onUploadClick && (
          <Button onClick={onUploadClick}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        )}
      </div>
    );
  }

  // Grid view
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4', className)}>
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          selected={selectedIds.has(document.id)}
          onClick={() => onDocumentClick?.(document)}
          onSelect={(selected) => onDocumentSelect?.(document.id, selected)}
          onDelete={() => onDocumentDelete?.(document.id)}
          onAddToCollection={() => onDocumentAddToCollection?.(document.id)}
        />
      ))}
    </div>
  );
}
