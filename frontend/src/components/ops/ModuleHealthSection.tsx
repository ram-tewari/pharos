/**
 * Module Health Section
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Grid of all backend module health statuses
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { StatusBadge } from './StatusBadge';
import { useOpsStore, type ModuleFilter } from '@/stores/opsStore';
import type { HealthCheckResponse } from '@/types/monitoring';

interface ModuleHealthSectionProps {
  health?: HealthCheckResponse;
}

export function ModuleHealthSection({ health }: ModuleHealthSectionProps) {
  const { moduleFilter, setModuleFilter } = useOpsStore();
  
  if (!health) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-muted-foreground">Loading module health...</p>
        </CardContent>
      </Card>
    );
  }
  
  const modules = Object.entries(health?.modules || {}).filter(([_, module]) => {
    if (moduleFilter === 'all') return true;
    return module.status === moduleFilter;
  });
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Module Health ({modules.length})</CardTitle>
          <Select value={moduleFilter} onValueChange={(v) => setModuleFilter(v as ModuleFilter)}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Modules</SelectItem>
              <SelectItem value="healthy">Healthy</SelectItem>
              <SelectItem value="degraded">Degraded</SelectItem>
              <SelectItem value="down">Down</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {modules.map(([name, module]) => (
            <Card key={name}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <p className="font-medium capitalize">{name}</p>
                    <p className="text-xs text-muted-foreground">
                      {module.response_time_ms}ms response
                    </p>
                    {module.error_count > 0 && (
                      <p className="text-xs text-red-500">
                        {module.error_count} errors
                      </p>
                    )}
                  </div>
                  <StatusBadge status={module.status} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
