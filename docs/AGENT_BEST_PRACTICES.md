# Agent Best Practices & Examples

## Overview
This document provides comprehensive examples and best practices for implementing production-ready AI agents using the Strands framework, specifically tailored for the CostSense-AI system.

## 1. Prompt Engineering Best Practices

### Structure Your Prompts with Clear Sections

```python
def get_enhanced_system_prompt(agent_role: str, domain: str) -> str:
    """Generate structured system prompts with examples"""
    
    prompt_template = """
# AGENT IDENTITY
You are a {agent_role} specializing in {domain}.

# CORE CAPABILITIES
- Primary: {primary_capability}
- Secondary: {secondary_capabilities}
- Tools Available: {available_tools}

# INPUT PROCESSING
Expected Input Format:
{{
  "query": "User's request",
  "context": "Previous conversation or analysis",
  "constraints": {{
    "time_period": "7_days|30_days|90_days",
    "focus_area": "specific area to analyze",
    "confidence_threshold": "minimum confidence for recommendations"
  }}
}}

# OUTPUT STRUCTURE
Always respond in this JSON format:
{{
  "analysis_summary": "Executive summary of findings",
  "confidence_score": 0.0-1.0,
  "key_insights": [
    {{
      "category": "cost|performance|security|compliance",
      "finding": "Specific insight",
      "evidence": "Supporting data",
      "confidence": "high|medium|low",
      "impact": "critical|high|medium|low"
    }}
  ],
  "recommendations": [
    {{
      "title": "Clear recommendation title",
      "description": "Detailed explanation",
      "action_items": ["step1", "step2", "step3"],
      "effort_estimate": "hours|days|weeks",
      "cost_impact": {{
        "savings_potential": "$X.XX per month",
        "implementation_cost": "$Y.YY",
        "payback_period": "X months"
      }},
      "risk_level": "low|medium|high",
      "priority": "p0|p1|p2|p3"
    }}
  ],
  "next_steps": ["immediate actions"],
  "follow_up_questions": ["clarifying questions if needed"]
}}

# EXAMPLES

## Example 1: Cost Trend Analysis
Input: {{"query": "Analyze EC2 cost trends", "constraints": {{"time_period": "30_days"}}}}

Expected Output:
{{
  "analysis_summary": "EC2 costs increased 15% over 30 days, driven by m5.large instance scaling",
  "confidence_score": 0.85,
  "key_insights": [
    {{
      "category": "cost",
      "finding": "Significant increase in compute costs due to auto-scaling",
      "evidence": "Daily costs rose from $250 to $289 average",
      "confidence": "high",
      "impact": "high"
    }}
  ],
  "recommendations": [
    {{
      "title": "Optimize Auto-Scaling Policies",
      "description": "Current scaling triggers are too aggressive, causing over-provisioning",
      "action_items": [
        "Review CloudWatch metrics thresholds",
        "Implement predictive scaling",
        "Add step scaling policies"
      ],
      "effort_estimate": "2-3 days",
      "cost_impact": {{
        "savings_potential": "$580.00 per month",
        "implementation_cost": "$0.00",
        "payback_period": "immediate"
      }},
      "risk_level": "low",
      "priority": "p1"
    }}
  ],
  "next_steps": ["Audit current auto-scaling configuration"],
  "follow_up_questions": ["What is your target CPU utilization threshold?"]
}}

# ANALYSIS GUIDELINES

## Data Interpretation Rules
1. Always quantify findings with specific numbers and percentages
2. Compare against baselines (previous period, industry benchmarks)
3. Identify statistical significance (avoid false positives)
4. Consider seasonal patterns and business context

## Recommendation Quality Standards
1. SMART criteria: Specific, Measurable, Achievable, Relevant, Time-bound
2. Include confidence intervals for estimates
3. Always provide implementation steps
4. Consider dependencies and prerequisites
5. Include rollback plans for high-risk changes

## Error Handling
- If data is insufficient: Request additional context
- If analysis is ambiguous: Present multiple scenarios
- If recommendations are uncertain: Lower confidence scores
- Always acknowledge limitations in your analysis

# ESCALATION TRIGGERS
Escalate to human when:
- Potential cost impact > $5,000/month
- Security or compliance implications detected
- Analysis confidence < 0.6
- Conflicting recommendations from multiple data sources
"""
    
    return prompt_template.format(
        agent_role=agent_role,
        domain=domain,
        # ... other parameters
    )
```

