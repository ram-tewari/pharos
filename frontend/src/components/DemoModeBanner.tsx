import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';
import { DEMO_MODE } from '@/lib/demo/config';

export function DemoModeBanner() {
  if (!DEMO_MODE) return null;

  return (
    <Alert variant="info" className="animate-slide-in-from-top">
      <Info className="h-4 w-4" />
      <AlertDescription>
        <strong className="font-semibold">Demo Mode Active:</strong> Using mock data. Backend is offline.
      </AlertDescription>
    </Alert>
  );
}
