/**
 * Azure Cost Optimization API Service
 *
 * This service provides compatibility layer between the frontend
 * and the new Azure-based backend
 */

import axios from 'axios';
import { toast } from 'react-hot-toast';
import type {
  CostAnalysisRequest,
  CostAnalysisResponse,
  OptimizationRequest,
  OptimizationResponse,
  HealthCheck
} from '@/types/api.types';
import type { AgentStatus, AgentResponse } from '@/types/agent.types';
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
    const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'An error occurred';
    toast.error(message);
    return Promise.reject(error);
  }
);

// Cost Analysis API - Adapted for Azure backend
export const costApi = {
  /**
   * Analyze costs using Azure AI agents
   */
  analyzeCosts: async (request: CostAnalysisRequest): Promise<CostAnalysisResponse> => {
    const response = await api.post('/api/v1/analyze', {
      query: request.query || request.message || 'Analyze my Azure costs'
    });

    // Transform Azure backend response to match frontend expectations
    return {
      analysis: response.data.analysis,
      recommendations: [],
      totalCost: 0,
      potentialSavings: 0,
      timestamp: response.data.timestamp,
      confidence: response.data.confidence || 'High'
    };
  },

  /**
   * Get cost summary data from Azure dashboard
   */
  getCostData: async (timePeriod: string = '30d'): Promise<CostSummary> => {
    const response = await api.get('/api/v1/dashboard/summary');
    const data = response.data;

    // Transform to match frontend CostSummary type
    return {
      total_cost: data.total_monthly_cost || 0,
      period: timePeriod,
      daily_costs: data.daily_costs || [],
      top_services: data.top_services || [],
      analysis_date: new Date().toISOString()
    };
  },

  /**
   * Get optimization recommendations
   */
  getOptimizationRecommendations: async (request?: OptimizationRequest): Promise<OptimizationResponse> => {
    const response = await api.get('/api/v1/recommendations');

    return {
      recommendations: response.data.recommendations || [],
      totalPotentialSavings: response.data.total_potential_savings || 0,
      priority: 'high',
      timestamp: new Date().toISOString()
    };
  },

  /**
   * Get infrastructure analysis
   */
  getInfrastructureAnalysis: async (): Promise<InfrastructureAnalysis> => {
    const [vmResponse, storageResponse] = await Promise.all([
      api.get('/api/v1/infrastructure/vms'),
      api.get('/api/v1/infrastructure/storage')
    ]);

    const vmData = vmResponse.data;
    const storageData = storageResponse.data;

    // Transform Azure VM/Storage data to EC2/S3 format expected by frontend
    return {
      ec2_analysis: {
        total_instances: vmData.totalInstances || 0,
        instances: (vmData.instances || []).map((vm: any) => ({
          instance_id: vm.name || vm.id,
          instance_type: vm.size || 'Unknown',
          avg_cpu_utilization: vm.cpuUtilization || 0,
          recommendation: vm.recommendation || 'No recommendation'
        })),
        underutilized_count: (vmData.instances || []).filter((vm: any) =>
          vm.cpuUtilization < 30 || vm.recommendation !== 'Optimal sizing'
        ).length,
        potential_monthly_savings: vmData.potentialSavings || 0
      },
      s3_analysis: {
        total_buckets_analyzed: storageData.totalAccounts || 0,
        total_size_gb: storageData.totalSizeGB || 0,
        buckets: (storageData.accounts || []).map((account: any) => ({
          bucket_name: account.name || account.accountName,
          size_gb: account.sizeGB || 0,
          recommendations: account.recommendations || []
        }))
      }
    };
  },

  /**
   * Calculate potential savings
   */
  calculateSavings: async (optimizationData?: any) => {
    // Use parallel analysis to get comprehensive savings calculation
    const response = await api.post('/api/v1/parallel-analysis', {
      query: 'Calculate total potential savings across all resources'
    });

    return {
      totalSavings: response.data.results?.financial_analysis?.match(/\$([0-9,]+\.\d{2})/)?.[0] || '$0.00',
      breakdown: response.data.results
    };
  }
};

// Agents API - Adapted for Azure multi-agent system
export const agentsApi = {
  /**
   * Execute a single agent query
   */
  executeAgent: async (agentName: string, query: string, context?: any): Promise<AgentResponse> => {
    const response = await api.post('/api/v1/analyze', { query });

    return {
      agentName,
      response: response.data.analysis,
      confidence: response.data.confidence || 'High',
      timestamp: response.data.timestamp,
      metadata: {
        agent_used: response.data.agent_used
      }
    };
  },

  /**
   * Execute multiple agents in parallel
   */
  executeMultiAgent: async (query: string, mode: string = 'parallel') => {
    const response = await api.post('/api/v1/parallel-analysis', { query });

    return {
      results: response.data.results,
      timestamp: response.data.timestamp,
      mode: 'parallel'
    };
  },

  /**
   * Get agent status
   */
  getAgentStatus: async (): Promise<AgentStatus> => {
    const response = await api.get('/api/v1/agent-status');

    return {
      orchestrator: response.data.orchestrator || 'active',
      agents: {
        cost_analyst: response.data.cost_analyst || 'active',
        infrastructure_analyst: response.data.infrastructure_analyst || 'active',
        financial_analyst: response.data.financial_analyst || 'active',
        remediation_specialist: response.data.remediation_specialist || 'active'
      },
      ollamaConnected: response.data.ollama_connected || false,
      langchainEnabled: response.data.langchain_enabled || true,
      timestamp: response.data.timestamp || new Date().toISOString()
    };
  },

  /**
   * Get agent capabilities
   */
  getAgentCapabilities: async () => {
    // Return static capabilities for Azure agents
    return {
      availableAgents: [
        'cost_analyst',
        'infrastructure_analyst',
        'financial_analyst',
        'remediation_specialist'
      ],
      capabilities: {
        cost_analysis: true,
        infrastructure_optimization: true,
        financial_projections: true,
        remediation_planning: true,
        parallel_execution: true,
        real_time_websocket: true
      },
      cloudProvider: 'Azure',
      aiFramework: 'LangChain',
      model: 'llama3.2:latest'
    };
  }
};

// Reports API - Placeholder (not yet implemented in Azure backend)
export const reportsApi = {
  generateReport: async (request: any) => {
    toast.info('Report generation will be available soon');
    return {
      reportId: 'mock-report-id',
      status: 'pending',
      message: 'Report generation coming soon in Azure version'
    };
  },

  downloadReport: async (reportId: string): Promise<Blob> => {
    throw new Error('Report download not yet implemented for Azure backend');
  },

  listReports: async () => {
    return {
      reports: [],
      message: 'Report listing coming soon'
    };
  },

  scheduleReport: async (reportData: any) => {
    toast.info('Report scheduling will be available soon');
    return {
      scheduleId: 'mock-schedule-id',
      status: 'pending'
    };
  }
};

// System API
export const systemApi = {
  /**
   * Check system health
   */
  healthCheck: async (): Promise<HealthCheck> => {
    const response = await api.get('/health');

    return {
      status: response.data.status,
      service: response.data.service,
      version: response.data.version,
      cloudProvider: response.data.cloud_provider,
      aiFramework: response.data.ai_framework,
      dependencies: response.data.dependencies,
      timestamp: new Date().toISOString()
    };
  },

  /**
   * Get agent status
   */
  getAgentStatus: async () => {
    const response = await api.get('/api/v1/agent-status');
    return response.data;
  }
};

export default api;