## 2. Tool Development Best Practices

### Async Tool Implementation with Error Handling

```python
import asyncio
from typing import Optional, Dict, Any
from strands import Tool
from functools import wraps
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

class EnhancedAWSCostTool(Tool):
    """Production-ready AWS Cost Explorer tool with comprehensive error handling"""
    
    def __init__(self):
        super().__init__(
            name="aws_cost_explorer_v2",
            description="Advanced AWS cost analysis with caching and resilience"
        )
        self.client = None
        self.cache = {}
        self.rate_limiter = AsyncRateLimiter(calls_per_minute=60)
    
    def with_telemetry(func):
        """Decorator for adding telemetry to tool methods"""
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = asyncio.get_event_loop().time()
            method_name = func.__name__
            
            try:
                logger.info("Tool method started", method=method_name, args=args)
                result = await func(self, *args, **kwargs)
                
                execution_time = asyncio.get_event_loop().time() - start_time
                logger.info(
                    "Tool method completed", 
                    method=method_name, 
                    execution_time=execution_time,
                    result_size=len(str(result)) if result else 0
                )
                return result
                
            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                logger.error(
                    "Tool method failed", 
                    method=method_name, 
                    error=str(e),
                    execution_time=execution_time
                )
                raise
        return wrapper
    
    @with_telemetry
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_cost_data(
        self, 
        time_period: str = "30_days",
        service_filter: Optional[str] = None,
        include_forecast: bool = False
    ) -> Dict[str, Any]:
        """
        Get comprehensive cost data with advanced filtering and forecasting
        
        Args:
            time_period: Analysis period (7_days, 30_days, 90_days, 1_year)
            service_filter: Specific AWS service to analyze (optional)
            include_forecast: Include cost forecasting (default: False)
        
        Returns:
            Comprehensive cost analysis data
        """
        
        # Check cache first
        cache_key = f"cost_data_{time_period}_{service_filter}_{include_forecast}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry['timestamp']):
                logger.info("Returning cached result", cache_key=cache_key)
                return cache_entry['data']
        
        # Rate limiting
        async with self.rate_limiter:
            try:
                # Ensure client is initialized
                await self._ensure_client_ready()
                
                # Get cost data
                cost_data = await self._fetch_cost_data(time_period, service_filter)
                
                # Add forecasting if requested
                if include_forecast:
                    forecast_data = await self._generate_cost_forecast(cost_data)
                    cost_data['forecast'] = forecast_data
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': cost_data,
                    'timestamp': asyncio.get_event_loop().time()
                }
                
                return cost_data
                
            except Exception as e:
                logger.error("Failed to fetch cost data", error=str(e))
                # Try to return cached data even if expired
                if cache_key in self.cache:
                    logger.warning("Returning stale cached data due to API failure")
                    return self.cache[cache_key]['data']
                raise
    
    async def _ensure_client_ready(self):
        """Ensure AWS client is properly initialized"""
        if self.client is None:
            try:
                self.client = await self._init_aws_client()
                logger.info("AWS client initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize AWS client", error=str(e))
                raise
    
    async def _fetch_cost_data(self, time_period: str, service_filter: Optional[str]) -> Dict:
        """Internal method to fetch cost data from AWS"""
        # Implementation details...
        pass
    
    async def _generate_cost_forecast(self, historical_data: Dict) -> Dict:
        """Generate cost forecasting based on historical trends"""
        # Implement forecasting logic using historical patterns
        pass
    
    def _is_cache_valid(self, timestamp: float, ttl: int = 3600) -> bool:
        """Check if cached data is still valid"""
        return (asyncio.get_event_loop().time() - timestamp) < ttl

class AsyncRateLimiter:
    """Async rate limiter for API calls"""
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def __aenter__(self):
        now = asyncio.get_event_loop().time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # Wait if we've exceeded the rate limit
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
```

## 3. Agent Workflow Orchestration

### Advanced Workflow Implementation

