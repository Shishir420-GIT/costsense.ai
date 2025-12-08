"""Fully Agentic Orchestrator using LangGraph with ReAct pattern"""

from typing import Dict, Any, List, Optional, Annotated, Sequence
import logging
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from .tools import (
    COST_ANALYSIS_TOOLS,
    INFRASTRUCTURE_TOOLS,
    OPTIMIZATION_TOOLS,
    FINANCIAL_TOOLS,
    INFRA_PLANNER_TOOLS,
    ALL_TOOLS
)

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT STATE
# ============================================================================

class AgentState(TypedDict):
    """State for the agentic system"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    agent_type: str
    final_response: Optional[str]


# ============================================================================
# AGENTIC ORCHESTRATOR
# ============================================================================

class AgenticOrchestrator:
    """Fully agentic orchestrator using LangGraph with tool calling"""

    def __init__(self):
        """Initialize the agentic orchestrator"""
        try:
            # Try to initialize Ollama LLM
            self.llm = ChatOllama(
                model="llama3.2:latest",
                temperature=0.1,
            )
            # Test connection
            self.llm.invoke("test")
            self.llm_available = True
            logger.info("Agentic Orchestrator initialized with Ollama LLM")
        except Exception as e:
            self.llm = None
            self.llm_available = False
            logger.warning(f"Ollama not available, using fallback mode: {e}")

        # Create specialized agents
        self.cost_agent = self._create_cost_agent()
        self.infrastructure_agent = self._create_infrastructure_agent()
        self.financial_agent = self._create_financial_agent()
        self.optimization_agent = self._create_optimization_agent()
        self.infra_planner_agent = self._create_infra_planner_agent()

    def _create_cost_agent(self):
        """Create cost analysis agent with tools"""
        if not self.llm_available:
            return None

        system_prompt = """You are an Azure Cost Analysis Expert.

Your role is to analyze Azure spending patterns, identify cost trends, and provide insights.

When analyzing costs:
1. Use the available tools to query actual database data
2. Identify patterns and anomalies
3. Provide specific recommendations
4. Highlight areas of concern

Available tools allow you to:
- Get total monthly costs
- Analyze cost trends over time
- Identify top spending services
- Calculate cost changes

Always provide data-driven insights with specific numbers and percentages.
"""

        llm_with_tools = self.llm.bind_tools(COST_ANALYSIS_TOOLS)

        return {
            "llm": llm_with_tools,
            "system_prompt": system_prompt,
            "tools": COST_ANALYSIS_TOOLS
        }

    def _create_infrastructure_agent(self):
        """Create infrastructure analysis agent with tools"""
        if not self.llm_available:
            return None

        system_prompt = """You are an Azure Infrastructure Expert.

Your role is to analyze virtual machines, storage accounts, and other infrastructure components.

When analyzing infrastructure:
1. Use tools to query VM and storage data from the database
2. Identify underutilized or overprovisioned resources
3. Assess resource health and performance
4. Recommend right-sizing opportunities

Available tools allow you to:
- Get all VMs with details
- Get VM summary statistics
- Find underutilized VMs
- Get storage account information
- Analyze storage tiers

Always provide specific resource names and actionable recommendations.
"""

        llm_with_tools = self.llm.bind_tools(INFRASTRUCTURE_TOOLS)

        return {
            "llm": llm_with_tools,
            "system_prompt": system_prompt,
            "tools": INFRASTRUCTURE_TOOLS
        }

    def _create_financial_agent(self):
        """Create financial analysis agent with tools"""
        if not self.llm_available:
            return None

        system_prompt = """You are an Azure Financial Analyst.

Your role is to perform ROI calculations, cost projections, and financial planning.

When performing financial analysis:
1. Use tools to calculate ROI and payback periods
2. Project future costs based on current spending
3. Analyze cost-benefit of optimization initiatives
4. Provide clear financial recommendations

Available tools allow you to:
- Calculate ROI for optimizations
- Project future costs
- Estimate total potential savings

Always provide clear financial metrics and justify your recommendations.
"""

        llm_with_tools = self.llm.bind_tools(FINANCIAL_TOOLS)

        return {
            "llm": llm_with_tools,
            "system_prompt": system_prompt,
            "tools": FINANCIAL_TOOLS
        }

    def _create_optimization_agent(self):
        """Create optimization recommendations agent with tools"""
        if not self.llm_available:
            return None

        system_prompt = """You are an Azure Optimization Specialist.

Your role is to identify and prioritize cost optimization opportunities.

