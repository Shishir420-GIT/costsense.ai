export interface Agent {
  name: string;
  status: 'active' | 'inactive' | 'error';
  description: string;
  capabilities: string[];
  tools: string[];
}

export interface AgentResponse {
  agent_name: string;
  response: string;
  execution_time: number;
  timestamp: string;
}

export interface AgentStatus {
  overall_health: 'healthy' | 'degraded' | 'unhealthy' | 'error';
  agents: Record<string, 'healthy' | 'unhealthy'>;
  healthy_agents: number;
  total_agents: number;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'ack' | 'status' | 'agent_stream' | 'agent_result' | 'analysis_complete' | 'error';
  message?: string;
  content?: string;
  agent?: string;
  result?: string;
  results?: Record<string, string>;
  progress?: number;
  is_complete?: boolean;
  timestamp?: string;
}

export interface AnalysisRequest {
  type: 'cost_analysis' | 'optimization_request' | 'parallel_analysis' | 'comprehensive_analysis';
  query: string;
  service?: string;
}

export interface AgentCapabilities {
  [agentName: string]: {
    description: string;
    capabilities: string[];
    tools: string[];
  };
}