import { createFileRoute } from '@tanstack/react-router';
import { LibraryPage } from '@/features/library/LibraryPage';

export const Route = createFileRoute('/_auth/library')({
  component: LibraryPage,
});