When analyzing optimizations:
1. Use tools to get all recommendations from the database
2. Prioritize by savings potential and ease of implementation
3. Categorize recommendations by type
4. Provide clear implementation guidance

Available tools allow you to:
- Get all optimization recommendations
- Filter by priority or category
- Calculate total savings potential
- Get optimization summary

Always prioritize high-impact, low-effort optimizations.
"""

        llm_with_tools = self.llm.bind_tools(OPTIMIZATION_TOOLS)

        return {
            "llm": llm_with_tools,
            "system_prompt": system_prompt,
            "tools": OPTIMIZATION_TOOLS
        }

    def _create_infra_planner_agent(self):
        """Create infrastructure planner agent with tools"""
        if not self.llm_available:
            return None

        system_prompt = """You are an Azure Infrastructure Planning Expert.

Your role is to design and visualize Azure cloud architectures based on requirements.

When planning infrastructure:
1. Understand the user's workload requirements (web app, data pipeline, ML, etc.)
2. Use tools to generate architecture DSL code
3. Recommend appropriate Azure services for the use case
4. Estimate monthly costs realistically
5. Validate architecture against Azure best practices
6. Provide security, reliability, and cost optimization recommendations

Available tools allow you to:
- Generate Azure architecture DSL code
- Get service recommendations for different workload types
- Estimate costs for Azure services
- Validate architecture against best practices

Always design for security, reliability, scalability, and cost optimization.
"""

        llm_with_tools = self.llm.bind_tools(INFRA_PLANNER_TOOLS)

        return {
            "llm": llm_with_tools,
            "system_prompt": system_prompt,
            "tools": INFRA_PLANNER_TOOLS
        }

    def _route_query(self, query: str) -> str:
        """Determine which agent should handle the query"""
        query_lower = query.lower().strip()

        # Check for greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        if query_lower in greetings or (len(query_lower.split()) <= 2 and any(g in query_lower for g in greetings)):
            return 'greeting'

        # Cost-related keywords
        if any(word in query_lower for word in ['cost', 'spend', 'expense', 'price', 'bill', 'budget']):
            return 'cost'

        # Infrastructure keywords
        if any(word in query_lower for word in ['vm', 'virtual machine', 'compute', 'storage', 'resource', 'infrastructure', 'server']):
            return 'infrastructure'

        # Financial keywords
        if any(word in query_lower for word in ['roi', 'return', 'investment', 'payback', 'financial', 'project', 'forecast']):
            return 'financial'

        # Optimization keywords
        if any(word in query_lower for word in ['optimize', 'recommend', 'save', 'savings', 'reduce', 'improve']):
            return 'optimization'

        # Infrastructure planning keywords
        if any(word in query_lower for word in ['plan', 'design', 'architect', 'build', 'create infrastructure', 'deploy', 'diagram', 'blueprint']):
            return 'infra_planner'

        # Default to cost analysis
        return 'cost'

    async def analyze(self, query: str) -> str:
        """Main analysis entry point using agentic approach"""

        # Handle greetings
        if self._route_query(query) == 'greeting':
            return self._greeting_response()

        # If LLM not available, use fallback
        if not self.llm_available:
            return await self._fallback_analyze(query)

        # Route to appropriate agent
        agent_type = self._route_query(query)

        try:
            if agent_type == 'cost':
                return await self._run_cost_agent(query)
            elif agent_type == 'infrastructure':
                return await self._run_infrastructure_agent(query)
            elif agent_type == 'financial':
                return await self._run_financial_agent(query)
            elif agent_type == 'optimization':
                return await self._run_optimization_agent(query)
            elif agent_type == 'infra_planner':
                return await self._run_infra_planner_agent(query)
            else:
                return await self._run_cost_agent(query)  # Default
        except Exception as e:
            logger.error(f"Agentic analysis failed: {e}")
            return await self._fallback_analyze(query)

    def _greeting_response(self) -> str:
        """Return greeting message"""
        return """👋 Hi! I'm your Azure Cost Optimization Assistant.

I can help you with:
• **Cost Analysis** - View spending, trends, and top services
• **Infrastructure Review** - Analyze VMs, storage, and resources
• **Optimization Tips** - Get recommendations to reduce costs
• **Savings Calculation** - Estimate ROI and potential savings

Try asking:
- "What is our total Azure spend?"
- "Show me all VMs"
- "Which resources are underutilized?"
- "How can we save money on storage?"

