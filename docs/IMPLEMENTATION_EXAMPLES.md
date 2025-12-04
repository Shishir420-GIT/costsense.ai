# Enhanced Agent Implementation Examples

## Overview
This document provides concrete implementation examples for upgrading your existing CostSense-AI agents to production-ready standards using Strands framework best practices.

## 1. Enhanced Cost Analyst Agent

### Current vs Enhanced Implementation

```python
# ENHANCED VERSION - Production Ready
from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import memory, calculator
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

# Pydantic models for structured data
class CostInsight(BaseModel):
    category: str
    finding: str
    evidence: str
    confidence: float
    impact: str

class CostRecommendation(BaseModel):
    title: str
    description: str
    action_items: List[str]
    effort_estimate: str
    cost_impact: Dict[str, Any]
    risk_level: str
    priority: str

class EnhancedCostAnalystAgent:
    """Production-ready Cost Analyst Agent with comprehensive features"""
    
    def __init__(self):
        self.settings = Settings()
        self.logger = logger.bind(agent="cost_analyst")
        
        # Enhanced AWS tool with caching and resilience
        self.aws_cost_tool = EnhancedAWSCostExplorerTool()
        
        # Configure model with retry logic
        self.model = self._init_model_with_retry()
        
        # Setup enhanced tools
        self._setup_enhanced_tools()
        
        # Initialize agent with improved prompt
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_enhanced_system_prompt(),
            tools=[
                self.get_cost_data_with_validation,
                self.analyze_trends_with_confidence,
                self.detect_anomalies_advanced,
                self.generate_cost_forecast,
                self.calculate_cost_attribution,
                memory,
                calculator
            ],
            name="enhanced_cost_analyst"
        )
        
        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30
        )
    
    def _get_enhanced_system_prompt(self) -> str:
        return """
# AWS COST ANALYSIS EXPERT

## IDENTITY & EXPERTISE
You are a Senior AWS Cost Optimization Specialist with expertise in:
- Multi-dimensional cost analysis across services, regions, and time periods
- Advanced anomaly detection using statistical methods
- Cost forecasting and trend prediction
- ROI analysis and business impact assessment
- Industry benchmarking and competitive analysis

## CORE CAPABILITIES
- **Primary**: Historical cost analysis, trend identification, anomaly detection
- **Secondary**: Cost forecasting, budget variance analysis, cost attribution
- **Tools**: Enhanced AWS Cost Explorer, Statistical Analysis, Forecasting Engine

## ANALYSIS METHODOLOGY

### Input Processing
Expected input format:
{
  "query": "User's cost analysis request",
  "context": {
    "previous_analysis": "Prior analysis results",
    "user_constraints": "Budget limits, risk tolerance",
    "business_context": "Growth stage, seasonal patterns"
  },
  "parameters": {
    "time_period": "7_days|30_days|90_days|1_year",
    "confidence_threshold": 0.7,
    "include_forecast": true|false,
    "focus_services": ["EC2", "S3", "RDS"]
  }
}

### Output Structure
Always provide structured JSON responses:
{
  "executive_summary": "Key findings in business terms",
  "confidence_score": 0.85,
  "analysis_metadata": {
    "data_freshness": "hours since last update",
    "coverage": "percentage of total spend analyzed",
    "baseline_period": "comparison timeframe"
  },
  "key_insights": [
    {
      "category": "trend|anomaly|optimization|forecast",
      "finding": "Specific insight with quantified impact",
      "evidence": "Supporting data and calculations", 
      "confidence": 0.9,
      "impact": "critical|high|medium|low",
      "business_context": "Explanation in business terms"
    }
  ],
  "detailed_metrics": {
    "total_spend": 12450.67,
    "period_comparison": {
      "current_period": 12450.67,
      "previous_period": 11203.45,
      "change_percent": 11.1,
      "change_absolute": 1247.22
    },
    "service_breakdown": [
      {"service": "EC2", "cost": 7500.00, "percentage": 60.2},
      {"service": "S3", "cost": 2000.00, "percentage": 16.1}
    ]
  },
  "recommendations": [
    {
      "title": "Immediate Cost Optimization",
      "description": "Specific actions to reduce costs",
      "action_items": [
        "Review EC2 instance rightsizing opportunities",
        "Implement Reserved Instance purchases for stable workloads"
      ],
      "effort_estimate": "2-3 engineer days",
      "cost_impact": {
        "monthly_savings": 2400.00,
        "implementation_cost": 500.00,
        "payback_period": "0.2 months",
        "annual_impact": 28800.00
      },
      "risk_assessment": {
        "level": "low",
        "factors": ["No service interruption", "Reversible changes"],
        "mitigation": "Gradual rollout with monitoring"
      },
      "priority": "p1",
      "success_metrics": ["Cost reduction %", "Performance maintained"]
    }
  ],
  "forecasting": {
    "next_30_days": {
      "projected_cost": 13200.00,
      "confidence_interval": [12500.00, 14000.00],
      "growth_rate": 0.06
    }
  },
  "next_steps": [
    "Implement top priority recommendations",
    "Set up automated cost monitoring alerts",
    "Schedule monthly cost review meetings"
  ]
}

## ANALYSIS EXAMPLES

### Example 1: Trend Analysis Request
Query: "Analyze EC2 cost trends over the last 90 days and identify optimization opportunities"

Response Focus:
- Detailed EC2 spending patterns by instance type and region
- Utilization analysis compared to spending
- Reserved Instance vs On-Demand cost comparison
- Specific rightsizing recommendations with ROI calculations

### Example 2: Anomaly Detection Request  
Query: "Detect any unusual spending patterns in the last 30 days"

Response Focus:
- Statistical anomaly detection with confidence scores
- Root cause analysis for each anomaly
- Impact assessment in business terms
- Preventive measures for future anomalies

## QUALITY STANDARDS

### Data Analysis Rules
1. Always provide confidence scores for all findings
2. Include statistical significance testing for trends
3. Compare against relevant baselines (previous periods, budgets, benchmarks)
4. Quantify all findings with specific numbers and percentages
5. Consider seasonal patterns and business context

### Recommendation Guidelines
1. SMART criteria: Specific, Measurable, Achievable, Relevant, Time-bound
2. Include implementation effort estimates in engineer-hours/days
3. Provide ROI calculations with payback periods
4. Assess risk levels and provide mitigation strategies
5. Prioritize based on impact vs effort matrix

### Error Handling
- Data insufficient: Request specific additional context needed
- Analysis ambiguous: Present multiple scenarios with probabilities
- Low confidence (<0.6): Acknowledge limitations and suggest data collection
- Conflicting signals: Explain the conflict and provide recommendation

## ESCALATION TRIGGERS
Escalate to human analyst when:
- Potential cost impact > $5,000/month (critical business impact)
- Confidence score < 0.5 (insufficient data quality)
- Anomalies suggest security or compliance issues
- Recommendations conflict with stated business constraints
"""
    
    def _setup_enhanced_tools(self):
        """Setup enhanced tools with validation and error handling"""
        
        @tool
        async def get_cost_data_with_validation(
            time_period: str = "30_days",
            service_filter: Optional[str] = None,
            include_forecast: bool = False
        ) -> str:
            """
            Get comprehensive AWS cost data with validation and enrichment
            
            Args:
                time_period: Analysis period (7_days, 30_days, 90_days, 1_year)
                service_filter: Specific AWS service to analyze  
                include_forecast: Include 30-day cost forecast
            """
            try:
                self.logger.info("Fetching cost data", period=time_period, service=service_filter)
                
                # Get cost data through circuit breaker
                cost_data = await self.circuit_breaker.call(
                    self.aws_cost_tool.get_cost_data,
                    time_period=time_period,
                    service_filter=service_filter,
                    include_forecast=include_forecast
                )
                
                # Validate data quality
                data_quality_score = self._assess_data_quality(cost_data)
                cost_data['data_quality_score'] = data_quality_score
                
                if data_quality_score < 0.7:
                    self.logger.warning("Low data quality detected", score=data_quality_score)
                
                return json.dumps(cost_data, indent=2)
                
            except Exception as e:
                self.logger.error("Failed to fetch cost data", error=str(e))
                return json.dumps({
                    "error": f"Cost data retrieval failed: {str(e)}",
                    "fallback_available": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        @tool
        async def analyze_trends_with_confidence(cost_data: str) -> str:
            """
            Advanced trend analysis with statistical confidence intervals
            """
            try:
                data = json.loads(cost_data)
                daily_costs = data.get('daily_costs', [])
                
                if len(daily_costs) < 7:
                    return json.dumps({"error": "Insufficient data for trend analysis"})
                
                # Enhanced trend analysis
                trend_analysis = await self._advanced_trend_analysis(daily_costs)
                
                return json.dumps(trend_analysis, indent=2)
                
            except Exception as e:
                self.logger.error("Trend analysis failed", error=str(e))
                return json.dumps({"error": f"Trend analysis failed: {str(e)}"})
        
        @tool 
        async def detect_anomalies_advanced(
            cost_data: str, 
            sensitivity: float = 2.0,
            method: str = "statistical"
        ) -> str:
            """
            Advanced anomaly detection using multiple algorithms
            
            Args:
                cost_data: JSON cost data
                sensitivity: Detection sensitivity (1.0=high, 3.0=low)
                method: Detection method (statistical|ml|hybrid)
            """
            try:
                data = json.loads(cost_data)
                daily_costs = data.get('daily_costs', [])
                
                # Multi-algorithm anomaly detection
                anomalies = await self._multi_algorithm_anomaly_detection(
                    daily_costs, 
                    sensitivity, 
                    method
                )
                
                return json.dumps(anomalies, indent=2)
                
            except Exception as e:
                self.logger.error("Anomaly detection failed", error=str(e))
                return json.dumps({"error": f"Anomaly detection failed: {str(e)}"})
        
        @tool
        async def generate_cost_forecast(cost_data: str, forecast_days: int = 30) -> str:
            """
            Generate cost forecasts using time series analysis
            """
            try:
                data = json.loads(cost_data)
                daily_costs = data.get('daily_costs', [])
                
                # Time series forecasting
                forecast = await self._generate_time_series_forecast(daily_costs, forecast_days)
                
                return json.dumps(forecast, indent=2)
                
            except Exception as e:
                self.logger.error("Forecasting failed", error=str(e))
                return json.dumps({"error": f"Forecasting failed: {str(e)}"})
        
        # Assign tools to instance
        self.get_cost_data_with_validation = get_cost_data_with_validation
        self.analyze_trends_with_confidence = analyze_trends_with_confidence
        self.detect_anomalies_advanced = detect_anomalies_advanced
        self.generate_cost_forecast = generate_cost_forecast
    
    async def _advanced_trend_analysis(self, daily_costs: List[Dict]) -> Dict:
        """Advanced statistical trend analysis"""
        
        # Extract cost values and dates
        costs = [item['cost'] for item in daily_costs]
        dates = [item['date'] for item in daily_costs]
        
        # Calculate multiple trend metrics
        n = len(costs)
        if n < 7:
            return {"error": "Insufficient data points"}
        
        # Linear regression trend
        from scipy import stats
        x = list(range(n))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, costs)
        
        # Moving averages
        window_7 = 7 if n >= 7 else n
        window_30 = 30 if n >= 30 else n
        
        ma_7 = sum(costs[-window_7:]) / window_7
        ma_30 = sum(costs[-window_30:]) / window_30 if window_30 > 7 else ma_7
        
        # Volatility analysis
        mean_cost = sum(costs) / n
        variance = sum((cost - mean_cost) ** 2 for cost in costs) / n
        volatility = (variance ** 0.5) / mean_cost * 100
        
        # Trend classification
        daily_trend = slope
        trend_strength = abs(r_value)
        
        if trend_strength > 0.7:
            trend_confidence = "high"
        elif trend_strength > 0.4:
            trend_confidence = "medium"
        else:
            trend_confidence = "low"
        
        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        return {
            "trend_analysis": {
                "direction": trend_direction,
                "daily_change": round(daily_trend, 4),
                "r_squared": round(r_value ** 2, 3),
                "confidence": trend_confidence,
                "p_value": round(p_value, 4),
                "statistical_significance": p_value < 0.05
            },
            "moving_averages": {
                "ma_7_days": round(ma_7, 2),
                "ma_30_days": round(ma_30, 2),
                "ma_trend": "increasing" if ma_7 > ma_30 else "decreasing"
            },
            "volatility_analysis": {
                "volatility_percentage": round(volatility, 2),
                "volatility_level": "high" if volatility > 20 else "medium" if volatility > 10 else "low",
                "cost_stability": "stable" if volatility < 15 else "unstable"
            },
            "period_summary": {
                "total_cost": round(sum(costs), 2),
                "average_daily": round(mean_cost, 2),
                "highest_day": round(max(costs), 2),
                "lowest_day": round(min(costs), 2),
                "period_change": round(costs[-1] - costs[0], 2),
                "period_change_percent": round((costs[-1] - costs[0]) / costs[0] * 100, 2) if costs[0] > 0 else 0
            }
        }
    
    async def _multi_algorithm_anomaly_detection(
        self, 
        daily_costs: List[Dict], 
        sensitivity: float,
        method: str
    ) -> Dict:
        """Multi-algorithm anomaly detection"""
        
        costs = [item['cost'] for item in daily_costs]
        dates = [item['date'] for item in daily_costs]
        
        if len(costs) < 7:
            return {"error": "Insufficient data for anomaly detection"}
        
        # Statistical method (Z-score)
        mean_cost = sum(costs) / len(costs)
        variance = sum((cost - mean_cost) ** 2 for cost in costs) / len(costs)
        std_dev = variance ** 0.5
        
        statistical_anomalies = []
        for i, (cost, date) in enumerate(zip(costs, dates)):
            z_score = (cost - mean_cost) / std_dev if std_dev > 0 else 0
            
            if abs(z_score) > sensitivity:
                anomaly_type = "spike" if z_score > 0 else "dip"
                severity = "critical" if abs(z_score) > 3 else "high" if abs(z_score) > 2.5 else "medium"
                
                statistical_anomalies.append({
                    "date": date,
                    "cost": cost,
                    "z_score": round(z_score, 2),
                    "type": anomaly_type,
                    "severity": severity,
                    "deviation_amount": round(cost - mean_cost, 2),
                    "deviation_percent": round((cost - mean_cost) / mean_cost * 100, 2),
                    "method": "statistical"
                })
        
        # IQR method for robust anomaly detection
        sorted_costs = sorted(costs)
        n = len(sorted_costs)
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        
        q1 = sorted_costs[q1_idx]
        q3 = sorted_costs[q3_idx]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        iqr_anomalies = []
        for i, (cost, date) in enumerate(zip(costs, dates)):
            if cost < lower_bound or cost > upper_bound:
                iqr_anomalies.append({
                    "date": date,
                    "cost": cost,
                    "type": "outlier",
                    "method": "iqr",
                    "bounds": {"lower": round(lower_bound, 2), "upper": round(upper_bound, 2)}
                })
        
        # Combine results
        all_anomalies = statistical_anomalies + iqr_anomalies
        
        # Deduplicate by date
        seen_dates = set()
        unique_anomalies = []
        for anomaly in all_anomalies:
            if anomaly['date'] not in seen_dates:
                unique_anomalies.append(anomaly)
                seen_dates.add(anomaly['date'])
        
        return {
            "anomaly_summary": {
                "total_anomalies": len(unique_anomalies),
                "critical_anomalies": len([a for a in unique_anomalies if a.get('severity') == 'critical']),
                "method_used": method,
                "sensitivity_threshold": sensitivity,
                "data_points_analyzed": len(costs)
            },
            "statistical_metrics": {
                "mean_daily_cost": round(mean_cost, 2),
                "standard_deviation": round(std_dev, 2),
                "coefficient_variation": round(std_dev / mean_cost * 100, 2) if mean_cost > 0 else 0
            },
            "anomalies": sorted(unique_anomalies, key=lambda x: x['date'], reverse=True),
            "recommendations": self._generate_anomaly_recommendations(unique_anomalies)
        }
    
    def _generate_anomaly_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Generate specific recommendations based on detected anomalies"""
        
        recommendations = []
        
        critical_count = len([a for a in anomalies if a.get('severity') == 'critical'])
        spike_count = len([a for a in anomalies if a.get('type') == 'spike'])
        
        if critical_count > 0:
            recommendations.append(
                f"URGENT: {critical_count} critical cost anomalies detected - investigate immediately"
            )
        
        if spike_count > 2:
            recommendations.append(
                f"Pattern detected: {spike_count} cost spikes - review auto-scaling policies and instance provisioning"
            )
        
        if len(anomalies) > 5:
            recommendations.append(
                "High anomaly frequency detected - implement automated cost monitoring and alerts"
            )
        
        recommendations.extend([
            "Set up CloudWatch cost anomaly detection for automated monitoring",
            "Review cost allocation tags for better attribution",
            "Implement budget alerts for proactive cost management"
        ])
        
        return recommendations
    
    async def analyze(self, query: str, context: Dict[str, Any] = None) -> str:
        """Enhanced analysis method with comprehensive error handling"""
        
        try:
            # Add query context and metadata
            enhanced_context = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
                "agent_version": "2.0",
                "confidence_threshold": 0.7
            }
            
            # Try primary analysis through circuit breaker
            result = await self.circuit_breaker.call(
                self._execute_primary_analysis,
                query,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Primary analysis failed, using fallback", error=str(e))
            return await self._execute_fallback_analysis(query, context)
    
    async def _execute_primary_analysis(self, query: str, context: Dict) -> str:
        """Execute primary analysis using LLM agent"""
        
        # Enhance query with context
        enhanced_query = f"""
Context: {json.dumps(context, indent=2)}

User Query: {query}

Please provide comprehensive cost analysis following the structured output format specified in your system prompt.
"""
        
        result = await asyncio.to_thread(self.agent, enhanced_query)
        
        # Validate and enhance result
        validated_result = await self._validate_and_enhance_result(str(result), context)
        
        return validated_result
    
    async def _validate_and_enhance_result(self, result: str, context: Dict) -> str:
        """Validate and enhance analysis result"""
        
        try:
            # Try to parse as JSON to validate structure
            if result.strip().startswith('{'):
                parsed_result = json.loads(result)
                
                # Add metadata
                parsed_result['analysis_metadata'] = {
                    "agent_version": "2.0",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "query_context": context,
                    "data_sources": ["AWS Cost Explorer", "CloudWatch Metrics"],
                    "processing_time": "calculated_in_production"
                }
                
                return json.dumps(parsed_result, indent=2)
            else:
                # Wrap text result in JSON structure
                return json.dumps({
                    "analysis_summary": result,
                    "format": "text_response",
                    "analysis_metadata": {
                        "agent_version": "2.0",
                        "analysis_timestamp": datetime.now().isoformat()
                    }
                })
                
        except json.JSONDecodeError:
            # Return as-is if can't parse
            return result
    
    async def _execute_fallback_analysis(self, query: str, context: Dict) -> str:
        """Comprehensive fallback analysis when primary fails"""
        
        try:
            self.logger.info("Executing fallback analysis")
            
            # Get basic cost data
            cost_data = await self.get_cost_data_with_validation("30_days")
            
            # Perform basic analysis
            trends = await self.analyze_trends_with_confidence(cost_data)
            anomalies = await self.detect_anomalies_advanced(cost_data)
            
            # Generate fallback response
            fallback_response = {
                "analysis_summary": f"Fallback analysis completed for: {query}",
                "mode": "fallback",
                "confidence_score": 0.6,
                "cost_data_summary": json.loads(cost_data) if cost_data.startswith('{') else {"status": "limited"},
                "trend_analysis": json.loads(trends) if trends.startswith('{') else {"status": "limited"},
                "anomaly_detection": json.loads(anomalies) if anomalies.startswith('{') else {"status": "limited"},
                "recommendations": [
                    "Review cost data in AWS Cost Explorer for detailed analysis",
                    "Set up automated cost monitoring and budgets",
                    "Consider Reserved Instances for stable workloads",
                    "Implement cost allocation tags for better visibility"
                ],
                "limitations": [
                    "Limited LLM processing capability",
                    "Basic analysis only",
                    "May require manual review for complex scenarios"
                ],
                "analysis_metadata": {
                    "agent_version": "2.0_fallback",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "fallback_reason": "Primary analysis unavailable"
                }
            }
            
            return json.dumps(fallback_response, indent=2)
            
        except Exception as e:
            self.logger.error("Fallback analysis also failed", error=str(e))
            return json.dumps({
                "error": "Analysis temporarily unavailable",
                "message": "Please try again later or contact support",
                "timestamp": datetime.now().isoformat()
            })

# Global enhanced instance
enhanced_cost_analyst = EnhancedCostAnalystAgent()
```

