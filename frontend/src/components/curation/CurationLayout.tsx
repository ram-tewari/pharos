/**
 * Curation Layout
 * 
 * Phase 9: Content Curation Dashboard
 * Main layout wrapper
 */

import { ReactNode } from 'react';

interface CurationLayoutProps {
  children: ReactNode;
}

export function CurationLayout({ children }: CurationLayoutProps) {
  return (
    <div className="space-y-6">
      {children}
    </div>
  );
}
