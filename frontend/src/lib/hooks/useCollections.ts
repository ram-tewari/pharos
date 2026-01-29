import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { collectionsApi } from '@/lib/api/collections';
import { useCollectionsStore } from '@/stores/collections';
import type { Collection, CollectionCreate, CollectionUpdate } from '@/types/library';

/**
 * Custom hook for managing collections with TanStack Query
 * Provides collection CRUD operations and batch resource management
 * with optimistic updates and cache management
 */
export function useCollections() {
  const queryClient = useQueryClient();
  const {
    setCollections,
    addCollection,
    updateCollection: updateCollectionInStore,
    removeCollection,
  } = useCollectionsStore();

  // Fetch collections
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['collections'],
    queryFn: async () => {
      const collections = await collectionsApi.listCollections();
      setCollections(collections);
      return collections;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create mutation with optimistic updates
  const createMutation = useMutation({
    mutationFn: (newCollection: CollectionCreate) => collectionsApi.createCollection(newCollection),
    onMutate: async (newCollection) => {
      await queryClient.cancelQueries({ queryKey: ['collections'] });

      // Optimistic update
      const tempCollection: Partial<Collection> = {
        id: `temp-${Date.now()}`,
        ...newCollection,
        resource_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      addCollection(tempCollection as Collection);

      return { tempCollection };
    },
    onSuccess: (data, _variables, context) => {
      // Replace temp with real collection
      if (context?.tempCollection) {
        removeCollection(context.tempCollection.id!);
      }
      addCollection(data);
      queryClient.invalidateQueries({ queryKey: ['collections'] });
    },
    onError: (_error, _variables, context) => {
      // Remove temp collection on error
      if (context?.tempCollection) {
        removeCollection(context.tempCollection.id!);
      }
    },
  });

  // Update mutation with optimistic updates
  const updateMutation = useMutation({
    mutationFn: ({ collectionId, updates }: { collectionId: string; updates: CollectionUpdate }) =>
      collectionsApi.updateCollection(collectionId, updates),
    onMutate: async ({ collectionId, updates }) => {
      await queryClient.cancelQueries({ queryKey: ['collections'] });

      // Snapshot previous value
      const previousCollections = queryClient.getQueryData(['collections']);

      // Optimistic update
      updateCollectionInStore(collectionId, updates);

      return { previousCollections };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousCollections) {
        setCollections(context.previousCollections as Collection[]);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
    },
  });

  // Delete mutation with optimistic updates
  const deleteMutation = useMutation({
    mutationFn: (collectionId: string) => collectionsApi.deleteCollection(collectionId),
    onMutate: async (collectionId) => {
      await queryClient.cancelQueries({ queryKey: ['collections'] });

      // Snapshot previous value
      const previousCollections = queryClient.getQueryData(['collections']);

      // Optimistic update
      removeCollection(collectionId);

      return { previousCollections };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousCollections) {
        setCollections(context.previousCollections as Collection[]);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
    },
  });

  // Batch add resources mutation
  const batchAddMutation = useMutation({
    mutationFn: ({ collectionId, resourceIds }: { collectionId: string; resourceIds: string[] }) =>
      collectionsApi.batchAddResources(collectionId, resourceIds),
    onSuccess: (_data, variables) => {
      // Invalidate queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      queryClient.invalidateQueries({ queryKey: ['collection-resources', variables.collectionId] });
    },
  });

  // Batch remove resources mutation
  const batchRemoveMutation = useMutation({
    mutationFn: ({ collectionId, resourceIds }: { collectionId: string; resourceIds: string[] }) =>
      collectionsApi.batchRemoveResources(collectionId, resourceIds),
    onSuccess: (_data, variables) => {
      // Invalidate queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      queryClient.invalidateQueries({ queryKey: ['collection-resources', variables.collectionId] });
    },
  });

  return {
    // Data
    collections: data || [],
    total: data?.length || 0,

    // Loading states
    isLoading,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isBatchAdding: batchAddMutation.isPending,
    isBatchRemoving: batchRemoveMutation.isPending,

    // Error states
    error,
    createError: createMutation.error,
    updateError: updateMutation.error,
    deleteError: deleteMutation.error,
    batchAddError: batchAddMutation.error,
    batchRemoveError: batchRemoveMutation.error,

    // Actions
    createCollection: createMutation.mutate,
    updateCollection: updateMutation.mutate,
    deleteCollection: deleteMutation.mutate,
    batchAddResources: batchAddMutation.mutate,
    batchRemoveResources: batchRemoveMutation.mutate,
    refetch,
  };
}
