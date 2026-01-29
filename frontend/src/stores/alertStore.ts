/**
 * Alert Store
 * 
 * Phase 7: Ops & Edge Management (Option C)
 * State management for smart alerts system
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AlertSeverity = 'info' | 'warning' | 'critical';

export interface Alert {
  id: string;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  source: string;
  acknowledged: boolean;
}

export interface AlertPreferences {
  errorRateThreshold: number;
  responseTimeThreshold: number;
  queueLengthThreshold: number;
  soundEnabled: boolean;
  metrics: string[];
}

interface AlertStore {
  // State
  alerts: Alert[];
  alertHistory: Alert[];
  preferences: AlertPreferences;
  
  // Actions
  addAlert: (alert: Omit<Alert, 'id' | 'timestamp' | 'acknowledged'>) => void;
  acknowledgeAlert: (alertId: string) => void;
  dismissAlert: (alertId: string) => void;
  clearAlerts: () => void;
  updatePreferences: (preferences: Partial<AlertPreferences>) => void;
}

const DEFAULT_PREFERENCES: AlertPreferences = {
  errorRateThreshold: 5,
  responseTimeThreshold: 500,
  queueLengthThreshold: 100,
  soundEnabled: false,
  metrics: ['error_rate', 'response_time', 'queue_length'],
};

export const useAlertStore = create<AlertStore>()(
  persist(
    (set) => ({
      // Initial state
      alerts: [],
      alertHistory: [],
      preferences: DEFAULT_PREFERENCES,
      
      // Actions
      addAlert: (alert) => set((state) => {
        const newAlert: Alert = {
          ...alert,
          id: `alert-${Date.now()}-${Math.random()}`,
          timestamp: new Date().toISOString(),
          acknowledged: false,
        };
        
        return {
          alerts: [...state.alerts, newAlert],
          alertHistory: [newAlert, ...state.alertHistory].slice(0, 100), // Keep last 100
        };
      }),
      
      acknowledgeAlert: (alertId) => set((state) => ({
        alerts: state.alerts.map((a) => 
          a.id === alertId ? { ...a, acknowledged: true } : a
        ),
        alertHistory: state.alertHistory.map((a) => 
          a.id === alertId ? { ...a, acknowledged: true } : a
        ),
      })),
      
      dismissAlert: (alertId) => set((state) => ({
        alerts: state.alerts.filter((a) => a.id !== alertId),
      })),
      
      clearAlerts: () => set({ alerts: [] }),
      
      updatePreferences: (preferences) => set((state) => ({
        preferences: { ...state.preferences, ...preferences },
      })),
    }),
    {
      name: 'alert-store',
      partialize: (state) => ({ 
        alertHistory: state.alertHistory,
        preferences: state.preferences,
      }),
    }
  )
);
