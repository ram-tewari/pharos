/**
 * Curation Page
 * 
 * Phase 9: Content Curation Dashboard
 * Main curation dashboard with review queue, quality analysis, and analytics
 */

import { createFileRoute } from '@tanstack/react-router';
import { CurationLayout } from '@/components/curation/CurationLayout';
import { CurationHeader } from '@/components/curation/CurationHeader';
import { TabNavigation } from '@/components/curation/TabNavigation';
import { ReviewQueueView } from '@/components/curation/ReviewQueueView';
import { LowQualityView } from '@/components/curation/LowQualityView';
import { QualityAnalyticsDashboard } from '@/components/curation/QualityAnalyticsDashboard';
import { useCurationStore } from '@/stores/curationStore';

const CurationPage = () => {
  const { currentTab } = useCurationStore();
  
  return (
    <CurationLayout>
      <CurationHeader />
      <TabNavigation />
      
      <div className="mt-6">
        {currentTab === 'queue' && <ReviewQueueView />}
        {currentTab === 'low-quality' && <LowQualityView />}
        {currentTab === 'analytics' && <QualityAnalyticsDashboard />}
      </div>
    </CurationLayout>
  );
};

export const Route = createFileRoute('/_auth/curation')({
  component: CurationPage,
});
