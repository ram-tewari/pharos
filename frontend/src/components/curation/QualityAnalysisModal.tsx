/**
 * Quality Analysis Modal
 * 
 * Phase 9: Content Curation Dashboard
 * Detailed quality analysis view with dimension scores
 */

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { QualityScoreBadge } from './QualityScoreBadge';
import { useQualityAnalysis } from '@/lib/hooks/useCuration';
import { AlertCircle, Check, X, Flag } from 'lucide-react';

interface QualityAnalysisModalProps {
  resourceId: string | null;
  open: boolean;
  onClose: () => void;
  onAction?: (action: 'approve' | 'reject' | 'flag') => void;
}

export function QualityAnalysisModal({
  resourceId,
  open,
  onClose,
  onAction,
}: QualityAnalysisModalProps) {
  const { data, isLoading } = useQualityAnalysis(resourceId || '');
  
  if (!resourceId) return null;
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Quality Analysis</DialogTitle>
          <DialogDescription>
            Detailed quality assessment and improvement suggestions
          </DialogDescription>
        </DialogHeader>
        
        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">
            Loading quality analysis...
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium">Overall Quality Score</h3>
                <p className="text-3xl font-bold mt-1">
                  {data.overall_score.toFixed(2)}
                </p>
              </div>
              <QualityScoreBadge score={data.overall_score} size="lg" />
            </div>
            
            {data.is_outlier && (
              <div className="flex items-center gap-2 rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-3 text-sm text-yellow-600">
                <AlertCircle className="h-4 w-4" />
                <span>This resource is flagged as a quality outlier</span>
              </div>
            )}
            
            {/* Dimension Scores */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium">Quality Dimensions</h3>
              
              {Object.entries(data.dimensions).map(([dimension, score]) => (
                <div key={dimension} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">{dimension}</span>
                    <span className="font-medium">{(score * 100).toFixed(0)}%</span>
                  </div>
                  <Progress value={score * 100} />
                </div>
              ))}
            </div>
            
            {/* Suggestions */}
            {data.suggestions && data.suggestions.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium">Improvement Suggestions</h3>
                <ul className="space-y-2">
                  {data.suggestions.map((suggestion, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex gap-2">
                      <span className="text-primary">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Quick Actions */}
            {onAction && (
              <div className="flex items-center gap-2 pt-4 border-t">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    onAction('approve');
                    onClose();
                  }}
                >
                  <Check className="mr-2 h-4 w-4" />
                  Approve
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    onAction('reject');
                    onClose();
                  }}
                >
                  <X className="mr-2 h-4 w-4" />
                  Reject
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    onAction('flag');
                    onClose();
                  }}
                >
                  <Flag className="mr-2 h-4 w-4" />
                  Flag
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            No quality analysis available
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
