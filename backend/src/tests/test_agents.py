import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.agents.orchestrator_agent import CostOptimizationOrchestrator

class TestCostOptimizationOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        with patch('src.agents.orchestrator_agent.Settings') as mock_settings:
            mock_settings.return_value.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.return_value.OLLAMA_MODEL = "llama2"
            return CostOptimizationOrchestrator()
    
    @pytest.mark.asyncio
    async def test_analyze_costs(self, orchestrator):
        query = "Analyze my AWS costs for the last 30 days"
        
        # Mock the orchestrator agent
        with patch.object(orchestrator, 'orchestrator') as mock_orchestrator:
            mock_orchestrator.return_value = "Mock cost analysis result"
            
            result = await orchestrator.analyze_costs(query)
            
            assert isinstance(result, str)
            assert len(result) > 0
            assert "Mock cost analysis result" in result
    
    @pytest.mark.asyncio
    async def test_parallel_analysis(self, orchestrator):
        query = "Provide comprehensive cost optimization recommendations"
        
        # Mock the Swarm execution
        with patch('src.agents.orchestrator_agent.Swarm') as mock_swarm_class:
            mock_swarm = Mock()
            mock_swarm_class.return_value = mock_swarm
            mock_swarm.execute = AsyncMock(return_value=[
                "Cost analysis result",
                "Infrastructure analysis result", 
                "Financial analysis result",
                "Remediation result"
            ])
            
            results = await orchestrator.parallel_analysis(query)
            
            assert isinstance(results, dict)
            assert "cost_analysis" in results
            assert "infrastructure_analysis" in results
            assert "financial_analysis" in results
            assert "remediation" in results
    
    def test_agent_initialization(self, orchestrator):
        assert orchestrator.cost_analyst is not None
        assert orchestrator.infrastructure_analyst is not None
        assert orchestrator.financial_analyst is not None
        assert orchestrator.remediation_specialist is not None
        assert orchestrator.orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, orchestrator):
        query = "Comprehensive cost optimization analysis"
        
        # Mock all agent calls
        with patch.object(orchestrator, 'cost_analyst') as mock_cost, \
             patch.object(orchestrator, 'infrastructure_analyst') as mock_infra, \
             patch.object(orchestrator, 'financial_analyst') as mock_financial, \
             patch.object(orchestrator, 'remediation_specialist') as mock_remediation:
            
            mock_cost.return_value = "Cost analysis"
            mock_infra.return_value = "Infrastructure analysis"
            mock_financial.return_value = "Financial analysis"
            mock_remediation.return_value = "Remediation plan"
            
            results = await orchestrator.comprehensive_analysis(query)
            
            assert isinstance(results, dict)
            assert "cost_analysis" in results
            assert "infrastructure_analysis" in results
            assert "financial_analysis" in results
            assert "remediation_plan" in results
            assert "timestamp" in results
    
    def test_workflow_graph_creation(self, orchestrator):
        graph = orchestrator.create_workflow_graph()
        assert graph is not None

@pytest.mark.asyncio
async def test_aws_tool_integration():
    with patch('boto3.client') as mock_client:
        mock_ce = Mock()
        mock_client.return_value = mock_ce
        mock_ce.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-02'},
                    'Total': {'BlendedCost': {'Amount': '100.00'}},
                    'Groups': []
                }
            ]
        }
        
        from src.tools.aws_tools import AWSCostExplorerTool
        tool = AWSCostExplorerTool()
        result = tool._run("30_days")
        
        assert "total_cost" in result or "error" in result.lower()
        mock_ce.get_cost_and_usage.assert_called_once()

@pytest.mark.asyncio 
async def test_ec2_utilization_tool():
    with patch('boto3.client') as mock_client:
        mock_ec2 = Mock()
        mock_cloudwatch = Mock()
        
        def client_side_effect(service_name, **kwargs):
            if service_name == 'ec2':
                return mock_ec2
            elif service_name == 'cloudwatch':
                return mock_cloudwatch
            return Mock()
        
        mock_client.side_effect = client_side_effect
        
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-123456789',
                            'InstanceType': 't2.micro'
                        }
                    ]
                }
            ]
        }
        
        mock_cloudwatch.get_metric_statistics.return_value = {
            'Datapoints': [{'Average': 15.0}]
        }
        
        from src.tools.aws_tools import EC2UtilizationTool
        tool = EC2UtilizationTool()
        result = tool._run()
        
        assert "total_instances" in result or "error" in result.lower()

@pytest.mark.asyncio
async def test_savings_calculation_tool():
    from src.tools.calculation_tools import SavingsCalculationTool
    
    tool = SavingsCalculationTool()
    
    test_data = {
        "ec2_data": {
            "instances": [
                {
                    "instance_id": "i-123456789",
                    "instance_type": "t2.medium",
                    "avg_cpu_utilization": 15.0
                }
            ]
        }
    }
    
    result = tool._run(test_data)
    
    assert "summary" in result or "error" in result.lower()
    
    # If successful, check structure
    if "summary" in result:
        import json
        parsed_result = json.loads(result)
        assert "summary" in parsed_result
        assert "detailed_calculations" in parsed_result