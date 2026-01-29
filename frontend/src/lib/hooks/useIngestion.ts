/**
 * Ingestion Hooks
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * TanStack Query hooks for ingestion operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ingestionApi } from '@/lib/api/ingestion';

const REFETCH_INTERVAL = 30000; // 30 seconds

export function useWorkerStatus() {
  return useQuery({
    queryKey: ['ingestion', 'worker-status'],
    queryFn: ingestionApi.getWorkerStatus,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useJobHistory(limit = 50) {
  return useQuery({
    queryKey: ['ingestion', 'job-history', limit],
    queryFn: () => ingestionApi.getJobHistory({ limit }),
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useIngestionHealth() {
  return useQuery({
    queryKey: ['ingestion', 'health'],
    queryFn: ingestionApi.getIngestionHealth,
    refetchInterval: REFETCH_INTERVAL,
  });
}

export function useIngestRepository() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (repoUrl: string) => ingestionApi.ingestRepository(repoUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingestion', 'job-history'] });
    },
  });
}

export function useGenerateSparseEmbeddings() {
  return useMutation({
    mutationFn: ingestionApi.generateSparseEmbeddings,
  });
}
