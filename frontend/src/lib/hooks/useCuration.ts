/**
 * Curation Hooks
 * 
 * Phase 9: Content Curation Dashboard
 * TanStack Query hooks for curation data
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { curationApi } from '@/lib/api/curation';
import type { ReviewQueueFilters, BatchReviewRequest, BatchTagRequest, BatchAssignRequest } from '@/types/curation';

export function useReviewQueue(filters: ReviewQueueFilters) {
  return useQuery({
    queryKey: ['curation', 'review-queue', filters],
    queryFn: () => curationApi.getReviewQueue(filters),
  });
}

export function useLowQualityResources(threshold: number, limit: number, offset: number) {
  return useQuery({
    queryKey: ['curation', 'low-quality', threshold, limit, offset],
    queryFn: () => curationApi.getLowQuality(threshold, limit, offset),
  });
}

export function useQualityAnalysis(resourceId: string) {
  return useQuery({
    queryKey: ['curation', 'quality-analysis', resourceId],
    queryFn: () => curationApi.getQualityAnalysis(resourceId),
    enabled: !!resourceId,
  });
}

export function useBatchReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: BatchReviewRequest) => curationApi.batchReview(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curation'] });
    },
  });
}

export function useBatchTag() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: BatchTagRequest) => curationApi.batchTag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curation'] });
    },
  });
}

export function useBatchAssign() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: BatchAssignRequest) => curationApi.batchAssign(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curation'] });
    },
  });
}

export function useBulkQualityCheck() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (resourceIds: string[]) => curationApi.bulkQualityCheck(resourceIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curation'] });
    },
  });
}
