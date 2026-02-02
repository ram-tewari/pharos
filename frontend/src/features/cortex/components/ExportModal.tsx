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
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Graph</DialogTitle>
          <DialogDescription>
            Choose a format to export the current graph view
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Format Selection */}
          <RadioGroup value={format} onValueChange={(v) => setFormat(v as ExportFormat)}>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent cursor-pointer">
                <RadioGroupItem value="png" id="png" />
                <Label htmlFor="png" className="flex items-center gap-3 cursor-pointer flex-1">
                  <FileImage className="w-5 h-5 text-blue-500" />
                  <div>
                    <div className="font-medium">PNG Image</div>
                    <div className="text-sm text-muted-foreground">
                      High-quality raster image (2x resolution)
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent cursor-pointer">
                <RadioGroupItem value="svg" id="svg" />
                <Label htmlFor="svg" className="flex items-center gap-3 cursor-pointer flex-1">
                  <FileCode className="w-5 h-5 text-green-500" />
                  <div>
                    <div className="font-medium">SVG Vector</div>
                    <div className="text-sm text-muted-foreground">
                      Scalable vector graphic
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent cursor-pointer">
                <RadioGroupItem value="json" id="json" />
                <Label htmlFor="json" className="flex items-center gap-3 cursor-pointer flex-1">
                  <FileJson className="w-5 h-5 text-purple-500" />
                  <div>
                    <div className="font-medium">JSON Data</div>
                    <div className="text-sm text-muted-foreground">
                      Raw graph data structure
                    </div>
                  </div>
                </Label>
              </div>
            </div>
          </RadioGroup>

          {/* Progress Bar */}
          {isExporting && (
            <div className="space-y-2">
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-center text-muted-foreground">
                Exporting... {progress}%
              </p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isExporting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting}
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
});

ExportModal.displayName = 'ExportModal';
