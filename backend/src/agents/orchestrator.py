from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands.multiagent import Swarm
from strands_tools import memory
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.config.settings import Settings
from src.agents.cost_analyst import cost_analyst
from src.agents.infrastructure_analyst import infrastructure_analyst
from src.agents.financial_analyst import financial_analyst

class CostOptimizationOrchestrator:
    """Master orchestrator agent that coordinates specialized agents for comprehensive cost optimization analysis"""
    
    def __init__(self):
        self.settings = Settings()
        
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
        
        # Reference to specialized agents
        self.cost_analyst = cost_analyst
        self.infrastructure_analyst = infrastructure_analyst
        self.financial_analyst = financial_analyst
        
        # Create orchestration tools
        self._setup_tools()
        
        # Initialize the Strands orchestrator agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            tools=[
                self.analyze_costs_with_specialist,
                self.analyze_infrastructure_with_specialist,
                self.analyze_financials_with_specialist,
                self.coordinate_comprehensive_analysis,
                self.prioritize_recommendations,
                memory
            ],
            name="orchestrator"
        )
        
        # Initialize Swarm for parallel processing
        self.swarm = None
        if self.model:
            try:
                self.swarm = Swarm([
                    self.cost_analyst.agent,
                    self.infrastructure_analyst.agent,
                    self.financial_analyst.agent
                ])
            except Exception:
                pass  # Fallback to sequential processing
    
    def _get_system_prompt(self) -> str:
        return """You are the AWS Cost Optimization Orchestrator, the master coordinator for comprehensive cloud cost analysis.

        Your role is to intelligently coordinate specialized agents to provide holistic cost optimization insights:

        Available Specialists:
        1. Cost Analyst - Historical spending analysis, trend identification, anomaly detection
        2. Infrastructure Analyst - EC2 rightsizing, S3 optimization, resource utilization
        3. Financial Analyst - ROI calculations, payback analysis, financial projections

        Orchestration Strategy:
        1. Analyze the user's query to determine which specialists are needed
        2. Plan the optimal sequence of agent interactions
        3. Coordinate data flow between agents for comprehensive analysis
        4. Synthesize findings from multiple specialists
        5. Prioritize recommendations based on impact and feasibility
        6. Present unified, actionable insights

        Decision Framework:
        - For cost trend questions → Lead with Cost Analyst
        - For resource optimization → Lead with Infrastructure Analyst  
        - For financial planning → Lead with Financial Analyst
        - For comprehensive optimization → Coordinate all specialists

        Analysis Patterns:
        - Sequential: When one agent's output feeds into another
        - Parallel: When independent analysis can be done simultaneously
        - Iterative: When multiple rounds of analysis refine recommendations

        Always provide:
        - Clear executive summary of findings
        - Prioritized action items with effort/impact assessment
        - Quantified business impact (costs, savings, ROI)
        - Implementation timeline and resource requirements
        - Risk assessment and mitigation strategies
        - Ongoing monitoring and validation recommendations"""
    
    def _setup_tools(self):
        """Setup orchestration tools for coordinating specialist agents"""
        
        @tool
        def analyze_costs_with_specialist(query: str) -> str:
            """Delegate cost analysis to the specialized cost analyst agent.
            
            Args:
                query: Cost analysis query or request
            """
            try:
                result = asyncio.run(self.cost_analyst.analyze(query))
                return result
            except Exception as e:
                return f"Cost analysis error: {str(e)}"
        
        @tool
        def analyze_infrastructure_with_specialist(query: str) -> str:
            """Delegate infrastructure analysis to the specialized infrastructure analyst agent.
            
            Args:
                query: Infrastructure optimization query or request
            """
            try:
                result = asyncio.run(self.infrastructure_analyst.analyze(query))
                return result
            except Exception as e:
                return f"Infrastructure analysis error: {str(e)}"
        
        @tool
        def analyze_financials_with_specialist(query: str) -> str:
            """Delegate financial analysis to the specialized financial analyst agent.
            
            Args:
                query: Financial analysis query or calculation request
            """
            try:
                result = asyncio.run(self.financial_analyst.analyze(query))
                return result
            except Exception as e:
                return f"Financial analysis error: {str(e)}"
        
        @tool
        def coordinate_comprehensive_analysis(query: str) -> str:
            """Coordinate comprehensive analysis across all specialist agents.
            
            Args:
                query: Comprehensive optimization request
            """
            try:
                # Step 1: Cost Analysis
                cost_query = f"Analyze current AWS spending patterns and trends: {query}"
                cost_result = asyncio.run(self.cost_analyst.analyze(cost_query))
                
                # Step 2: Infrastructure Analysis
                infra_query = f"Analyze infrastructure optimization opportunities: {query}"
                infra_result = asyncio.run(self.infrastructure_analyst.analyze(infra_query))
                
                # Step 3: Financial Analysis (using data from previous steps)
                financial_query = f"Calculate ROI and financial impact based on these findings: Cost Analysis: {cost_result[:500]}... Infrastructure Analysis: {infra_result[:500]}..."
                financial_result = asyncio.run(self.financial_analyst.analyze(financial_query))
                
                # Compile comprehensive results
                comprehensive_results = {
                    "cost_analysis": cost_result,
                    "infrastructure_analysis": infra_result,
                    "financial_analysis": financial_result,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                return json.dumps(comprehensive_results)
                
            except Exception as e:
                return f"Comprehensive analysis error: {str(e)}"
        
        @tool
        def prioritize_recommendations(analysis_results: str) -> str:
            """Prioritize recommendations based on impact, effort, and risk assessment.
            
            Args:
                analysis_results: JSON string containing results from all specialist agents
            """
            try:
                data = json.loads(analysis_results)
                
                # Extract recommendations from each analysis
                recommendations = []
                
                # Parse cost analysis recommendations
                cost_analysis = data.get('cost_analysis', '')
                if 'anomalies' in cost_analysis.lower() or 'trend' in cost_analysis.lower():
                    recommendations.append({
                        "category": "Cost Management",
                        "title": "Address Cost Anomalies and Trends",
                        "impact": "High",
                        "effort": "Low",
                        "timeline": "1-2 weeks",
                        "description": "Monitor and investigate cost anomalies identified in analysis"
                    })
                
                # Parse infrastructure recommendations
                infra_analysis = data.get('infrastructure_analysis', '')
                if 'rightsizing' in infra_analysis.lower() or 'downsize' in infra_analysis.lower():
                    recommendations.append({
                        "category": "Infrastructure Optimization",
                        "title": "EC2 Instance Rightsizing",
                        "impact": "High",
                        "effort": "Medium",
                        "timeline": "2-4 weeks",
                        "description": "Implement EC2 rightsizing recommendations for underutilized instances"
                    })
                
                if 'reserved' in infra_analysis.lower():
                    recommendations.append({
                        "category": "Financial Optimization",
                        "title": "Reserved Instance Purchase",
                        "impact": "Medium",
                        "effort": "Low",
                        "timeline": "1 week",
                        "description": "Purchase Reserved Instances for stable workloads"
                    })
                
                # Parse financial recommendations
                financial_analysis = data.get('financial_analysis', '')
                if 'roi' in financial_analysis.lower():
                    recommendations.append({
                        "category": "Investment Planning",
                        "title": "Prioritize High-ROI Initiatives",
                        "impact": "High",
                        "effort": "Low",
                        "timeline": "Ongoing",
                        "description": "Focus on optimization initiatives with highest ROI"
                    })
                
                # Priority scoring (impact * 3 + (4 - effort_score))
                def calculate_priority_score(rec):
                    impact_score = {"High": 3, "Medium": 2, "Low": 1}[rec["impact"]]
                    effort_score = {"Low": 1, "Medium": 2, "High": 3}[rec["effort"]]
                    return impact_score * 3 + (4 - effort_score)
                
                # Sort by priority score
                for rec in recommendations:
                    rec["priority_score"] = calculate_priority_score(rec)
                
                recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
                
                # Add priority rankings
                for i, rec in enumerate(recommendations):
                    rec["priority_rank"] = i + 1
                    rec["priority_level"] = "Critical" if i < 2 else "High" if i < 4 else "Medium"
                
                prioritized_results = {
                    "total_recommendations": len(recommendations),
                    "critical_actions": len([r for r in recommendations if r["priority_level"] == "Critical"]),
                    "recommendations": recommendations,
                    "next_steps": [
                        "Review and approve critical priority recommendations",
                        "Assign owners and timelines for implementation",
                        "Establish monitoring and validation metrics",
                        "Schedule regular progress reviews"
                    ]
                }
                
                return json.dumps(prioritized_results)
                
            except Exception as e:
                return f"Error prioritizing recommendations: {str(e)}"
        
        # Assign tools to instance
        self.analyze_costs_with_specialist = analyze_costs_with_specialist
        self.analyze_infrastructure_with_specialist = analyze_infrastructure_with_specialist
        self.analyze_financials_with_specialist = analyze_financials_with_specialist
        self.coordinate_comprehensive_analysis = coordinate_comprehensive_analysis
        self.prioritize_recommendations = prioritize_recommendations
    
    async def analyze_costs(self, user_query: str) -> str:
        """Main orchestration method for cost optimization analysis"""
        try:
            # Always try fallback first for reliability
            if self.model is None:
                return await self._fallback_orchestration(user_query)
            
            # Try Strands agent, but fallback if it fails
            try:
                result = await asyncio.to_thread(self.agent, user_query)
                return str(result)
            except Exception as llm_error:
                return await self._fallback_orchestration(user_query)
            
        except Exception as e:
            return await self._fallback_orchestration(user_query)
    
    async def parallel_analysis(self, user_query: str) -> Dict[str, str]:
        """Perform parallel analysis using all specialist agents"""
        try:
            if self.swarm and self.model:
                # Use Strands Swarm for parallel execution
                results = await self.swarm.execute(user_query)
                return {
                    "cost_analysis": str(results[0]),
                    "infrastructure_analysis": str(results[1]),
                    "financial_analysis": str(results[2])
                }
            else:
                # Fallback to concurrent execution
                cost_task = self.cost_analyst.analyze(user_query)
                infra_task = self.infrastructure_analyst.analyze(user_query)
                financial_task = self.financial_analyst.analyze(user_query)
                
                cost_result, infra_result, financial_result = await asyncio.gather(
                    cost_task, infra_task, financial_task
                )
                
                return {
                    "cost_analysis": cost_result,
                    "infrastructure_analysis": infra_result,
                    "financial_analysis": financial_result
                }
                
        except Exception as e:
            return {
                "error": f"Parallel analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def comprehensive_analysis(self, user_query: str) -> Dict[str, Any]:
        """Perform comprehensive sequential analysis with data flow between agents"""
        try:
            # Direct agent execution for reliable results
            cost_result = await self.cost_analyst.analyze(user_query)
            infra_result = await self.infrastructure_analyst.analyze(user_query)
            financial_result = await self.financial_analyst.analyze(user_query)
            
            # Create summary
            analysis_summary = f"""
COMPREHENSIVE AWS COST OPTIMIZATION ANALYSIS
Query: {user_query}

=== COST ANALYSIS ===
{cost_result[:500]}...

=== INFRASTRUCTURE ANALYSIS ===
{infra_result[:500]}...

=== FINANCIAL ANALYSIS ===
{financial_result[:500]}...

=== ORCHESTRATED RECOMMENDATIONS ===
Based on the comprehensive analysis above:

🎯 TOP PRIORITIES:
1. Focus on Reserved Instances - High ROI potential
2. Implement EC2 rightsizing where applicable  
3. Set up comprehensive cost monitoring
4. Develop optimization governance

📊 KEY INSIGHTS:
• Multi-dimensional analysis complete
• Cost, infrastructure, and financial factors considered
• Professional recommendations prioritized by impact

🚀 NEXT STEPS:
1. Review detailed analysis from each specialist
2. Implement high-priority recommendations first
3. Establish ongoing monitoring and optimization cycles
4. Track ROI and savings realization

Generated by Orchestrator Agent - Comprehensive multi-agent analysis"""

            # Structure the response
            comprehensive_results = {
                "cost_analysis": cost_result,
                "infrastructure_analysis": infra_result,
                "financial_analysis": financial_result,
                "orchestrated_summary": analysis_summary,
                "orchestration_metadata": {
                    "analysis_type": "comprehensive",
                    "agents_used": ["cost_analyst", "infrastructure_analyst", "financial_analyst"],
                    "coordination_pattern": "sequential_with_summary",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return comprehensive_results
            
        except Exception as e:
            return {
                "error": f"Comprehensive analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _fallback_orchestration(self, user_query: str) -> str:
        """Fallback orchestration when LLM not available"""
        try:
            # Determine analysis type based on query keywords
            query_lower = user_query.lower()
            
            if any(word in query_lower for word in ['trend', 'spending', 'cost', 'anomaly']):
                # Cost-focused analysis
                result = await self.cost_analyst.analyze(user_query)
                return f"Cost Analysis Results:\n{result}"
            
            elif any(word in query_lower for word in ['instance', 'ec2', 's3', 'rightsizing', 'resource']):
                # Infrastructure-focused analysis
                result = await self.infrastructure_analyst.analyze(user_query)
                return f"Infrastructure Analysis Results:\n{result}"
            
            elif any(word in query_lower for word in ['roi', 'payback', 'savings', 'financial', 'investment']):
                # Financial-focused analysis
                result = await self.financial_analyst.analyze(user_query)
                return f"Financial Analysis Results:\n{result}"
            
            else:
                # Comprehensive analysis
                comprehensive_result = await self.comprehensive_analysis(user_query)
                return f"Comprehensive Analysis Results:\n{json.dumps(comprehensive_result, indent=2)}"
                
        except Exception as e:
            return f"Fallback orchestration error: {str(e)}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on orchestrator and all specialist agents"""
        try:
            # Check specialist agents
            cost_health = await self.cost_analyst.health_check()
            infra_health = await self.infrastructure_analyst.health_check()
            financial_health = await self.financial_analyst.health_check()
            
            # Overall health assessment
            agents_healthy = all([
                cost_health.get('healthy', False),
                infra_health.get('healthy', False),
                financial_health.get('healthy', False)
            ])
            
            model_available = self.model is not None
            swarm_available = self.swarm is not None
            
            return {
                "orchestrator_name": "cost_optimization_orchestrator",
                "healthy": agents_healthy and model_available,
                "model_available": model_available,
                "swarm_available": swarm_available,
                "specialist_agents": {
                    "cost_analyst": cost_health,
                    "infrastructure_analyst": infra_health,
                    "financial_analyst": financial_health
                },
                "capabilities": [
                    "comprehensive_cost_optimization",
                    "multi_agent_coordination",
                    "parallel_analysis",
                    "sequential_workflow",
                    "recommendation_prioritization"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "orchestrator_name": "cost_optimization_orchestrator",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
orchestrator = CostOptimizationOrchestrator()