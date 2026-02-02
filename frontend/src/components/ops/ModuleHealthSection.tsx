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
  
  const components = Object.entries(health?.components || {}).filter(([_, component]) => {
    if (moduleFilter === 'all') return true;
    return component.status === moduleFilter;
  });
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Module Health ({components.length})</CardTitle>
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
          {components.map(([name, component]) => (
            <Card key={name}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <p className="font-medium capitalize">{name.replace('_', ' ')}</p>
                    <p className="text-xs text-muted-foreground">
                      {component.message}
                    </p>
                    {component.worker_count !== undefined && (
                      <p className="text-xs text-muted-foreground">
                        {component.worker_count} worker(s)
                      </p>
                    )}
                  </div>
                  <StatusBadge status={component.status as HealthStatus} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
