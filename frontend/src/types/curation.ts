/**
 * Curation Types
 * 
 * Phase 9: Content Curation Dashboard
 * TypeScript types for curation API responses
 */

export type CurationStatus = 'pending' | 'assigned' | 'approved' | 'rejected' | 'flagged';

export interface ReviewQueueItem {
  resource_id: string;
  title: string;
  resource_type: string;
  quality_score: number;
  status: CurationStatus;
  assigned_to?: string;
  last_updated: string;
  created_at: string;
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface QualityDimensions {
  completeness: number;
  accuracy: number;
  clarity: number;
  relevance: number;
  freshness: number;
}

export interface QualityAnalysisResponse {
  resource_id: string;
  overall_score: number;
  dimensions: QualityDimensions;
  is_outlier: boolean;
  suggestions: string[];
  trend?: Array<{ date: string; score: number }>;
}

export interface BatchUpdateResult {
  updated_count: number;
  failed_count: number;
  errors: Array<{
    resource_id: string;
    error: string;
  }>;
}

export interface ReviewQueueFilters {
  status?: CurationStatus | 'all';
  assigned_to?: string;
  min_quality?: number;
  max_quality?: number;
  limit?: number;
  offset?: number;
}

export interface BatchReviewRequest {
  resource_ids: string[];
  action: 'approve' | 'reject' | 'flag';
  reviewer_id: string;
  notes?: string;
}

export interface BatchTagRequest {
  resource_ids: string[];
  tags: string[];
}

export interface BatchAssignRequest {
  resource_ids: string[];
  curator_id: string;
}
