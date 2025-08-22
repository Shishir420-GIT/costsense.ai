from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from enum import Enum

from src.agents.cost_analyst import cost_analyst
from src.agents.infrastructure_analyst import infrastructure_analyst
from src.agents.financial_analyst import financial_analyst
from src.agents.orchestrator import orchestrator

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of available agents"""
    COST_ANALYST = "cost_analyst"
    INFRASTRUCTURE_ANALYST = "infrastructure_analyst"
    FINANCIAL_ANALYST = "financial_analyst"
    ORCHESTRATOR = "orchestrator"

class AgentRegistry:
    """Central registry for managing all AI agents in the system"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize and register all available agents"""
        try:
            # Register cost analyst
            self.register_agent(
                AgentType.COST_ANALYST.value,
                cost_analyst,
                {
                    "display_name": "Cost Analyst",
                    "description": "Specialized in AWS cost analysis, trend identification, and anomaly detection",
                    "capabilities": cost_analyst.get_capabilities(),
                    "domain": "cost_analysis",
                    "priority": 1
                }
            )
            
            # Register infrastructure analyst
            self.register_agent(
                AgentType.INFRASTRUCTURE_ANALYST.value,
                infrastructure_analyst,
                {
                    "display_name": "Infrastructure Analyst", 
                    "description": "Specialized in AWS resource optimization, rightsizing, and efficiency analysis",
                    "capabilities": infrastructure_analyst.get_capabilities(),
                    "domain": "infrastructure_optimization",
                    "priority": 2
                }
            )
            
            # Register financial analyst
            self.register_agent(
                AgentType.FINANCIAL_ANALYST.value,
                financial_analyst,
                {
                    "display_name": "Financial Analyst",
                    "description": "Specialized in ROI calculations, financial projections, and investment analysis",
                    "capabilities": financial_analyst.get_capabilities(),
                    "domain": "financial_analysis",
                    "priority": 3
                }
            )
            
            # Register orchestrator
            self.register_agent(
                AgentType.ORCHESTRATOR.value,
                orchestrator,
                {
                    "display_name": "Cost Optimization Orchestrator",
                    "description": "Master coordinator for comprehensive multi-agent cost optimization analysis",
                    "capabilities": ["comprehensive_analysis", "agent_coordination", "recommendation_prioritization"],
                    "domain": "orchestration",
                    "priority": 0  # Highest priority as master coordinator
                }
            )
            
            logger.info(f"Successfully initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def register_agent(self, agent_name: str, agent_instance: Any, metadata: Dict[str, Any]):
        """Register an agent with the registry"""
        try:
            self.agents[agent_name] = agent_instance
            self.agent_metadata[agent_name] = {
                **metadata,
                "registered_at": datetime.now().isoformat(),
                "status": "registered"
            }
            
            logger.info(f"Registered agent: {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_name}: {e}")
            raise
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get an agent instance by name"""
        return self.agents.get(agent_name)
    
    def get_agent_metadata(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific agent"""
        return self.agent_metadata.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self.agents.keys())
    
    def list_agents_by_domain(self, domain: str) -> List[str]:
        """List agents by domain"""
        return [
            name for name, metadata in self.agent_metadata.items()
            if metadata.get("domain") == domain
        ]
    
    def list_agents_by_capability(self, capability: str) -> List[str]:
        """List agents that have a specific capability"""
        matching_agents = []
        for name, metadata in self.agent_metadata.items():
            capabilities = metadata.get("capabilities", [])
            if capability in capabilities:
                matching_agents.append(name)
        return matching_agents
    
    async def get_agent_health_status(self, agent_name: str) -> Dict[str, Any]:
        """Get health status for a specific agent"""
        try:
            agent = self.get_agent(agent_name)
            if not agent:
                return {
                    "agent_name": agent_name,
                    "healthy": False,
                    "error": "Agent not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Call agent's health check method
            if hasattr(agent, 'health_check'):
                health_status = await agent.health_check()
                return health_status
            else:
                return {
                    "agent_name": agent_name,
                    "healthy": True,
                    "note": "Health check method not implemented",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Health check failed for agent {agent_name}: {e}")
            return {
                "agent_name": agent_name,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_all_agents_health(self) -> Dict[str, Any]:
        """Get health status for all registered agents"""
        try:
            health_results = {}
            
            # Get health status for each agent concurrently
            health_tasks = []
            for agent_name in self.agents.keys():
                task = self.get_agent_health_status(agent_name)
                health_tasks.append((agent_name, task))
            
            # Wait for all health checks to complete
            for agent_name, task in health_tasks:
                health_results[agent_name] = await task
            
            # Calculate overall system health
            healthy_agents = sum(1 for status in health_results.values() if status.get("healthy", False))
            total_agents = len(health_results)
            overall_health = "healthy" if healthy_agents == total_agents else "degraded" if healthy_agents > 0 else "unhealthy"
            
            return {
                "overall_health": overall_health,
                "healthy_agents": healthy_agents,
                "total_agents": total_agents,
                "agent_details": health_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "overall_health": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_agent_query(self, agent_name: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a query using a specific agent"""
        try:
            agent = self.get_agent(agent_name)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            start_time = datetime.now()
            
            # Execute query based on agent type
            if agent_name == AgentType.ORCHESTRATOR.value:
                result = await agent.analyze_costs(query)
            else:
                result = await agent.analyze(query, context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "agent_name": agent_name,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute query with agent {agent_name}: {e}")
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_parallel_analysis(self, query: str) -> Dict[str, Any]:
        """Execute parallel analysis using the orchestrator"""
        try:
            orchestrator_agent = self.get_agent(AgentType.ORCHESTRATOR.value)
            if not orchestrator_agent:
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            start_time = datetime.now()
            results = await orchestrator_agent.parallel_analysis(query)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "analysis_type": "parallel",
                "results": results,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Parallel analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_comprehensive_analysis(self, query: str) -> Dict[str, Any]:
        """Execute comprehensive analysis using the orchestrator"""
        try:
            orchestrator_agent = self.get_agent(AgentType.ORCHESTRATOR.value)
            if not orchestrator_agent:
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            start_time = datetime.now()
            results = await orchestrator_agent.comprehensive_analysis(query)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "analysis_type": "comprehensive",
                "results": results,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agent_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of all agent capabilities"""
        try:
            capabilities_by_domain = {}
            all_capabilities = set()
            
            for agent_name, metadata in self.agent_metadata.items():
                domain = metadata.get("domain", "unknown")
                capabilities = metadata.get("capabilities", [])
                
                if domain not in capabilities_by_domain:
                    capabilities_by_domain[domain] = {
                        "agents": [],
                        "capabilities": []
                    }
                
                capabilities_by_domain[domain]["agents"].append({
                    "name": agent_name,
                    "display_name": metadata.get("display_name"),
                    "description": metadata.get("description")
                })
                
                capabilities_by_domain[domain]["capabilities"].extend(capabilities)
                all_capabilities.update(capabilities)
            
            return {
                "total_agents": len(self.agents),
                "total_capabilities": len(all_capabilities),
                "capabilities_by_domain": capabilities_by_domain,
                "all_capabilities": list(all_capabilities),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate capabilities summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get comprehensive registry information"""
        return {
            "registry_status": "active",
            "total_agents": len(self.agents),
            "registered_agents": [
                {
                    "name": name,
                    "display_name": metadata.get("display_name"),
                    "description": metadata.get("description"),
                    "domain": metadata.get("domain"),
                    "priority": metadata.get("priority"),
                    "capabilities_count": len(metadata.get("capabilities", [])),
                    "registered_at": metadata.get("registered_at")
                }
                for name, metadata in self.agent_metadata.items()
            ],
            "available_domains": list(set(
                metadata.get("domain") for metadata in self.agent_metadata.values()
            )),
            "timestamp": datetime.now().isoformat()
        }

# Global registry instance
agent_registry = AgentRegistry()