/**
 * Export Modal Component
 * 
 * Modal for exporting the graph as PNG, SVG, or JSON.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 23 Export
 * Task: 23.1-23.4
 * 
 * Properties:
 * - Property 34: Export Filename Timestamp
 * - Property 35: Export Progress Indicator
 */

import { memo, useState } from 'react';
import { toPng, toSvg } from 'html-to-image';
import { saveAs } from 'file-saver';
import { Download, FileImage, FileCode, FileJson, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import type { GraphData } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

type ExportFormat = 'png' | 'svg' | 'json';

interface ExportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  graphData: GraphData;
  canvasElementId?: string;
}

// ============================================================================
// Component
// ============================================================================

export const ExportModal = memo<ExportModalProps>(({
  open,
  onOpenChange,
  graphData,
  canvasElementId = 'graph-canvas',
}) => {
  const [format, setFormat] = useState<ExportFormat>('png');
  const [isExporting, setIsExporting] = useState(false);
  const [progress, setProgress] = useState(0);

  // Property 34: Export Filename Timestamp
  const generateFilename = (ext: string): string => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    return `graph-${timestamp}.${ext}`;
  };

  const handleExport = async () => {
    setIsExporting(true);
    setProgress(0);

    try {
      const element = document.querySelector('.react-flow') as HTMLElement;
      if (!element) {
        throw new Error('Graph canvas not found');
      }

      setProgress(25);

      if (format === 'png') {
        // Property 35: Export Progress Indicator
        setProgress(50);
        const dataUrl = await toPng(element, {
          quality: 1.0,
          pixelRatio: 2,
        });
        setProgress(75);
        
        const link = document.createElement('a');
        link.download = generateFilename('png');
        link.href = dataUrl;
        link.click();
        
      } else if (format === 'svg') {
        setProgress(50);
        const dataUrl = await toSvg(element);
        setProgress(75);
        
        const link = document.createElement('a');
        link.download = generateFilename('svg');
        link.href = dataUrl;
        link.click();
        
      } else if (format === 'json') {
        setProgress(50);
        const data = JSON.stringify(graphData, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        setProgress(75);
        
        saveAs(blob, generateFilename('json'));
      }

      setProgress(100);
      toast.success(`Graph exported as ${format.toUpperCase()}`);
      onOpenChange(false);
      
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Failed to export graph');
    } finally {
      setIsExporting(false);
      setProgress(0);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md w-[95vw] max-h-[90vh] overflow-y-auto animate-in fade-in-0 zoom-in-95 duration-200" aria-describedby="export-description">
        <DialogHeader>
          <DialogTitle className="text-base md:text-lg">Export Graph</DialogTitle>
          <DialogDescription id="export-description" className="text-sm">
            Choose a format to export the current graph view
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 md:space-y-6 py-3 md:py-4">
          {/* Format Selection */}
          <RadioGroup 
            value={format} 
            onValueChange={(v) => setFormat(v as ExportFormat)}
            aria-label="Export format selection"
          >
            <div className="space-y-2 md:space-y-3" role="list">
              <div className="flex items-center space-x-2 md:space-x-3 p-2 md:p-3 rounded-lg border hover:bg-accent cursor-pointer min-h-[60px] transition-all duration-200 hover:shadow-md hover:border-primary" role="listitem">
                <RadioGroupItem value="png" id="png" aria-label="PNG Image format" className="min-h-[24px] min-w-[24px]" />
                <Label htmlFor="png" className="flex items-center gap-2 md:gap-3 cursor-pointer flex-1">
                  <FileImage className="w-4 h-4 md:w-5 md:h-5 text-blue-500 shrink-0" aria-hidden="true" />
                  <div>
                    <div className="font-medium text-sm md:text-base">PNG Image</div>
                    <div className="text-xs md:text-sm text-muted-foreground">
                      High-quality raster image (2x resolution)
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 md:space-x-3 p-2 md:p-3 rounded-lg border hover:bg-accent cursor-pointer min-h-[60px] transition-all duration-200 hover:shadow-md hover:border-primary" role="listitem">
                <RadioGroupItem value="svg" id="svg" aria-label="SVG Vector format" className="min-h-[24px] min-w-[24px]" />
                <Label htmlFor="svg" className="flex items-center gap-2 md:gap-3 cursor-pointer flex-1">
                  <FileCode className="w-4 h-4 md:w-5 md:h-5 text-green-500 shrink-0" aria-hidden="true" />
                  <div>
                    <div className="font-medium text-sm md:text-base">SVG Vector</div>
                    <div className="text-xs md:text-sm text-muted-foreground">
                      Scalable vector graphic
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 md:space-x-3 p-2 md:p-3 rounded-lg border hover:bg-accent cursor-pointer min-h-[60px] transition-all duration-200 hover:shadow-md hover:border-primary" role="listitem">
                <RadioGroupItem value="json" id="json" aria-label="JSON Data format" className="min-h-[24px] min-w-[24px]" />
                <Label htmlFor="json" className="flex items-center gap-2 md:gap-3 cursor-pointer flex-1">
                  <FileJson className="w-4 h-4 md:w-5 md:h-5 text-purple-500 shrink-0" aria-hidden="true" />
                  <div>
                    <div className="font-medium text-sm md:text-base">JSON Data</div>
                    <div className="text-xs md:text-sm text-muted-foreground">
                      Raw graph data structure
                    </div>
                  </div>
                </Label>
              </div>
            </div>
          </RadioGroup>

          {/* Progress Bar */}
          {isExporting && (
            <div className="space-y-2 animate-in fade-in duration-200" role="status" aria-live="polite">
              <Progress 
                value={progress} 
                className="w-full h-2 bg-gradient-to-r from-primary/20 to-primary/40"
                aria-label={`Export progress: ${progress} percent`}
              />
              <p className="text-xs md:text-sm text-center text-muted-foreground">
                Exporting... {progress}%
              </p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col-reverse sm:flex-row justify-end gap-2" role="group" aria-label="Export actions">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isExporting}
            aria-label="Cancel export and close dialog"
            className="w-full sm:w-auto min-h-[44px] transition-all duration-200 hover:scale-[1.02] active:scale-95"
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting}
            aria-label={`Export graph as ${format.toUpperCase()}`}
            className="w-full sm:w-auto min-h-[44px] transition-all duration-200 hover:scale-[1.02] hover:shadow-lg active:scale-95"
          >
            <Download className="w-4 h-4 mr-2" aria-hidden="true" />
            Export
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
});

ExportModal.displayName = 'ExportModal';
