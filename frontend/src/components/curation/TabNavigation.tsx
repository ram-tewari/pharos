/**
 * Tab Navigation
 * 
 * Phase 9: Content Curation Dashboard
 * Tab navigation for different views
 */

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useCurationStore, type CurationTab } from '@/stores/curationStore';

export function TabNavigation() {
  const { currentTab, setCurrentTab } = useCurationStore();
  
  return (
    <Tabs value={currentTab} onValueChange={(v) => setCurrentTab(v as CurationTab)}>
      <TabsList>
        <TabsTrigger value="queue">Review Queue</TabsTrigger>
        <TabsTrigger value="low-quality">Low Quality</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
