/**
 * Demo Mode Configuration
 * 
 * Demo mode is DISABLED. All API calls go to the live backend.
 */

export const DEMO_MODE = false;

export const demoConfig = {
  enabled: false,
  user: {
    user_id: 'demo-user-123',
    email: 'demo@neoalexandria.dev',
    name: 'Demo User',
    tier: 'premium' as const,
    created_at: new Date().toISOString(),
  },
  repositories: [
    {
      id: 'repo-1',
      name: 'react-query',
      url: 'https://github.com/tanstack/react-query',
      description: 'Powerful asynchronous state management',
      language: 'TypeScript',
      stars: 35000,
      lastUpdated: '2024-01-15',
    },
    {
      id: 'repo-2',
      name: 'zustand',
      url: 'https://github.com/pmndrs/zustand',
      description: 'Bear necessities for state management',
      language: 'TypeScript',
      stars: 28000,
      lastUpdated: '2024-01-20',
    },
    {
      id: 'repo-3',
      name: 'fastapi',
      url: 'https://github.com/tiangolo/fastapi',
      description: 'Modern, fast web framework for Python',
      language: 'Python',
      stars: 65000,
      lastUpdated: '2024-01-25',
    },
  ],
  documents: [
    {
      id: 'doc-1',
      title: 'Attention Is All You Need',
      type: 'pdf',
      url: 'https://arxiv.org/pdf/1706.03762.pdf',
      authors: ['Vaswani et al.'],
      year: 2017,
      pages: 15,
      thumbnail: 'https://via.placeholder.com/200x280/4f46e5/ffffff?text=Transformer',
      collections: ['machine-learning', 'nlp'],
      quality_score: 0.95,
      tags: ['transformers', 'attention', 'neural-networks'],
    },
    {
      id: 'doc-2',
      title: 'BERT: Pre-training of Deep Bidirectional Transformers',
      type: 'pdf',
      url: 'https://arxiv.org/pdf/1810.04805.pdf',
      authors: ['Devlin et al.'],
      year: 2018,
      pages: 16,
      thumbnail: 'https://via.placeholder.com/200x280/7c3aed/ffffff?text=BERT',
      collections: ['machine-learning', 'nlp'],
      quality_score: 0.92,
      tags: ['bert', 'language-models', 'pre-training'],
    },
    {
      id: 'doc-3',
      title: 'Deep Residual Learning for Image Recognition',
      type: 'pdf',
      url: 'https://arxiv.org/pdf/1512.03385.pdf',
      authors: ['He et al.'],
      year: 2015,
      pages: 12,
      thumbnail: 'https://via.placeholder.com/200x280/dc2626/ffffff?text=ResNet',
      collections: ['machine-learning', 'computer-vision'],
      quality_score: 0.98,
      tags: ['resnet', 'cnn', 'image-recognition'],
    },
    {
      id: 'doc-4',
      title: 'Generative Adversarial Networks',
      type: 'pdf',
      url: 'https://arxiv.org/pdf/1406.2661.pdf',
      authors: ['Goodfellow et al.'],
      year: 2014,
      pages: 9,
      thumbnail: 'https://via.placeholder.com/200x280/059669/ffffff?text=GAN',
      collections: ['machine-learning', 'generative-models'],
      quality_score: 0.96,
      tags: ['gan', 'generative', 'adversarial'],
    },
  ],
  collections: [
    {
      id: 'machine-learning',
      name: 'Machine Learning',
      description: 'Core ML papers and resources',
      documentCount: 4,
      color: '#4f46e5',
    },
    {
      id: 'nlp',
      name: 'Natural Language Processing',
      description: 'NLP and language models',
      documentCount: 2,
      color: '#7c3aed',
    },
    {
      id: 'computer-vision',
      name: 'Computer Vision',
      description: 'Image and video processing',
      documentCount: 1,
      color: '#dc2626',
    },
    {
      id: 'generative-models',
      name: 'Generative Models',
      description: 'GANs, VAEs, and diffusion models',
      documentCount: 1,
      color: '#059669',
    },
  ],
  codeFile: {
    id: 'file-1',
    name: 'useQuery.ts',
    path: 'packages/react-query/src/useQuery.ts',
    language: 'typescript',
    content: `import { useEffect } from 'react';
import { QueryObserver } from '@tanstack/query-core';
import { useQueryClient } from './QueryClientProvider';

export function useQuery<TData = unknown, TError = unknown>(
  options: UseQueryOptions<TData, TError>
) {
  const client = useQueryClient();
  const [observer] = useState(() => new QueryObserver(client, options));
  
  const result = useSyncExternalStore(
    useCallback(
      (onStoreChange) => observer.subscribe(onStoreChange),
      [observer]
    ),
    () => observer.getCurrentResult(),
    () => observer.getCurrentResult()
  );

  useEffect(() => {
    observer.setOptions(options);
  }, [observer, options]);

  return result;
}`,
    chunks: [
      {
        id: 'chunk-1',
        startLine: 1,
        endLine: 5,
        type: 'import',
        summary: 'Import dependencies for useQuery hook',
      },
      {
        id: 'chunk-2',
        startLine: 7,
        endLine: 12,
        type: 'function',
        summary: 'Main useQuery hook implementation with QueryObserver',
      },
      {
        id: 'chunk-3',
        startLine: 14,
        endLine: 20,
        type: 'hook',
        summary: 'Subscribe to query observer with useSyncExternalStore',
      },
    ],
    annotations: [
      {
        id: 'ann-1',
        startLine: 7,
        endLine: 7,
        text: 'Generic types allow flexible data and error handling',
        color: '#4f46e5',
        tags: ['typescript', 'generics'],
      },
      {
        id: 'ann-2',
        startLine: 10,
        endLine: 10,
        text: 'QueryObserver manages query lifecycle and caching',
        color: '#7c3aed',
        tags: ['architecture', 'caching'],
      },
    ],
    quality: {
      overall: 0.89,
      dimensions: {
        readability: 0.92,
        maintainability: 0.88,
        testability: 0.85,
        documentation: 0.90,
      },
    },
  },
};

// Export demo plan for planner
export { demoPlan } from './plannerData';