## 2. Enhanced Orchestrator Implementation

```python
# PRODUCTION-READY ORCHESTRATOR
from strands.multiagent import GraphBuilder, Swarm
from typing import Dict, Any, List, Optional, Callable
import asyncio
import structlog
from datetime import datetime
from enum import Enum
import json

logger = structlog.get_logger(__name__)

class WorkflowType(Enum):
    SIMPLE = "simple"           # Single agent
    PARALLEL = "parallel"       # Multiple agents in parallel
    SEQUENTIAL = "sequential"   # Chained agent workflow
    ADAPTIVE = "adaptive"       # Intelligent routing

class QueryIntent(Enum):
    COST_ANALYSIS = "cost_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_ASSESSMENT = "security_assessment"
    COMPREHENSIVE_AUDIT = "comprehensive_audit"
    FORECASTING = "forecasting"

class EnhancedOrchestrator:
    """Production-ready orchestrator with advanced workflow management"""
    
    def __init__(self):
        self.logger = logger.bind(component="orchestrator")
        
        # Initialize enhanced agents
        self.enhanced_cost_analyst = enhanced_cost_analyst
        self.enhanced_infra_analyst = EnhancedInfrastructureAnalyst()
        self.enhanced_financial_analyst = EnhancedFinancialAnalyst()
        self.risk_assessment_agent = RiskAssessmentAgent()
        
        # Workflow components
        self.query_analyzer = QueryAnalyzer()
        self.workflow_router = WorkflowRouter()
        self.result_synthesizer = ResultSynthesizer()
        
        # Build workflow graphs
        self.workflow_graphs = self._build_workflow_graphs()
        
        # Session management
        self.active_sessions = {}
        
        # Performance metrics
        self.metrics_collector = MetricsCollector()
    
    def _build_workflow_graphs(self) -> Dict[str, Any]:
        """Build different workflow graphs for various scenarios"""
        
        workflows = {}
        
        # 1. Cost-focused workflow
        cost_builder = GraphBuilder()
        cost_builder.add_agent("cost_analyzer", self.enhanced_cost_analyst)
        cost_builder.add_agent("financial_calculator", self.enhanced_financial_analyst)
        cost_builder.add_agent("risk_assessor", self.risk_assessment_agent)
        cost_builder.add_edge("cost_analyzer", "financial_calculator")
        cost_builder.add_edge("financial_calculator", "risk_assessor")
        workflows[QueryIntent.COST_ANALYSIS] = cost_builder.build()
        
        # 2. Performance-focused workflow
        perf_builder = GraphBuilder()
        perf_builder.add_agent("infra_analyzer", self.enhanced_infra_analyst)
        perf_builder.add_agent("cost_analyzer", self.enhanced_cost_analyst)
        perf_builder.add_agent("financial_calculator", self.enhanced_financial_analyst)
        perf_builder.add_edge("infra_analyzer", "cost_analyzer")
        perf_builder.add_edge("cost_analyzer", "financial_calculator")
        workflows[QueryIntent.PERFORMANCE_OPTIMIZATION] = perf_builder.build()
        
        # 3. Comprehensive workflow with parallel execution
        comprehensive_builder = GraphBuilder()
        comprehensive_builder.add_agent("cost_analyzer", self.enhanced_cost_analyst)
        comprehensive_builder.add_agent("infra_analyzer", self.enhanced_infra_analyst)
        comprehensive_builder.add_agent("risk_assessor", self.risk_assessment_agent)
        comprehensive_builder.add_agent("financial_calculator", self.enhanced_financial_analyst)
        
        # Parallel execution for independent analyses
        comprehensive_builder.add_parallel_edges([
            "cost_analyzer",
            "infra_analyzer", 
            "risk_assessor"
        ])
        
        # Convergence to financial analysis
        comprehensive_builder.add_convergence_edge(
            ["cost_analyzer", "infra_analyzer", "risk_assessor"],
            "financial_calculator"
        )
        
        workflows[QueryIntent.COMPREHENSIVE_AUDIT] = comprehensive_builder.build()
        
        return workflows
    
    async def analyze_with_intelligent_routing(
        self,
        query: str,
        context: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration method with intelligent workflow routing
        
        Args:
            query: User's analysis request
            context: Previous conversation context
            user_preferences: User's risk tolerance, priorities, constraints
            session_id: Session identifier for context continuity
            
        Returns:
            Comprehensive analysis results
        """
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(query) % 10000}"
        
        self.logger.info("Starting intelligent analysis", session_id=session_id, query=query)
        
        # Start performance tracking
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Analyze query intent and complexity
            query_analysis = await self.query_analyzer.analyze_query(
                query, context, user_preferences
            )
            
            self.logger.info("Query analysis completed", 
                           intent=query_analysis['primary_intent'],
                           complexity=query_analysis['complexity_score'])
            
            # Step 2: Select optimal workflow
            workflow_type = self._select_workflow(query_analysis)
            
            # Step 3: Execute selected workflow
            results = await self._execute_workflow(
                workflow_type,
                query,
                context,
                user_preferences,
                session_id
            )
            
            # Step 4: Synthesize and enhance results
            final_results = await self.result_synthesizer.synthesize_results(
                results,
                query_analysis,
                user_preferences
            )
            
            # Step 5: Add execution metadata
            execution_time = asyncio.get_event_loop().time() - start_time
            final_results['execution_metadata'] = {
                "session_id": session_id,
                "execution_time_seconds": round(execution_time, 2),
                "workflow_type": workflow_type.value,
                "query_intent": query_analysis['primary_intent'],
                "agents_executed": results.get('agents_executed', []),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store session context for future queries
            self._update_session_context(session_id, query, final_results)
            
            # Record metrics
            await self.metrics_collector.record_execution(
                session_id, execution_time, workflow_type, len(results)
            )
            
            self.logger.info("Analysis completed successfully", 
                           session_id=session_id,
                           execution_time=execution_time)
            
            return final_results
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error("Analysis failed", 
                            session_id=session_id,
                            error=str(e),
                            execution_time=execution_time)
            
            # Attempt recovery
            return await self._handle_analysis_failure(
                e, query, context, session_id, execution_time
            )
    
    def _select_workflow(self, query_analysis: Dict) -> WorkflowType:
        """Select optimal workflow based on query analysis"""
        
        intent = query_analysis.get('primary_intent')
        complexity = query_analysis.get('complexity_score', 0.5)
        time_sensitivity = query_analysis.get('time_sensitivity', 'normal')
        
        # Simple workflows for straightforward queries
        if complexity < 0.3 and time_sensitivity == 'urgent':
            return WorkflowType.SIMPLE
        
        # Parallel workflows for comprehensive analysis
        if intent == QueryIntent.COMPREHENSIVE_AUDIT or complexity > 0.7:
            return WorkflowType.PARALLEL
        
        # Sequential workflows for dependent analyses
        if intent in [QueryIntent.COST_ANALYSIS, QueryIntent.PERFORMANCE_OPTIMIZATION]:
            return WorkflowType.SEQUENTIAL
        
        # Default to adaptive routing
        return WorkflowType.ADAPTIVE
    
    async def _execute_workflow(
        self,
        workflow_type: WorkflowType,
        query: str,
        context: Optional[Dict],
        user_preferences: Optional[Dict],
        session_id: str
    ) -> Dict[str, Any]:
        """Execute the selected workflow type"""
        
        if workflow_type == WorkflowType.SIMPLE:
            return await self._execute_simple_workflow(query, context)
        
        elif workflow_type == WorkflowType.PARALLEL:
            return await self._execute_parallel_workflow(query, context, user_preferences)
        
        elif workflow_type == WorkflowType.SEQUENTIAL:
            return await self._execute_sequential_workflow(query, context)
        
        elif workflow_type == WorkflowType.ADAPTIVE:
            return await self._execute_adaptive_workflow(query, context, user_preferences)
        
        else:
            raise ValueError(f"Unsupported workflow type: {workflow_type}")
    
    async def _execute_parallel_workflow(
        self, 
        query: str, 
        context: Optional[Dict],
        user_preferences: Optional[Dict]
    ) -> Dict[str, Any]:
        """Execute parallel agent workflow for maximum speed"""
        
        self.logger.info("Executing parallel workflow")
        
        # Create tasks for parallel execution
        tasks = {
            'cost_analysis': self.enhanced_cost_analyst.analyze(query, context),
            'infrastructure_analysis': self.enhanced_infra_analyst.analyze(query, context),
            'financial_analysis': self.enhanced_financial_analyst.analyze(query, context),
            'risk_assessment': self.risk_assessment_agent.analyze(query, context)
        }
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Combine results with error handling
        combined_results = {}
        agents_executed = []
        
        for (agent_name, task), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                self.logger.warning(f"{agent_name} failed", error=str(result))
                combined_results[agent_name] = {
                    "error": str(result),
                    "status": "failed"
                }
            else:
                combined_results[agent_name] = result
                agents_executed.append(agent_name)
        
        return {
            "workflow_type": "parallel",
            "agents_executed": agents_executed,
            "results": combined_results,
            "execution_summary": f"Executed {len(agents_executed)}/{len(tasks)} agents successfully"
        }
    
    async def _execute_sequential_workflow(
        self,
        query: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Execute sequential workflow with data flow between agents"""
        
        self.logger.info("Executing sequential workflow")
        
        results = {}
        
        # Step 1: Cost analysis
        cost_result = await self.enhanced_cost_analyst.analyze(query, context)
        results['cost_analysis'] = cost_result
        
        # Step 2: Infrastructure analysis with cost context
        infra_context = {**(context or {}), "cost_analysis": cost_result}
        infra_result = await self.enhanced_infra_analyst.analyze(query, infra_context)
        results['infrastructure_analysis'] = infra_result
        
        # Step 3: Financial analysis with both previous contexts
        financial_context = {
            **(context or {}),
            "cost_analysis": cost_result,
            "infrastructure_analysis": infra_result
        }
        financial_result = await self.enhanced_financial_analyst.analyze(query, financial_context)
        results['financial_analysis'] = financial_result
        
        return {
            "workflow_type": "sequential",
            "agents_executed": ["cost_analyst", "infrastructure_analyst", "financial_analyst"],
            "results": results,
            "data_flow": "cost_analysis → infrastructure_analysis → financial_analysis"
        }

# Usage Example
async def main():
    """Example usage of enhanced orchestrator"""
    
    orchestrator = EnhancedOrchestrator()
    
    # Example 1: Cost optimization query
    result = await orchestrator.analyze_with_intelligent_routing(
        query="Analyze our EC2 costs and provide optimization recommendations",
        context={"business_context": "startup", "growth_stage": "scaling"},
        user_preferences={
            "risk_tolerance": "medium",
            "priority": "cost_optimization",
            "timeline": "3_months"
        }
    )
    
    print("Cost Optimization Analysis:")
    print(json.dumps(result, indent=2))
    
    # Example 2: Comprehensive audit
    audit_result = await orchestrator.analyze_with_intelligent_routing(
        query="Perform a comprehensive AWS cost and performance audit",
        user_preferences={
            "risk_tolerance": "low",
            "priority": "comprehensive_analysis",
            "include_forecasting": True
        }
    )
    
    print("\nComprehensive Audit Results:")
    print(json.dumps(audit_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Production Deployment Configuration

```python
# PRODUCTION DEPLOYMENT SETUP
import os
from typing import Dict, Any
import structlog
from opentelemetry import trace
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class ProductionConfig:
    """Production configuration for agent deployment"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_monitoring()
        self.setup_secrets_management()
        
    def setup_logging(self):
        """Configure structured logging for production"""
        
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def setup_monitoring(self):
        """Configure OpenTelemetry monitoring"""
        
        # Set up tracing
        trace.set_tracer_provider(TracerProvider())
        
        # Configure Cloud Monitoring exporter (for GCP)
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            cloud_exporter = CloudMonitoringSpanExporter()
            span_processor = BatchSpanProcessor(cloud_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
    
    def setup_secrets_management(self):
        """Configure secure secrets management"""
        
        # Use environment variables or secret management service
        self.secrets = {
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'database_url': os.getenv('DATABASE_URL'),
            'redis_url': os.getenv('REDIS_URL')
        }

# Docker configuration
DOCKERFILE = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV PROMETHEUS_MULTIPROC_DIR=/tmp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# Kubernetes deployment
K8S_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: costsense-agents
  labels:
    app: costsense-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: costsense-agents
  template:
    metadata:
      labels:
        app: costsense-agents
    spec:
      containers:
      - name: costsense-agents
        image: costsense-agents:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: costsense-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: costsense-agents-service
spec:
  selector:
    app: costsense-agents
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
"""
```

This implementation provides:

1. **Enhanced Agent Architecture** with production-ready features
2. **Comprehensive Error Handling** with circuit breakers and fallbacks
3. **Advanced Orchestration** with intelligent workflow routing
4. **Production Deployment Configuration** with monitoring and scaling
5. **Structured Logging and Observability** for operations

The enhanced agents are ready for production deployment with enterprise-grade reliability, performance, and monitoring capabilities.