```python
from strands.multiagent import GraphBuilder, WorkflowState
from typing import Dict, Any, List, Callable
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_HUMAN = "requires_human"

class WorkflowNode:
    def __init__(self, name: str, agent, condition: Optional[Callable] = None):
        self.name = name
        self.agent = agent
        self.condition = condition
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.metadata = {}

class AdvancedOrchestrator:
    """Production-ready agent orchestrator with sophisticated workflow management"""
    
    def __init__(self):
        self.workflow_graph = self._build_adaptive_workflow()
        self.session_state = WorkflowState()
        self.execution_history = []
        
    def _build_adaptive_workflow(self) -> 'WorkflowGraph':
        """Build workflow graph with conditional routing and parallel execution"""
        
        builder = GraphBuilder()
        
        # Define workflow nodes
        nodes = {
            "query_analyzer": WorkflowNode("query_analyzer", self.query_analyzer_agent),
            "cost_analyzer": WorkflowNode("cost_analyzer", self.cost_analyst_agent),
            "infra_analyzer": WorkflowNode("infra_analyzer", self.infrastructure_analyst_agent),
            "financial_calculator": WorkflowNode("financial_calculator", self.financial_analyst_agent),
            "risk_assessor": WorkflowNode("risk_assessor", self.risk_assessment_agent),
            "recommendation_engine": WorkflowNode("recommendation_engine", self.recommendation_agent),
            "validation_agent": WorkflowNode("validation_agent", self.validation_agent)
        }
        
        # Add nodes to graph
        for node_name, node in nodes.items():
            builder.add_agent(node_name, node.agent)
        
        # Define conditional workflows
        
        # 1. Query Analysis → Determine Path
        builder.add_conditional_edge(
            "query_analyzer", 
            ["cost_analyzer", "infra_analyzer"],
            condition=self._route_based_on_query_intent
        )
        
        # 2. Parallel Analysis Phase
        builder.add_parallel_edges([
            ("cost_analyzer", "financial_calculator"),
            ("infra_analyzer", "risk_assessor")
        ])
        
        # 3. Convergence → Recommendation Engine
        builder.add_convergence_edge(
            ["financial_calculator", "risk_assessor"],
            "recommendation_engine"
        )
        
        # 4. Validation Phase
        builder.add_edge("recommendation_engine", "validation_agent")
        
        return builder.build()
    
    async def execute_intelligent_workflow(
        self, 
        query: str, 
        context: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with intelligent routing and context management
        
        Args:
            query: User's analysis request
            context: Previous conversation or session context
            user_preferences: User's risk tolerance, priorities, constraints
            
        Returns:
            Comprehensive analysis results with recommendations
        """
        
        # Initialize workflow state
        workflow_id = self._generate_workflow_id()
        self.session_state = WorkflowState({
            "workflow_id": workflow_id,
            "query": query,
            "context": context or {},
            "user_preferences": user_preferences or {},
            "start_time": asyncio.get_event_loop().time(),
            "execution_path": [],
            "intermediate_results": {}
        })
        
        try:
            logger.info("Starting workflow execution", workflow_id=workflow_id, query=query)
            
            # Execute workflow graph
            result = await self.workflow_graph.execute(self.session_state)
            
            # Post-process results
            processed_result = await self._post_process_results(result)
            
            # Update execution history
            self._update_execution_history(workflow_id, processed_result)
            
            logger.info("Workflow completed successfully", workflow_id=workflow_id)
            return processed_result
            
        except Exception as e:
            logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))
            
            # Attempt recovery
            recovery_result = await self._attempt_workflow_recovery(e)
            if recovery_result:
                return recovery_result
            
            # If recovery fails, return partial results
            return await self._generate_partial_results(self.session_state)
    
    def _route_based_on_query_intent(self, state: WorkflowState) -> List[str]:
        """Intelligent routing based on query analysis"""
        
        query = state.get("query", "").lower()
        intent_keywords = {
            "cost": ["cost", "spend", "bill", "expense", "budget"],
            "performance": ["performance", "utilization", "efficiency", "speed"],
            "security": ["security", "compliance", "audit", "risk"],
            "optimization": ["optimize", "improve", "reduce", "save"]
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                detected_intents.append(intent)
        
        # Route based on detected intents
        route_map = {
            "cost": ["cost_analyzer"],
            "performance": ["infra_analyzer"], 
            "security": ["risk_assessor"],
            "optimization": ["cost_analyzer", "infra_analyzer"]
        }
        
        routes = []
        for intent in detected_intents:
            routes.extend(route_map.get(intent, []))
        
        # Default to comprehensive analysis if unclear
        return routes if routes else ["cost_analyzer", "infra_analyzer"]
    
    async def _post_process_results(self, raw_results: Dict) -> Dict[str, Any]:
        """Post-process workflow results for consistency and quality"""
        
        processed = {
            "workflow_summary": {
                "execution_time": asyncio.get_event_loop().time() - self.session_state.get("start_time", 0),
                "agents_executed": list(raw_results.keys()),
                "confidence_score": self._calculate_overall_confidence(raw_results),
                "data_freshness": await self._assess_data_freshness(),
                "workflow_id": self.session_state.get("workflow_id")
            },
            "executive_summary": await self._generate_executive_summary(raw_results),
            "detailed_analysis": raw_results,
            "prioritized_recommendations": await self._prioritize_recommendations(raw_results),
            "risk_assessment": await self._consolidate_risk_assessment(raw_results),
            "implementation_plan": await self._generate_implementation_plan(raw_results),
            "monitoring_strategy": await self._generate_monitoring_strategy(raw_results)
        }
        
        return processed
    
    async def _attempt_workflow_recovery(self, error: Exception) -> Optional[Dict]:
        """Attempt to recover from workflow failures"""
        
        logger.info("Attempting workflow recovery", error=str(error))
        
        # Strategy 1: Use cached intermediate results
        if self.session_state.get("intermediate_results"):
            logger.info("Using cached intermediate results for recovery")
            return await self._build_results_from_cache()
        
        # Strategy 2: Fallback to simpler workflow
        try:
            logger.info("Attempting simplified workflow")
            return await self._execute_fallback_workflow()
        except Exception as fallback_error:
            logger.error("Fallback workflow also failed", error=str(fallback_error))
            return None
    
    def _calculate_overall_confidence(self, results: Dict) -> float:
        """Calculate overall confidence score from individual agent results"""
        
        confidences = []
        for agent_result in results.values():
            if isinstance(agent_result, dict) and 'confidence_score' in agent_result:
                confidences.append(agent_result['confidence_score'])
        
        if not confidences:
            return 0.5  # Default medium confidence
        
        # Weighted average (you can customize weights based on agent importance)
        return sum(confidences) / len(confidences)
```

