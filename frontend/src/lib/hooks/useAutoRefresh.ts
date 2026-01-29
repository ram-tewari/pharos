/**
 * Auto-Refresh Hook
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Manages auto-refresh behavior for monitoring dashboard
 */

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export function useAutoRefresh(enabled: boolean, interval = 30000) {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    if (!enabled) return;
    
    const timer = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
      queryClient.invalidateQueries({ queryKey: ['ingestion'] });
    }, interval);
    
    return () => clearInterval(timer);
  }, [enabled, interval, queryClient]);
}
