/**
 * Ingestion API Client
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * Provides repository ingestion and worker management endpoints
 */

import { apiClient } from '@/core/api/client';

const INGESTION_BASE = '/api/v1/ingestion';
const ADMIN_BASE = '/admin';

export interface IngestionJob {
  id: string;
  repo_url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
}

export interface WorkerStatusResponse {
  active_workers: number;
  worker_health: 'healthy' | 'degraded' | 'down';
  workers: Array<{
    id: string;
    type: 'cloud' | 'edge';
    status: 'online' | 'offline' | 'degraded';
    last_heartbeat: string;
    gpu_available?: boolean;
  }>;
}

export interface IngestionQueueStatus {
  pending: number;
  processing: number;
  completed: number;
  failed: number;
}

export const ingestionApi = {
  // Ingestion
  ingestRepository: (repoUrl: string) => 
    apiClient.post(`${INGESTION_BASE}/ingest/${encodeURIComponent(repoUrl)}`),
  
  getWorkerStatus: () => 
    apiClient.get<WorkerStatusResponse>(`${INGESTION_BASE}/worker/status`),
  
  getJobHistory: (params?: { limit?: number }) => 
    apiClient.get<IngestionJob[]>(`${INGESTION_BASE}/jobs/history`, { params }),
  
  getIngestionHealth: () => 
    apiClient.get(`${INGESTION_BASE}/health`),
  
  // Admin operations
  generateSparseEmbeddings: () => 
    apiClient.post(`${ADMIN_BASE}/sparse-embeddings/generate`),
};
