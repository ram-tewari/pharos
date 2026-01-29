/**
 * Curation API Client
 * 
 * Phase 9: Content Curation Dashboard
 * API endpoints for content curation operations
 */

import { apiClient } from '@/core/api/client';
import type {
  ReviewQueueResponse,
  ReviewQueueFilters,
  QualityAnalysisResponse,
  BatchUpdateResult,
  BatchReviewRequest,
  BatchTagRequest,
  BatchAssignRequest,
} from '@/types/curation';

const CURATION_BASE = '/curation';

export const curationApi = {
  // Review Queue
  getReviewQueue: (filters: ReviewQueueFilters) =>
    apiClient.get<ReviewQueueResponse>(`${CURATION_BASE}/queue`, { params: filters }),
  
  getLowQuality: (threshold: number, limit: number, offset: number) =>
    apiClient.get<ReviewQueueResponse>(`${CURATION_BASE}/low-quality`, {
      params: { threshold, limit, offset },
    }),
  
  // Quality Analysis
  getQualityAnalysis: (resourceId: string) =>
    apiClient.get<QualityAnalysisResponse>(`${CURATION_BASE}/quality-analysis/${resourceId}`),
  
  bulkQualityCheck: (resourceIds: string[]) =>
    apiClient.post<BatchUpdateResult>(`${CURATION_BASE}/bulk-quality-check`, {
      resource_ids: resourceIds,
    }),
  
  // Batch Operations
  batchReview: (data: BatchReviewRequest) =>
    apiClient.post<BatchUpdateResult>(`${CURATION_BASE}/batch/review`, data),
  
  batchTag: (data: BatchTagRequest) =>
    apiClient.post<BatchUpdateResult>(`${CURATION_BASE}/batch/tag`, data),
  
  batchAssign: (data: BatchAssignRequest) =>
    apiClient.post<BatchUpdateResult>(`${CURATION_BASE}/batch/assign`, data),
};
