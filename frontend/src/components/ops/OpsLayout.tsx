/**
 * Ops Layout
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Main layout wrapper for ops dashboard
 */

import { ReactNode } from 'react';

interface OpsLayoutProps {
  children: ReactNode;
}

export function OpsLayout({ children }: OpsLayoutProps) {
  return (
    <div className="space-y-6">
      {children}
    </div>
  );
}
