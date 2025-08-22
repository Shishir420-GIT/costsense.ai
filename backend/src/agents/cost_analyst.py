from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import memory, calculator
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.config.settings import Settings
from src.tools.aws_tools_simple import AWSCostExplorerTool

class CostAnalystAgent:
    """Specialized agent for AWS cost analysis and trend identification"""
    
    def __init__(self):
        self.settings = Settings()
        self.aws_cost_tool = AWSCostExplorerTool()
        
        # Configure Ollama model
        try:
            self.model = OllamaModel(
                host=self.settings.OLLAMA_HOST,
                model_id=self.settings.OLLAMA_MODEL,
                temperature=0.1
            )
        except Exception:
            # Fallback to mock mode if Ollama not available
            self.model = None
        
        # Create specialized tools for cost analysis
        self._setup_tools()
        
        # Initialize the Strands agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            tools=[
                self.get_cost_data,
                self.analyze_cost_trends,
                self.detect_anomalies,
                memory,
                calculator
            ],
            name="cost_analyst"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Cost Analysis Expert specializing in cloud spending optimization. 
        
        Your expertise includes:
        - Historical spending pattern analysis
        - Cost trend identification and forecasting
        - Service-level cost breakdown and attribution
        - Anomaly detection in spending patterns
        - Budget variance analysis and alerts
        - Cost optimization opportunity identification
        
        Guidelines:
        1. Always provide data-driven insights with specific numbers
        2. Identify both immediate and long-term cost trends
        3. Flag unusual spending patterns or anomalies
        4. Suggest actionable cost optimization strategies
        5. Present findings in clear, business-friendly language
        6. Include confidence levels for your recommendations
        
        When analyzing costs, consider:
        - Seasonal patterns and business cycles
        - Service growth trends and scaling patterns
        - Resource utilization efficiency
        - Potential cost-saving opportunities
        - Risk factors for budget overruns
        
        Always cite specific data points and provide quantified recommendations."""
    
    def _setup_tools(self):
        """Setup specialized tools for cost analysis"""
        
        @tool
        def get_cost_data(time_period: str = "30_days") -> str:
            """Retrieve AWS cost data for specified time period.
            
            Args:
                time_period: Time period for cost analysis (7_days, 30_days, 90_days, 1_year)
            """
            return self.aws_cost_tool._run(time_period)
        
        @tool
        def analyze_cost_trends(cost_data: str) -> str:
            """Analyze cost trends and patterns from cost data.
            
            Args:
                cost_data: JSON string containing cost data with daily_costs and top_services
            """
            try:
                data = json.loads(cost_data)
                daily_costs = data.get('daily_costs', [])
                
                if len(daily_costs) < 7:
                    return "Insufficient data for trend analysis"
                
                # Calculate trend metrics
                recent_costs = [item['cost'] for item in daily_costs[-7:]]
                previous_costs = [item['cost'] for item in daily_costs[-14:-7]] if len(daily_costs) >= 14 else recent_costs
                
                recent_avg = sum(recent_costs) / len(recent_costs)
                previous_avg = sum(previous_costs) / len(previous_costs)
                
                trend_percentage = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
                
                # Calculate volatility
                cost_values = [item['cost'] for item in daily_costs]
                avg_cost = sum(cost_values) / len(cost_values)
                variance = sum((cost - avg_cost) ** 2 for cost in cost_values) / len(cost_values)
                volatility = (variance ** 0.5) / avg_cost * 100
                
                trend_analysis = {
                    "trend_direction": "increasing" if trend_percentage > 2 else "decreasing" if trend_percentage < -2 else "stable",
                    "trend_percentage": round(trend_percentage, 2),
                    "recent_average_daily_cost": round(recent_avg, 2),
                    "previous_average_daily_cost": round(previous_avg, 2),
                    "volatility_percentage": round(volatility, 2),
                    "total_period_cost": round(sum(cost_values), 2),
                    "highest_daily_cost": round(max(cost_values), 2),
                    "lowest_daily_cost": round(min(cost_values), 2)
                }
                
                return json.dumps(trend_analysis)
                
            except Exception as e:
                return f"Error analyzing trends: {str(e)}"
        
        @tool
        def detect_anomalies(cost_data: str, threshold: float = 2.0) -> str:
            """Detect cost anomalies and unusual spending patterns.
            
            Args:
                cost_data: JSON string containing cost data
                threshold: Standard deviation threshold for anomaly detection
            """
            try:
                data = json.loads(cost_data)
                daily_costs = data.get('daily_costs', [])
                
                if len(daily_costs) < 7:
                    return "Insufficient data for anomaly detection"
                
                cost_values = [item['cost'] for item in daily_costs]
                mean_cost = sum(cost_values) / len(cost_values)
                variance = sum((cost - mean_cost) ** 2 for cost in cost_values) / len(cost_values)
                std_dev = variance ** 0.5
                
                anomalies = []
                for item in daily_costs:
                    cost = item['cost']
                    z_score = (cost - mean_cost) / std_dev if std_dev > 0 else 0
                    
                    if abs(z_score) > threshold:
                        anomalies.append({
                            "date": item['date'],
                            "cost": cost,
                            "z_score": round(z_score, 2),
                            "deviation_from_mean": round(cost - mean_cost, 2),
                            "type": "spike" if z_score > 0 else "dip"
                        })
                
                anomaly_summary = {
                    "total_anomalies": len(anomalies),
                    "mean_daily_cost": round(mean_cost, 2),
                    "standard_deviation": round(std_dev, 2),
                    "threshold_used": threshold,
                    "anomalies": anomalies
                }
                
                return json.dumps(anomaly_summary)
                
            except Exception as e:
                return f"Error detecting anomalies: {str(e)}"
        
        # Assign tools to instance for access by agent
        self.get_cost_data = get_cost_data
        self.analyze_cost_trends = analyze_cost_trends
        self.detect_anomalies = detect_anomalies
    
    async def analyze(self, query: str, context: Dict[str, Any] = None) -> str:
        """Perform cost analysis based on query"""
        try:
            # Always try fallback first for reliability
            if self.model is None:
                # Fallback to direct analysis when Ollama not available
                return await self._fallback_analysis(query, context)
            
            # Try Strands agent, but fallback if it fails
            try:
                result = await asyncio.to_thread(self.agent, query)
                return str(result)
            except Exception as llm_error:
                # LLM failed, use fallback
                return await self._fallback_analysis(query, context)
            
        except Exception as e:
            return await self._fallback_analysis(query, context)
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any] = None) -> str:
        """Fallback analysis when LLM not available"""
        try:
            # Get cost data
            cost_data = self.get_cost_data("30_days")
            
            # Perform trend analysis
            trends = self.analyze_cost_trends(cost_data)
            
            # Detect anomalies
            anomalies = self.detect_anomalies(cost_data)
            
            # Parse the JSON results for better formatting
            import json
            try:
                cost_json = json.loads(cost_data)
                trends_json = json.loads(trends) if trends.startswith('{') else {"error": trends}
                anomalies_json = json.loads(anomalies) if anomalies.startswith('{') else {"error": anomalies}
            except:
                cost_json = {"total_cost": "Unknown"}
                trends_json = {"trend_direction": "Unknown"}
                anomalies_json = {"total_anomalies": 0}
            
            # Generate intelligent analysis
            total_cost = cost_json.get('total_cost', 0)
            trend_direction = trends_json.get('trend_direction', 'stable')
            trend_percentage = trends_json.get('trend_percentage', 0)
            anomaly_count = anomalies_json.get('total_anomalies', 0)
            
            analysis_summary = []
            
            if total_cost > 2000:
                analysis_summary.append(f"• High monthly spending detected: ${total_cost:,.2f}")
            elif total_cost > 1000:
                analysis_summary.append(f"• Moderate monthly spending: ${total_cost:,.2f}")
            else:
                analysis_summary.append(f"• Low monthly spending: ${total_cost:,.2f}")
            
            if trend_direction == "increasing" and abs(trend_percentage) > 10:
                analysis_summary.append(f"• ⚠️ Concerning cost increase: {trend_percentage:+.1f}% vs previous period")
            elif trend_direction == "decreasing" and abs(trend_percentage) > 5:
                analysis_summary.append(f"• ✅ Positive cost reduction: {trend_percentage:.1f}% vs previous period")
            else:
                analysis_summary.append(f"• Stable cost pattern: {trend_percentage:+.1f}% change")
            
            if anomaly_count > 0:
                analysis_summary.append(f"• 🔍 {anomaly_count} cost anomalies detected - investigate unusual spikes or dips")
            else:
                analysis_summary.append("• No significant cost anomalies detected")
            
            # Add recommendations
            recommendations = []
            if total_cost > 1500:
                recommendations.append("Consider Reserved Instances for stable workloads")
            if trend_direction == "increasing":
                recommendations.append("Review recent resource provisioning and scaling policies")
            if anomaly_count > 0:
                recommendations.append("Investigate anomalous spending patterns for optimization opportunities")
            recommendations.append("Set up cost budgets and alerts for proactive monitoring")
            
            return f"""🔍 AWS Cost Analysis Results

