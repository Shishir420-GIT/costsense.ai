import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { agentsApi } from '@/services/api';
import webSocketService from '@/services/websocket';
import type { 
  AgentStatus, 
  AgentCapabilities, 
  AgentResponse,
  WebSocketMessage 
} from '@/types/agent.types';

interface AgentState {
  // Agent Status
  agentStatus: AgentStatus | null;
  agentCapabilities: AgentCapabilities | null;
  
  // WebSocket Connection
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  
  // Analysis State
  currentAnalysis: {
    type: string | null;
    query: string | null;
    progress: number;
    status: 'idle' | 'analyzing' | 'complete' | 'error';
    results: Record<string, any>;
    messages: WebSocketMessage[];
  };
  
  // Agent Responses
  agentResponses: Record<string, AgentResponse[]>;
  
  // Loading states
  loadingStatus: boolean;
  loadingCapabilities: boolean;
  
  // Actions
  fetchAgentStatus: () => Promise<void>;
  fetchAgentCapabilities: () => Promise<void>;
  executeAgent: (agentName: string, query: string, context?: any) => Promise<void>;
  executeMultiAgent: (query: string, mode?: string) => Promise<void>;
  
  // WebSocket Actions
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  sendAnalysisRequest: (type: string, query: string, service?: string) => void;
  
  // Analysis Actions
  startAnalysis: (type: string, query: string) => void;
  updateAnalysisProgress: (progress: number, status?: string) => void;
  addAnalysisResult: (agentName: string, result: any) => void;
  completeAnalysis: (results: any) => void;
  clearAnalysis: () => void;
  
  // Message Actions
  addMessage: (message: WebSocketMessage) => void;
  clearMessages: () => void;
  
  // Reset
  reset: () => void;
}

