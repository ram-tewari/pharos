/**
 * Phase 5: Plan Input Component
 */

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Loader2, Sparkles } from 'lucide-react';

interface PlanInputProps {
  onGenerate: (description: string) => Promise<void>;
  isLoading: boolean;
}

export function PlanInput({ onGenerate, isLoading }: PlanInputProps) {
  const [description, setDescription] = useState('');

  const handleSubmit = async () => {
    if (description.trim().length < 10) {
      return;
    }
    await onGenerate(description);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="plan-description" className="text-sm font-medium">
          What do you want to build?
        </label>
        <Textarea
          id="plan-description"
          placeholder="Describe your implementation goal... (e.g., 'Build a payment service with Stripe integration')"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={4}
          className="mt-2"
          disabled={isLoading}
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Press Cmd+Enter to generate • Minimum 10 characters
        </p>
      </div>
      
      <Button
        onClick={handleSubmit}
        disabled={isLoading || description.trim().length < 10}
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Generating Plan...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            Generate Implementation Plan
          </>
        )}
      </Button>
    </div>
  );
}
