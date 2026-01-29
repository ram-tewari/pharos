/**
 * Status Badge
 * 
 * Phase 9: Content Curation Dashboard
 * Curation status indicator
 */

import { Badge } from '@/components/ui/badge';
import type { CurationStatus } from '@/types/curation';

interface StatusBadgeProps {
  status: CurationStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variants = {
    pending: 'bg-gray-500/10 text-gray-500 hover:bg-gray-500/20',
    assigned: 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20',
    approved: 'bg-green-500/10 text-green-500 hover:bg-green-500/20',
    rejected: 'bg-red-500/10 text-red-500 hover:bg-red-500/20',
    flagged: 'bg-orange-500/10 text-orange-500 hover:bg-orange-500/20',
  };
  
  return (
    <Badge variant="outline" className={variants[status]}>
      {status}
    </Badge>
  );
}
