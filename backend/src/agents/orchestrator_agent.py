from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands.multiagent import GraphBuilder, Swarm
from strands_tools import calculator, memory
import asyncio
from typing import Dict, Any, List
import json

from src.config.settings import Settings
from src.tools.aws_tools import AWSCostExplorerTool, EC2UtilizationTool, S3OptimizationTool
from src.tools.calculation_tools import SavingsCalculationTool

class CostOptimizationOrchestrator:
    def __init__(self):
        self.settings = Settings()
        
        # Configure Ollama model
        self.ollama_model = OllamaModel(
            host=self.settings.OLLAMA_HOST,
            model_id=self.settings.OLLAMA_MODEL,
            temperature=0.1
        )
        
        # Initialize tools
        self.aws_cost_tool = AWSCostExplorerTool()
        self.ec2_tool = EC2UtilizationTool()
        self.s3_tool = S3OptimizationTool()
        self.calc_tool = SavingsCalculationTool()
        
        # Create specialized agents
        self._create_agents()
        self._create_orchestrator()
    
    def _create_agents(self):
        # Cost Analysis Agent
        self.cost_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are an AWS Cost Analysis Expert. Analyze spending patterns, 
            identify trends, and provide insights about cost optimization opportunities.
            
            Focus on:
            - Historical spending analysis
            - Cost trend identification
            - Service-level cost breakdown
            - Anomaly detection in spending
            - Budget variance analysis
            
            Always provide actionable insights with specific recommendations.""",
            tools=[self.aws_cost_tool, memory],
            name="cost_analyst"
        )
        
        # Infrastructure Analysis Agent
        self.infrastructure_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are an AWS Infrastructure Optimization Specialist. 
            Focus on EC2 rightsizing, S3 optimization, and resource utilization.
            
            Analyze:
            - EC2 instance utilization and rightsizing opportunities
            - S3 storage optimization and lifecycle policies
            - Resource allocation efficiency
            - Performance vs cost trade-offs
            - Reserved instance opportunities
            
            Provide specific technical recommendations with implementation steps.""",
            tools=[self.ec2_tool, self.s3_tool, memory],
            name="infrastructure_analyst"
        )
        
        # Financial Calculator Agent
        self.financial_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are a Financial Analysis Expert. Perform precise 
            calculations, ROI analysis, and financial projections.
            
            Calculate:
            - Potential cost savings
            - ROI for optimization initiatives
            - Payback periods
            - Risk assessments
            - Budget impact analysis
            
            Always show your calculations and provide confidence intervals.""",
            tools=[self.calc_tool, calculator, memory],
            name="financial_analyst"
        )
        
        # Remediation Agent
        self.remediation_specialist = Agent(
            model=self.ollama_model,
            system_prompt="""You are a Cost Optimization Remediation Specialist. 
            Generate actionable recommendations with implementation plans.
            
            Create:
            - Step-by-step implementation plans
            - Risk mitigation strategies
            - Timeline estimates
            - Resource requirements
            - Success metrics and KPIs
            
            Focus on practical, executable solutions.""",
            tools=[memory],
            name="remediation_specialist"
        )
    
    def _create_orchestrator(self):
        
        @tool
        def cost_analysis_tool(query: str) -> str:
            """Analyze AWS costs and spending patterns"""
            return str(self.cost_analyst(query))
        
        @tool
        def infrastructure_analysis_tool(query: str) -> str:
            """Analyze infrastructure for optimization opportunities"""
            return str(self.infrastructure_analyst(query))
        
        @tool
        def financial_analysis_tool(query: str) -> str:
            """Perform financial calculations and projections"""
            return str(self.financial_analyst(query))
        
        @tool
        def remediation_tool(query: str) -> str:
            """Generate optimization recommendations"""
            return str(self.remediation_specialist(query))
        
        self.orchestrator = Agent(
            model=self.ollama_model,
            system_prompt="""You are the AWS Cost Optimization Orchestrator. 
            Coordinate specialists to provide comprehensive cost optimization analysis.
            
            Available specialists:
            - cost_analysis_tool: For spending analysis and trends
            - infrastructure_analysis_tool: For resource optimization
            - financial_analysis_tool: For calculations and ROI
            - remediation_tool: For actionable recommendations
            
            Process:
            1. Understand the user's request
            2. Determine which specialists are needed
            3. Coordinate their work in logical sequence
            4. Synthesize their findings into actionable insights
            5. Provide prioritized recommendations
            
            Always provide complete, actionable insights with clear next steps.""",
            tools=[
                cost_analysis_tool,
                infrastructure_analysis_tool,
                financial_analysis_tool,
                remediation_tool,
                memory
            ],
            name="orchestrator"
        )
    
    async def analyze_costs(self, user_query: str) -> str:
        try:
            result = self.orchestrator(user_query)
            return str(result)
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    async def parallel_analysis(self, user_query: str) -> Dict[str, str]:
        swarm = Swarm([
            self.cost_analyst,
            self.infrastructure_analyst,
            self.financial_analyst,
            self.remediation_specialist
        ])
        
        results = await swarm.execute(user_query)
        
        return {
            "cost_analysis": str(results[0]),
            "infrastructure_analysis": str(results[1]),
            "financial_analysis": str(results[2]),
            "remediation": str(results[3])
        }
    
    def create_workflow_graph(self):
        graph_builder = GraphBuilder()
        
        graph_builder.add_agent("cost_analyst", self.cost_analyst)
        graph_builder.add_agent("infrastructure_analyst", self.infrastructure_analyst)
        graph_builder.add_agent("financial_analyst", self.financial_analyst)
        graph_builder.add_agent("remediation_specialist", self.remediation_specialist)
        
        # Define workflow
        graph_builder.add_edge("cost_analyst", "infrastructure_analyst")
        graph_builder.add_edge("infrastructure_analyst", "financial_analyst")
        graph_builder.add_edge("financial_analyst", "remediation_specialist")
        
        return graph_builder.build()
    
    async def comprehensive_analysis(self, user_query: str) -> Dict[str, Any]:
        # Step 1: Cost Analysis
        cost_result = await asyncio.to_thread(self.cost_analyst, 
            f"Analyze current AWS costs: {user_query}")
        
        # Step 2: Infrastructure Analysis  
        infra_result = await asyncio.to_thread(self.infrastructure_analyst,
            f"Analyze infrastructure optimization opportunities: {user_query}")
        
        # Step 3: Financial Analysis
        financial_data = {
            "ec2_data": {"instances": []},  # Would be populated from real analysis
            "s3_data": {"buckets": []},
            "rds_data": {"databases": []}
        }
        
        financial_result = await asyncio.to_thread(self.financial_analyst,
            f"Calculate savings and ROI: {json.dumps(financial_data)}")
        
        # Step 4: Remediation Planning
        remediation_result = await asyncio.to_thread(self.remediation_specialist,
            f"Create implementation plan based on: Cost Analysis: {cost_result[:500]} Infrastructure: {infra_result[:500]} Financial: {financial_result[:500]}")
        
        return {
            "cost_analysis": str(cost_result),
            "infrastructure_analysis": str(infra_result), 
            "financial_analysis": str(financial_result),
            "remediation_plan": str(remediation_result),
            "timestamp": asyncio.get_event_loop().time()
        }

# Global instance
orchestrator = CostOptimizationOrchestrator()