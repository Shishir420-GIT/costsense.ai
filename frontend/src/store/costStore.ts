import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { costApi } from '@/services/api';
import type { 
  CostSummary, 
  InfrastructureAnalysis, 
  OptimizationRecommendation,
  SavingsCalculation 
} from '@/types/cost.types';

interface CostState {
  // Data
  costSummary: CostSummary | null;
  infrastructureAnalysis: InfrastructureAnalysis | null;
  optimizationRecommendations: OptimizationRecommendation[];
  savingsCalculation: SavingsCalculation | null;
  
  // Loading states
  loadingCostData: boolean;
  loadingInfrastructure: boolean;
  loadingOptimizations: boolean;
  loadingSavings: boolean;
  
  // Selected time period
  selectedTimePeriod: string;
  
  // Actions
  fetchCostData: (timePeriod: string) => Promise<void>;
  fetchInfrastructureAnalysis: () => Promise<void>;
  fetchOptimizationRecommendations: (query: string, service?: string) => Promise<void>;
  calculateSavings: (optimizationData: any) => Promise<void>;
  setTimePeriod: (period: string) => void;
  
  // Reset
  reset: () => void;
}

export const useCostStore = create<CostState>()(
  devtools(
    (set, get) => ({
      // Initial state
      costSummary: null,
      infrastructureAnalysis: null,
      optimizationRecommendations: [],
      savingsCalculation: null,
      
      loadingCostData: false,
      loadingInfrastructure: false,
      loadingOptimizations: false,
      loadingSavings: false,
      
      selectedTimePeriod: '30_days',
      
      // Actions
      fetchCostData: async (timePeriod: string) => {
        set({ loadingCostData: true });
        try {
          const data = await costApi.getCostData(timePeriod);
          set({ 
            costSummary: data, 
            selectedTimePeriod: timePeriod,
            loadingCostData: false 
          });
        } catch (error) {
          console.error('Error fetching cost data:', error);
          set({ loadingCostData: false });
        }
      },
      
      fetchInfrastructureAnalysis: async () => {
        set({ loadingInfrastructure: true });
        try {
          const data = await costApi.getInfrastructureAnalysis();
          set({ 
            infrastructureAnalysis: data,
            loadingInfrastructure: false 
          });
        } catch (error) {
          console.error('Error fetching infrastructure analysis:', error);
          set({ loadingInfrastructure: false });
        }
      },
      
      fetchOptimizationRecommendations: async (query: string, service?: string) => {
        set({ loadingOptimizations: true });
        try {
          const response = await costApi.getOptimizationRecommendations({
            query,
            service,
            priority: 'savings'
          });
          
          set({ 
            optimizationRecommendations: response.recommendations,
            loadingOptimizations: false 
          });
        } catch (error) {
          console.error('Error fetching optimization recommendations:', error);
          set({ loadingOptimizations: false });
        }
      },
      
      calculateSavings: async (optimizationData: any) => {
        set({ loadingSavings: true });
        try {
          const data = await costApi.calculateSavings(optimizationData);
          set({ 
            savingsCalculation: data,
            loadingSavings: false 
          });
        } catch (error) {
          console.error('Error calculating savings:', error);
          set({ loadingSavings: false });
        }
      },
      
      setTimePeriod: (period: string) => {
        set({ selectedTimePeriod: period });
        get().fetchCostData(period);
      },
      
      reset: () => {
        set({
          costSummary: null,
          infrastructureAnalysis: null,
          optimizationRecommendations: [],
          savingsCalculation: null,
          loadingCostData: false,
          loadingInfrastructure: false,
          loadingOptimizations: false,
          loadingSavings: false,
          selectedTimePeriod: '30_days'
        });
      }
    }),
    {
      name: 'cost-store',
    }
  )
);