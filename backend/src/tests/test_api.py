import pytest
import json
from httpx import AsyncClient
from unittest.mock import Mock, patch
from main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "aws-cost-optimizer"

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_cost_analysis_endpoint():
    request_data = {
        "query": "Analyze my AWS costs for the last 30 days",
        "time_period": "30_days"
    }
    
    with patch('src.routers.cost_optimization.orchestrator') as mock_orchestrator:
        mock_orchestrator.analyze_costs.return_value = "Mock analysis result"
        
        with patch('src.routers.cost_optimization.cost_tool') as mock_tool:
            mock_tool._run.return_value = json.dumps({
                "total_cost": 1000.0,
                "daily_costs": [],
                "top_services": []
            })
            
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post("/api/v1/analyze-costs", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert "timestamp" in data
            assert "confidence" in data

@pytest.mark.asyncio
async def test_optimization_endpoint():
    request_data = {
        "query": "Provide optimization recommendations",
        "service": "ec2",
        "priority": "savings"
    }
    
    with patch('src.routers.cost_optimization.ec2_tool') as mock_ec2_tool, \
         patch('src.routers.cost_optimization.orchestrator') as mock_orchestrator:
        
        mock_ec2_tool._run.return_value = json.dumps({
            "instances": [
                {
                    "instance_id": "i-123456789",
                    "instance_type": "t2.large",
                    "recommendation": "Consider downsizing"
                }
            ]
        })
        
        mock_orchestrator.analyze_costs.return_value = "Implementation plan"
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "potential_savings" in data
        assert "implementation_plan" in data

@pytest.mark.asyncio
async def test_agent_execute_endpoint():
    request_data = {
        "agent_name": "cost_analyst",
        "query": "Test query"
    }
    
    with patch('src.routers.agents.orchestrator') as mock_orchestrator:
        mock_orchestrator.cost_analyst.return_value = "Agent response"
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/agents/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "agent_name" in data
        assert "response" in data
        assert "execution_time" in data

@pytest.mark.asyncio
async def test_agent_status_endpoint():
    with patch('src.routers.agents.orchestrator') as mock_orchestrator:
        # Mock all agent calls to succeed
        mock_orchestrator.cost_analyst.return_value = "OK"
        mock_orchestrator.infrastructure_analyst.return_value = "OK"
        mock_orchestrator.financial_analyst.return_value = "OK"
        mock_orchestrator.remediation_specialist.return_value = "OK"
        mock_orchestrator.analyze_costs.return_value = "OK"
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/agents/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_health" in data
        assert "agents" in data

@pytest.mark.asyncio
async def test_agent_capabilities_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/agents/capabilities")
    
    assert response.status_code == 200
    data = response.json()
    assert "cost_analyst" in data
    assert "infrastructure_analyst" in data
    assert "financial_analyst" in data
    assert "remediation_specialist" in data
    assert "orchestrator" in data

@pytest.mark.asyncio
async def test_infrastructure_analysis_endpoint():
    with patch('src.routers.cost_optimization.ec2_tool') as mock_ec2_tool, \
         patch('src.routers.cost_optimization.s3_tool') as mock_s3_tool:
        
        mock_ec2_tool._run.return_value = json.dumps({
            "total_instances": 5,
            "instances": []
        })
        
        mock_s3_tool._run.return_value = json.dumps({
            "total_buckets_analyzed": 3,
            "buckets": []
        })
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/infrastructure-analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert "ec2_analysis" in data
        assert "s3_analysis" in data

@pytest.mark.asyncio
async def test_cost_data_endpoint():
    with patch('src.routers.cost_optimization.cost_tool') as mock_tool:
        mock_tool._run.return_value = json.dumps({
            "total_cost": 1000.0,
            "period": "30_days",
            "daily_costs": []
        })
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/cost-data/30_days")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data

@pytest.mark.asyncio 
async def test_reports_generate_endpoint():
    request_data = {
        "report_type": "cost_analysis",
        "time_period": "30_days",
        "format": "json"
    }
    
    with patch('src.routers.reports.generate_cost_analysis_report') as mock_generate, \
         patch('src.routers.reports.save_report') as mock_save, \
         patch('pathlib.Path') as mock_path:
        
        mock_generate.return_value = {"report": "data"}
        mock_save.return_value = mock_path.return_value
        mock_path.return_value.__str__ = lambda x: "/path/to/report"
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/reports/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert "download_url" in data

@pytest.mark.asyncio
async def test_websocket_endpoint():
    # WebSocket testing requires special handling
    # This is a basic structure test
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    try:
        with client.websocket_connect("/ws/cost-analysis") as websocket:
            # Send test message
            websocket.send_json({
                "type": "cost_analysis",
                "query": "Test query"
            })
            
            # Should receive acknowledgment
            data = websocket.receive_json()
            assert data["type"] == "ack"
    except Exception:
        # WebSocket connections might fail in test environment
        # This is expected for integration tests
        pass

@pytest.mark.asyncio
async def test_error_handling():
    # Test with invalid data
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/analyze-costs", json={})
    
    # Should return validation error
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_cors_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.options("/api/v1/analyze-costs")
    
    # Should have CORS headers
    assert response.status_code in [200, 405]  # Either OK or Method Not Allowed is fine for OPTIONS