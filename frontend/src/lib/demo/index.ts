/**
 * Demo Mode Interceptor
 * 
 * Intercepts API calls and returns mock data when DEMO_MODE is enabled.
 * Usage: Wrap your API hooks with useDemoMode()
 */

import { DEMO_MODE, demoConfig } from './config';
import { demoApi } from './api';

export function useDemoMode() {
  return {
    enabled: DEMO_MODE,
    config: demoConfig,
    api: demoApi,
  };
}

/**
 * Wrap API call with demo mode fallback
 */
export async function withDemoMode<T>(
  apiCall: () => Promise<T>,
  demoCall: () => Promise<T>
): Promise<T> {
  if (DEMO_MODE) {
    if (import.meta.env.DEV) {
      console.log('[DEMO MODE] Using mock data');
    }
    return demoCall();
  }
  return apiCall();
}