export const useAgentStore = create<AgentState>()(
  devtools(
    (set, get) => ({
      // Initial state
      agentStatus: null,
      agentCapabilities: null,
      
      isConnected: false,
      connectionStatus: 'disconnected',
      
      currentAnalysis: {
        type: null,
        query: null,
        progress: 0,
        status: 'idle',
        results: {},
        messages: []
      },
      
      agentResponses: {},
      
      loadingStatus: false,
      loadingCapabilities: false,
      
      // Actions
      fetchAgentStatus: async () => {
        set({ loadingStatus: true });
        try {
          const status = await agentsApi.getAgentStatus();
          set({ 
            agentStatus: status,
            loadingStatus: false 
          });
        } catch (error) {
          console.error('Error fetching agent status:', error);
          set({ loadingStatus: false });
        }
      },
      
      fetchAgentCapabilities: async () => {
        set({ loadingCapabilities: true });
        try {
          const capabilities = await agentsApi.getAgentCapabilities();
          set({ 
            agentCapabilities: capabilities,
            loadingCapabilities: false 
          });
        } catch (error) {
          console.error('Error fetching agent capabilities:', error);
          set({ loadingCapabilities: false });
        }
      },
      
      executeAgent: async (agentName: string, query: string, context?: any) => {
        try {
          const response = await agentsApi.executeAgent(agentName, query, context);
          
          const currentResponses = get().agentResponses[agentName] || [];
          set({
            agentResponses: {
              ...get().agentResponses,
              [agentName]: [...currentResponses, response]
            }
          });
        } catch (error) {
          console.error(`Error executing agent ${agentName}:`, error);
        }
      },
      
      executeMultiAgent: async (query: string, mode: string = 'parallel') => {
        try {
          const response = await agentsApi.executeMultiAgent(query, mode);
          
          set({
            currentAnalysis: {
              ...get().currentAnalysis,
              results: response.results,
              status: 'complete'
            }
          });
        } catch (error) {
          console.error('Error executing multi-agent analysis:', error);
          set({
            currentAnalysis: {
              ...get().currentAnalysis,
              status: 'error'
            }
          });
        }
      },
      
      // WebSocket Actions
      connectWebSocket: () => {
        set({ connectionStatus: 'connecting' });
        
        webSocketService.on('connected', () => {
          set({ 
            isConnected: true, 
            connectionStatus: 'connected' 
          });
        });
        
        webSocketService.on('disconnected', () => {
          set({ 
            isConnected: false, 
            connectionStatus: 'disconnected' 
          });
        });
        
        webSocketService.on('error', () => {
          set({ 
            isConnected: false, 
            connectionStatus: 'error' 
          });
        });
        
        webSocketService.on('message', (message: WebSocketMessage) => {
          get().addMessage(message);
          
          // Handle different message types
          switch (message.type) {
            case 'status':
              if (message.progress !== undefined) {
                get().updateAnalysisProgress(message.progress, message.message);
              }
              break;
              
            case 'agent_result':
              if (message.agent && message.result) {
                get().addAnalysisResult(message.agent, message.result);
              }
              break;
              
            case 'analysis_complete':
            case 'optimization_complete':
            case 'parallel_analysis_complete':
            case 'comprehensive_analysis_complete':
              get().completeAnalysis(message.result || message.results);
              break;
              
            case 'error':
              set({
                currentAnalysis: {
                  ...get().currentAnalysis,
                  status: 'error'
                }
              });
              break;
          }
        });
      },
      
      disconnectWebSocket: () => {
        webSocketService.disconnect();
        set({ 
          isConnected: false, 
          connectionStatus: 'disconnected' 
        });
      },
      
      sendAnalysisRequest: (type: string, query: string, service?: string) => {
        if (!get().isConnected) {
          console.error('WebSocket not connected');
          return;
        }
        
        get().startAnalysis(type, query);
        
        try {
          switch (type) {
            case 'cost_analysis':
              webSocketService.requestCostAnalysis(query);
              break;
            case 'optimization_request':
              webSocketService.requestOptimization(query, service);
              break;
            case 'parallel_analysis':
              webSocketService.requestParallelAnalysis(query);
              break;
            case 'comprehensive_analysis':
              webSocketService.requestComprehensiveAnalysis(query);
              break;
            default:
              webSocketService.send({ type: type as any, query, service });
          }
        } catch (error) {
          console.error('Error sending WebSocket message:', error);
          set({
            currentAnalysis: {
              ...get().currentAnalysis,
              status: 'error'
            }
          });
        }
      },
      
      // Analysis Actions
      startAnalysis: (type: string, query: string) => {
        set({
          currentAnalysis: {
            type,
            query,
            progress: 0,
            status: 'analyzing',
            results: {},
            messages: []
          }
        });
      },
      
      updateAnalysisProgress: (progress: number, status?: string) => {
        set({
          currentAnalysis: {
            ...get().currentAnalysis,
            progress,
            ...(status && { status: status as any })
          }
        });
      },
      
      addAnalysisResult: (agentName: string, result: any) => {
        set({
          currentAnalysis: {
            ...get().currentAnalysis,
            results: {
              ...get().currentAnalysis.results,
              [agentName]: result
            }
          }
        });
      },
      
      completeAnalysis: (results: any) => {
        set({
          currentAnalysis: {
            ...get().currentAnalysis,
            results: typeof results === 'object' ? results : { analysis: results },
            status: 'complete',
            progress: 100
          }
        });
      },
      
      clearAnalysis: () => {
        set({
          currentAnalysis: {
            type: null,
            query: null,
            progress: 0,
            status: 'idle',
            results: {},
            messages: []
          }
        });
      },
      
      // Message Actions
      addMessage: (message: WebSocketMessage) => {
        set({
          currentAnalysis: {
            ...get().currentAnalysis,
            messages: [...get().currentAnalysis.messages, message]
          }
        });
      },
      
      clearMessages: () => {
        set({
          currentAnalysis: {
            ...get().currentAnalysis,
            messages: []
          }
        });
      },
      
      reset: () => {
        get().disconnectWebSocket();
        set({
          agentStatus: null,
          agentCapabilities: null,
          isConnected: false,
          connectionStatus: 'disconnected',
          currentAnalysis: {
            type: null,
            query: null,
            progress: 0,
            status: 'idle',
            results: {},
            messages: []
          },
          agentResponses: {},
          loadingStatus: false,
          loadingCapabilities: false
        });
      }
    }),
    {
      name: 'agent-store',
    }
  )
);