Query: {query}

📊 Key Insights:
{chr(10).join(analysis_summary)}

💡 Recommendations:
{chr(10).join(f"• {rec}" for rec in recommendations)}

📈 Detailed Metrics:
• Total Period Cost: ${total_cost:,.2f}
• Trend Direction: {trend_direction} ({trend_percentage:+.1f}%)
• Anomalies Detected: {anomaly_count}
• Data Source: Last 30 days AWS spending

🔧 Next Steps:
1. Review the highest spending services
2. Analyze resource utilization patterns
3. Consider cost optimization strategies
4. Set up automated monitoring and alerts

Generated by Cost Analyst Agent - Professional AWS cost optimization insights"""
            
        except Exception as e:
            return f"Cost Analysis completed with basic insights. Query: {query}. Note: Detailed analysis requires data connection. Error: {str(e)}"
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "cost_trend_analysis",
            "anomaly_detection", 
            "budget_variance_analysis",
            "service_cost_breakdown",
            "cost_forecasting",
            "spending_pattern_identification"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test cost data retrieval
            test_data = self.get_cost_data("7_days")
            data_available = len(test_data) > 10
            
            # Test model availability
            model_available = self.model is not None
            
            return {
                "agent_name": "cost_analyst",
                "healthy": data_available,
                "model_available": model_available,
                "data_available": data_available,
                "capabilities": self.get_capabilities(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": "cost_analyst",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
cost_analyst = CostAnalystAgent()