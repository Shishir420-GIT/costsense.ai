import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { systemApi } from '@/services/api';
import type { HealthCheck } from '@/types/api.types';

interface AppState {
  // System Health
  systemHealth: HealthCheck | null;
  
  // UI State
  sidebarOpen: boolean;
  currentPage: string;
  theme: 'light' | 'dark';
  
  // Loading states
  loadingHealth: boolean;
  
  // User preferences
  preferences: {
    defaultTimePeriod: string;
    autoRefresh: boolean;
    refreshInterval: number;
    notifications: boolean;
    compactView: boolean;
  };
  
  // Actions
  fetchSystemHealth: () => Promise<void>;
  setSidebarOpen: (open: boolean) => void;
  setCurrentPage: (page: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  updatePreferences: (preferences: Partial<AppState['preferences']>) => void;
  
  // Reset
  reset: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        systemHealth: null,
        
        sidebarOpen: true,
        currentPage: 'dashboard',
        theme: 'light',
        
        loadingHealth: false,
        
        preferences: {
          defaultTimePeriod: '30_days',
          autoRefresh: true,
          refreshInterval: 300000, // 5 minutes
          notifications: true,
          compactView: false
        },
        
        // Actions
        fetchSystemHealth: async () => {
          set({ loadingHealth: true });
          try {
            const health = await systemApi.healthCheck();
            set({ 
              systemHealth: health,
              loadingHealth: false 
            });
          } catch (error) {
            console.error('Error fetching system health:', error);
            set({ 
              systemHealth: null,
              loadingHealth: false 
            });
          }
        },
        
        setSidebarOpen: (open: boolean) => {
          set({ sidebarOpen: open });
        },
        
        setCurrentPage: (page: string) => {
          set({ currentPage: page });
        },
        
        setTheme: (theme: 'light' | 'dark') => {
          set({ theme });
          
          // Apply theme to document
          if (theme === 'dark') {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        },
        
        updatePreferences: (newPreferences: Partial<AppState['preferences']>) => {
          set({
            preferences: {
              ...get().preferences,
              ...newPreferences
            }
          });
        },
        
        reset: () => {
          set({
            systemHealth: null,
            sidebarOpen: true,
            currentPage: 'dashboard',
            loadingHealth: false,
            preferences: {
              defaultTimePeriod: '30_days',
              autoRefresh: true,
              refreshInterval: 300000,
              notifications: true,
              compactView: false
            }
          });
        }
      }),
      {
        name: 'app-store',
        // Only persist user preferences and UI state
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          theme: state.theme,
          preferences: state.preferences
        })
      }
    ),
    {
      name: 'app-store',
    }
  )
);