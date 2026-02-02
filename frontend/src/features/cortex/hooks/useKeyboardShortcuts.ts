/**
 * Keyboard Shortcuts Hook
 * 
 * Custom hook for managing keyboard shortcuts in the graph.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 19 Accessibility
 * 
 * Properties:
 * - Property 30: Keyboard Shortcut Handling
 * - Property 38: Keyboard Navigation
 */

import { useEffect } from 'react';

// ============================================================================
// Types
// ============================================================================

interface KeyboardShortcutsConfig {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onClearSelection: () => void;
  onToggleFilters?: () => void;
  onToggleFocusMode?: () => void;
}

// ============================================================================
// Hook
// ============================================================================

/**
 * Property 30: Keyboard Shortcut Handling
 * Property 38: Keyboard Navigation
 */
export function useKeyboardShortcuts(config: KeyboardShortcutsConfig) {
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      // Zoom shortcuts
      if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        config.onZoomIn();
      } else if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        config.onZoomOut();
      } else if (e.key === '0') {
        e.preventDefault();
        config.onResetZoom();
      }
      
      // Clear selection
      else if (e.key === 'Escape') {
        e.preventDefault();
        config.onClearSelection();
      }
      
      // Toggle filters
      else if (e.key === 'f' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        config.onToggleFilters?.();
      }
      
      // Toggle focus mode
      else if (e.key === 'F' && e.shiftKey) {
        e.preventDefault();
        config.onToggleFocusMode?.();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [config]);
}