What would you like to know?"""

    async def _run_cost_agent(self, query: str) -> str:
        """Run cost analysis agent with tool calling"""
        agent = self.cost_agent

        messages = [
            SystemMessage(content=agent["system_prompt"]),
            HumanMessage(content=query)
        ]

        # Agent reasoning loop (ReAct pattern)
        max_iterations = 5
        for i in range(max_iterations):
            response = await agent["llm"].ainvoke(messages)
            messages.append(response)

            # Check if agent wants to use tools
            if not response.tool_calls:
                # Agent has final answer
                return f"**Cost Analysis:**\n\n{response.content}"

            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the tool
                tool = next((t for t in agent["tools"] if t.name == tool_name), None)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        # Add tool result to messages
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        messages.append(ToolMessage(
                            content=f"Tool '{tool_name}' failed: {str(e)}",
                            tool_call_id=tool_call["id"]
                        ))

        return f"**Cost Analysis:**\n\n{messages[-1].content if messages else 'Analysis unavailable'}"

    async def _run_infrastructure_agent(self, query: str) -> str:
        """Run infrastructure analysis agent with tool calling"""
        agent = self.infrastructure_agent

        messages = [
            SystemMessage(content=agent["system_prompt"]),
            HumanMessage(content=query)
        ]

        # Agent reasoning loop
        max_iterations = 5
        for i in range(max_iterations):
            response = await agent["llm"].ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return f"**Infrastructure Analysis:**\n\n{response.content}"

            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool = next((t for t in agent["tools"] if t.name == tool_name), None)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        messages.append(ToolMessage(
                            content=f"Tool '{tool_name}' failed: {str(e)}",
                            tool_call_id=tool_call["id"]
                        ))

        return f"**Infrastructure Analysis:**\n\n{messages[-1].content if messages else 'Analysis unavailable'}"

    async def _run_financial_agent(self, query: str) -> str:
        """Run financial analysis agent with tool calling"""
        agent = self.financial_agent

        messages = [
            SystemMessage(content=agent["system_prompt"]),
            HumanMessage(content=query)
        ]

        max_iterations = 5
        for i in range(max_iterations):
            response = await agent["llm"].ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return f"**Financial Analysis:**\n\n{response.content}"

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool = next((t for t in agent["tools"] if t.name == tool_name), None)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        messages.append(ToolMessage(
                            content=f"Tool '{tool_name}' failed: {str(e)}",
                            tool_call_id=tool_call["id"]
                        ))

        return f"**Financial Analysis:**\n\n{messages[-1].content if messages else 'Analysis unavailable'}"

    async def _run_optimization_agent(self, query: str) -> str:
        """Run optimization agent with tool calling"""
        agent = self.optimization_agent

        messages = [
            SystemMessage(content=agent["system_prompt"]),
            HumanMessage(content=query)
        ]

        max_iterations = 5
        for i in range(max_iterations):
            response = await agent["llm"].ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return f"**Optimization Recommendations:**\n\n{response.content}"

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool = next((t for t in agent["tools"] if t.name == tool_name), None)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        messages.append(ToolMessage(
                            content=f"Tool '{tool_name}' failed: {str(e)}",
                            tool_call_id=tool_call["id"]
                        ))

        return f"**Optimization Recommendations:**\n\n{messages[-1].content if messages else 'Analysis unavailable'}"

    async def _run_infra_planner_agent(self, query: str) -> str:
        """Run infrastructure planner agent with tool calling"""
        agent = self.infra_planner_agent

        messages = [
            SystemMessage(content=agent["system_prompt"]),
            HumanMessage(content=query)
        ]

        max_iterations = 5
        for i in range(max_iterations):
            response = await agent["llm"].ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return f"**Infrastructure Plan:**\n\n{response.content}"

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool = next((t for t in agent["tools"] if t.name == tool_name), None)
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        messages.append(ToolMessage(
                            content=f"Tool '{tool_name}' failed: {str(e)}",
                            tool_call_id=tool_call["id"]
                        ))

        return f"**Infrastructure Plan:**\n\n{messages[-1].content if messages else 'Plan unavailable'}"

    async def _fallback_analyze(self, query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        from .cost_analyst import cost_analyst
        from .infrastructure_analyst import infrastructure_analyst

        agent_type = self._route_query(query)

        if agent_type == 'cost':
            return await cost_analyst.analyze(query)
        elif agent_type == 'infrastructure':
            return await infrastructure_analyst.analyze(query)
        else:
            return await cost_analyst.analyze(query)


# Singleton instance
agentic_orchestrator = AgenticOrchestrator()
