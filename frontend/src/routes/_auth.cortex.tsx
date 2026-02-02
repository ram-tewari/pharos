import { createFileRoute } from '@tanstack/react-router';
import { GraphPage } from '@/features/cortex/components/GraphPage';

export const Route = createFileRoute('/_auth/cortex')({
  component: GraphPage,
});
