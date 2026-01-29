/**
 * Page Header
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Header with title, refresh controls, and time range selector
 */

import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RefreshCw } from 'lucide-react';
import { useOpsStore, type TimeRange } from '@/stores/opsStore';
import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

export function PageHeader() {
  const { timeRange, autoRefresh, setTimeRange, toggleAutoRefresh } = useOpsStore();
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    await queryClient.invalidateQueries({ queryKey: ['ingestion'] });
    setTimeout(() => setIsRefreshing(false), 500);
  };
  
  return (
    <div className="flex items-center justify-between pb-6 border-b">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">System Operations</h1>
        <p className="text-sm text-muted-foreground">
          Monitor system health, performance, and infrastructure
        </p>
      </div>
      
      <div className="flex items-center gap-2">
        <Select value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1h">Last Hour</SelectItem>
            <SelectItem value="6h">Last 6 Hours</SelectItem>
            <SelectItem value="24h">Last 24 Hours</SelectItem>
            <SelectItem value="7d">Last 7 Days</SelectItem>
          </SelectContent>
        </Select>
        
        <Button
          variant={autoRefresh ? 'default' : 'outline'}
          size="sm"
          onClick={toggleAutoRefresh}
          className="min-w-[110px]"
        >
          Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
        </Button>
        
        <Button 
          variant="outline" 
          size="icon" 
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </Button>
      </div>
    </div>
  );
}
