/**
 * Quality Score Badge
 * 
 * Phase 9: Content Curation Dashboard
 * Color-coded quality score indicator
 */

import { Badge } from '@/components/ui/badge';

interface QualityScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export function QualityScoreBadge({ score, size = 'md' }: QualityScoreBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500/10 text-green-500 hover:bg-green-500/20';
    if (score >= 0.6) return 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20';
    if (score >= 0.4) return 'bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20';
    return 'bg-red-500/10 text-red-500 hover:bg-red-500/20';
  };
  
  const sizeClass = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }[size];
  
  return (
    <Badge variant="outline" className={`${getColor(score)} ${sizeClass}`}>
      {score.toFixed(2)}
    </Badge>
  );
}