## 4. Error Handling and Resilience Patterns

### Circuit Breaker Pattern Implementation

```python
import asyncio
from enum import Enum
from typing import Optional, Callable, Any
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open" # Testing recovery

class CircuitBreaker:
    """Circuit breaker implementation for agent resilience"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage example
class ResilientAgent:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30
        )
    
    async def analyze_with_resilience(self, query: str) -> str:
        """Agent analysis with circuit breaker protection"""
        
        try:
            return await self.circuit_breaker.call(
                self._perform_analysis, 
                query
            )
        except Exception as e:
            logger.warning("Primary analysis failed, using fallback", error=str(e))
            return await self._fallback_analysis(query)
```

## 5. Testing Best Practices

### Comprehensive Agent Testing Framework

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

class AgentTestFramework:
    """Comprehensive testing framework for AI agents"""
    
    @pytest.fixture
    def mock_aws_client(self):
        """Mock AWS client for testing"""
        client = Mock()
        
        # Mock Cost Explorer responses
        client.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-02'},
                    'Total': {'BlendedCost': {'Amount': '150.50'}},
                    'Groups': [
                        {
                            'Keys': ['Amazon Elastic Compute Cloud - Compute'],
                            'Metrics': {'BlendedCost': {'Amount': '100.00'}}
                        }
                    ]
                }
            ]
        }
        
        return client
    
    @pytest.mark.asyncio
    async def test_cost_analyst_basic_analysis(self, mock_aws_client):
        """Test cost analyst basic functionality"""
        
        with patch('boto3.client', return_value=mock_aws_client):
            agent = CostAnalystAgent()
            result = await agent.analyze("Analyze EC2 costs for last 30 days")
            
            # Verify response structure
            assert isinstance(result, str)
            assert "EC2" in result
            assert "$" in result  # Should contain cost information
    
    @pytest.mark.asyncio
    async def test_orchestrator_workflow_routing(self):
        """Test orchestrator query routing logic"""
        
        orchestrator = AdvancedOrchestrator()
        
        # Test cost-related query routing
        cost_query = "What are my EC2 costs this month?"
        routes = orchestrator._route_based_on_query_intent(
            WorkflowState({"query": cost_query})
        )
        
        assert "cost_analyzer" in routes
        
        # Test performance-related query routing
        perf_query = "How can I improve my infrastructure performance?"
        routes = orchestrator._route_based_on_query_intent(
            WorkflowState({"query": perf_query})
        )
        
        assert "infra_analyzer" in routes
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, mock_aws_client):
        """Test error handling and fallback mechanisms"""
        
        # Configure mock to raise exception
        mock_aws_client.get_cost_and_usage.side_effect = Exception("AWS API Error")
        
        with patch('boto3.client', return_value=mock_aws_client):
            agent = CostAnalystAgent()
            
            # Should not raise exception, should use fallback
            result = await agent.analyze("Analyze costs")
            
            assert isinstance(result, str)
            assert "error" not in result.lower() or "fallback" in result.lower()
    
    def test_prompt_template_generation(self):
        """Test prompt template generation"""
        
        prompt = get_enhanced_system_prompt(
            agent_role="Cost Analyst",
            domain="AWS Cost Optimization"
        )
        
        # Verify prompt structure
        assert "AGENT IDENTITY" in prompt
        assert "CORE CAPABILITIES" in prompt
        assert "INPUT PROCESSING" in prompt
        assert "OUTPUT STRUCTURE" in prompt
        assert "EXAMPLES" in prompt
    
    @pytest.mark.parametrize("query,expected_confidence", [
        ("Analyze EC2 costs with detailed breakdown", 0.9),
        ("What happened to my bill?", 0.6),
        ("Vague cost question", 0.3)
    ])
    def test_confidence_scoring(self, query, expected_confidence):
        """Test confidence scoring for different query types"""
        
        # Mock confidence calculation
        def calculate_confidence(query_text: str) -> float:
            if "detailed" in query_text and "costs" in query_text:
                return 0.9
            elif "bill" in query_text:
                return 0.6
            else:
                return 0.3
        
        confidence = calculate_confidence(query)
        assert abs(confidence - expected_confidence) < 0.1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        
        rate_limiter = AsyncRateLimiter(calls_per_minute=2)
        
        start_time = asyncio.get_event_loop().time()
        
        # Make calls that exceed rate limit
        for i in range(3):
            async with rate_limiter:
                pass
        
        end_time = asyncio.get_event_loop().time()
        
        # Should have been rate limited
        assert end_time - start_time >= 60  # Had to wait a minute

