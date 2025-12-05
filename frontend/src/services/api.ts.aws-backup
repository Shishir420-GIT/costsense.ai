import axios from 'axios';
import { toast } from 'react-hot-toast';
import type {
  CostAnalysisRequest,
  CostAnalysisResponse,
  OptimizationRequest,
  OptimizationResponse,
  ReportRequest,
  ReportResponse,
  HealthCheck
} from '@/types/api.types';
import type { AgentStatus, AgentCapabilities, AgentResponse } from '@/types/agent.types';
import type { CostSummary, InfrastructureAnalysis } from '@/types/cost.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`📡 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error);
    const message = error.response?.data?.message || error.message || 'An error occurred';
    toast.error(message);
    return Promise.reject(error);
  }
);

// Cost Analysis API
export const costApi = {
  analyzeCosts: async (request: CostAnalysisRequest): Promise<CostAnalysisResponse> => {
    const response = await api.post('/api/v1/analyze-costs', request);
    return response.data;
  },

  getCostData: async (timePeriod: string): Promise<CostSummary> => {
    const response = await api.get(`/api/v1/cost-data/${timePeriod}`);
    return response.data;
  },

  getOptimizationRecommendations: async (request: OptimizationRequest): Promise<OptimizationResponse> => {
    const response = await api.post('/api/v1/optimize', request);
    return response.data;
  },

  getInfrastructureAnalysis: async (): Promise<InfrastructureAnalysis> => {
    const response = await api.get('/api/v1/infrastructure-analysis');
    return response.data;
  },

  calculateSavings: async (optimizationData: any) => {
    const response = await api.post('/api/v1/calculate-savings', optimizationData);
    return response.data;
  }
};

// Agents API
export const agentsApi = {
  executeAgent: async (agentName: string, query: string, context?: any): Promise<AgentResponse> => {
    const response = await api.post('/api/v1/agents/execute', {
      agent_name: agentName,
      query,
      context
    });
    return response.data;
  },

  executeMultiAgent: async (query: string, mode: string = 'parallel') => {
    const response = await api.post('/api/v1/agents/multi-agent', {
      query,
      mode
    });
    return response.data;
  },

  getAgentStatus: async (): Promise<AgentStatus> => {
    const response = await api.get('/api/v1/agents/status');
    return response.data;
  },

  getAgentCapabilities: async (): Promise<AgentCapabilities> => {
    const response = await api.get('/api/v1/agents/capabilities');
    return response.data;
  }
};

// Reports API
export const reportsApi = {
  generateReport: async (request: ReportRequest): Promise<ReportResponse> => {
    const response = await api.post('/api/v1/reports/generate', request);
    return response.data;
  },

  downloadReport: async (reportId: string): Promise<Blob> => {
    const response = await api.get(`/api/v1/reports/download/${reportId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  listReports: async () => {
    const response = await api.get('/api/v1/reports/list');
    return response.data;
  },

  scheduleReport: async (reportData: any) => {
    const response = await api.post('/api/v1/reports/schedule', reportData);
    return response.data;
  }
};

// System API
export const systemApi = {
  healthCheck: async (): Promise<HealthCheck> => {
    const response = await api.get('/health');
    return response.data;
  },

  getAgentStatus: async (): Promise<any> => {
    const response = await api.get('/api/v1/agent-status');
    return response.data;
  }
};

export default api;