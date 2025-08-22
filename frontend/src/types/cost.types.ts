export interface CostDataPoint {
  date: string;
  cost: number;
}

export interface ServiceCost {
  service: string;
  cost: number;
  percentage: number;
}

export interface CostSummary {
  total_cost: number;
  period: string;
  daily_costs: CostDataPoint[];
  top_services: [string, number][];
  analysis_date: string;
}

export interface OptimizationRecommendation {
  service: string;
  resource: string;
  recommendation: string;
  potential_savings: number;
  confidence: string;
  priority: string;
}

export interface SavingsCalculation {
  total_monthly_savings: number;
  total_annual_savings: number;
  confidence_level: string;
  detailed_calculations: any[];
  roi_analysis: {
    implementation_cost: number;
    payback_period_months: number;
    three_year_savings: number;
    three_year_roi_percentage: number;
  };
  recommendations: OptimizationRecommendation[];
}

export interface InfrastructureAnalysis {
  ec2_analysis: {
    total_instances: number;
    instances: Array<{
      instance_id: string;
      instance_type: string;
      avg_cpu_utilization: number;
      recommendation: string;
    }>;
    underutilized_count: number;
    potential_monthly_savings: number;
  };
  s3_analysis: {
    total_buckets_analyzed: number;
    total_size_gb: number;
    buckets: Array<{
      bucket_name: string;
      size_gb: number;
      recommendations: string[];
    }>;
  };
}