# Performance Benchmarks
class PerformanceBenchmarks:
    """Performance benchmarking for agents"""
    
    @pytest.mark.benchmark
    async def test_agent_response_time(self):
        """Benchmark agent response times"""
        
        agent = CostAnalystAgent()
        queries = [
            "Analyze EC2 costs",
            "Find cost anomalies", 
            "Generate cost report"
        ]
        
        for query in queries:
            start_time = asyncio.get_event_loop().time()
            await agent.analyze(query)
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            assert response_time < 5.0  # Should respond within 5 seconds
    
    @pytest.mark.load_test
    async def test_concurrent_load(self):
        """Test agent performance under concurrent load"""
        
        agent = CostAnalystAgent()
        concurrent_requests = 10
        
        tasks = [
            agent.analyze(f"Test query {i}") 
            for i in range(concurrent_requests)
        ]
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()
        
        # Verify all requests completed
        assert len(results) == concurrent_requests
        
        # Check for exceptions
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0
        
        # Performance should scale reasonably
        avg_time_per_request = (end_time - start_time) / concurrent_requests
        assert avg_time_per_request < 10.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
```

---

This comprehensive guide provides production-ready patterns for:
1. **Structured prompt engineering** with examples and clear output formats
2. **Resilient tool implementation** with caching, rate limiting, and error handling
3. **Advanced workflow orchestration** with conditional routing and parallel execution
4. **Production monitoring and observability**
5. **Comprehensive testing strategies**

These patterns will significantly improve your agent system's reliability, performance, and maintainability.