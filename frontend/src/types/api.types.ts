export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: 'success' | 'error' | 'loading';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CostAnalysisRequest {
  query: string;
  time_period?: string;
  services?: string[];
}

export interface CostAnalysisResponse {
  analysis: string;
  timestamp: string;
  confidence: string;
}

export interface OptimizationRequest {
  query: string;
  service?: string;
  priority?: string;
}

export interface OptimizationResponse {
  recommendations: Array<{
    service: string;
    resource: string;
    recommendation: string;
    potential_savings: number;
    confidence: string;
  }>;
  potential_savings: number;
  implementation_plan: string;
  timestamp: string;
}

export interface ReportRequest {
  report_type: 'cost_analysis' | 'optimization' | 'comprehensive';
  time_period?: string;
  format?: 'json' | 'csv' | 'pdf';
  include_recommendations?: boolean;
  email_recipients?: string[];
}

export interface ReportResponse {
  report_id: string;
  report_path: string;
  format: string;
  generated_at: string;
  download_url: string;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
  dependencies: {
    ollama: 'connected' | 'disconnected' | 'unknown';
    aws: 'connected' | 'disconnected' | 'unknown';
  };
}