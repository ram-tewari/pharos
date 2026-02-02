/**
 * Hypothesis Discovery Modal Component
 * 
 * Modal for Literature-Based Discovery (LBD) using ABC pattern.
 * Allows users to select entity A and C to discover hidden connections.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 11 View Modes
 * Task: 11.10
 */

import { memo, useState, useEffect } from 'react';
import { Lightbulb, Search, ArrowRight, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { graphAPI } from '@/lib/api/graph';
import type { GraphEntity, Hypothesis } from '@/types/graph';

// ============================================================================
// Types
// ============================================================================

interface HypothesisDiscoveryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onHypothesesDiscovered: (hypotheses: Hypothesis[]) => void;
}

// ============================================================================
// Component
// ============================================================================

export const HypothesisDiscoveryModal = memo<HypothesisDiscoveryModalProps>(({
  open,
  onOpenChange,
  onHypothesesDiscovered,
}) => {
  const [entities, setEntities] = useState<GraphEntity[]>([]);
  const [entityA, setEntityA] = useState<string>('');
  const [entityC, setEntityC] = useState<string>('');
  const [isLoadingEntities, setIsLoadingEntities] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [searchA, setSearchA] = useState('');
  const [searchC, setSearchC] = useState('');

  // Load entities when modal opens
  useEffect(() => {
    if (open) {
      loadEntities();
    }
  }, [open]);

  const loadEntities = async () => {
    setIsLoadingEntities(true);
    try {
      const response = await graphAPI.getEntities();
      setEntities(response.entities);
    } catch (error) {
      console.error('Failed to load entities:', error);
      toast.error('Failed to load entities');
    } finally {
      setIsLoadingEntities(false);
    }
  };

  const handleDiscover = async () => {
    if (!entityA || !entityC) {
      toast.error('Please select both entities');
      return;
    }

    if (entityA === entityC) {
      toast.error('Please select different entities');
      return;
    }

    setIsDiscovering(true);
    try {
      const response = await graphAPI.discoverHypotheses(entityA, entityC);
      
      if (response.hypotheses.length === 0) {
        toast.info('No hypotheses found for this combination');
      } else {
        toast.success(`Discovered ${response.hypotheses.length} hypotheses`);
        onHypothesesDiscovered(response.hypotheses);
        onOpenChange(false);
      }
    } catch (error) {
      console.error('Failed to discover hypotheses:', error);
      toast.error('Failed to discover hypotheses');
    } finally {
      setIsDiscovering(false);
    }
  };

  const filteredEntitiesA = entities.filter((e) =>
    e.name.toLowerCase().includes(searchA.toLowerCase())
  );

  const filteredEntitiesC = entities.filter((e) =>
    e.name.toLowerCase().includes(searchC.toLowerCase())
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-primary" />
            Discover Hidden Connections
          </DialogTitle>
          <DialogDescription>
            Use Literature-Based Discovery (LBD) to find hidden connections between entities.
            Select entity A and entity C to discover potential relationships through intermediate entity B.
          </DialogDescription>
        </DialogHeader>

        {isLoadingEntities ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-6 py-4">
            {/* ABC Pattern Visualization */}
            <div className="flex items-center justify-center gap-4 py-4 bg-muted/50 rounded-lg">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-2 mx-auto">
                  <span className="text-lg font-bold text-primary">A</span>
                </div>
                <span className="text-xs text-muted-foreground">Start Entity</span>
              </div>
              
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
              
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center mb-2 mx-auto">
                  <span className="text-lg font-bold text-secondary-foreground">B</span>
                </div>
                <span className="text-xs text-muted-foreground">Hidden Link</span>
              </div>
              
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
              
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-2 mx-auto">
                  <span className="text-lg font-bold text-primary">C</span>
                </div>
                <span className="text-xs text-muted-foreground">End Entity</span>
              </div>
            </div>

            {/* Entity A Selection */}
            <div className="space-y-2">
              <Label htmlFor="entity-a">Entity A (Start)</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="entity-a-search"
                  placeholder="Search entities..."
                  value={searchA}
                  onChange={(e) => setSearchA(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Select value={entityA} onValueChange={setEntityA}>
                <SelectTrigger id="entity-a">
                  <SelectValue placeholder="Select start entity" />
                </SelectTrigger>
                <SelectContent>
                  {filteredEntitiesA.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground text-center">
                      No entities found
                    </div>
                  ) : (
                    filteredEntitiesA.slice(0, 50).map((entity) => (
                      <SelectItem key={entity.id} value={entity.id}>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{entity.name}</span>
                          <span className="text-xs text-muted-foreground">
                            ({entity.type})
                          </span>
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Entity C Selection */}
            <div className="space-y-2">
              <Label htmlFor="entity-c">Entity C (End)</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="entity-c-search"
                  placeholder="Search entities..."
                  value={searchC}
                  onChange={(e) => setSearchC(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Select value={entityC} onValueChange={setEntityC}>
                <SelectTrigger id="entity-c">
                  <SelectValue placeholder="Select end entity" />
                </SelectTrigger>
                <SelectContent>
                  {filteredEntitiesC.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground text-center">
                      No entities found
                    </div>
                  ) : (
                    filteredEntitiesC.slice(0, 50).map((entity) => (
                      <SelectItem key={entity.id} value={entity.id}>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{entity.name}</span>
                          <span className="text-xs text-muted-foreground">
                            ({entity.type})
                          </span>
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDiscovering}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDiscover}
            disabled={!entityA || !entityC || isDiscovering || isLoadingEntities}
          >
            {isDiscovering ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Discovering...
              </>
            ) : (
              <>
                <Lightbulb className="h-4 w-4 mr-2" />
                Discover Hypotheses
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
});

HypothesisDiscoveryModal.displayName = 'HypothesisDiscoveryModal';
