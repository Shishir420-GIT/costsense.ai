# 📡 API Documentation

## Overview

The CostSense AI platform provides a comprehensive RESTful API and WebSocket interface for AWS cost optimization. The API is built with FastAPI and includes automatic OpenAPI documentation.

**Base URL**: `http://localhost:8000` (development)
**WebSocket URL**: `ws://localhost:8000/ws`

## Authentication

Currently, the API operates in development mode without authentication. For production deployment, implement JWT-based authentication.

## API Endpoints

### Health & Status

#### GET /health
System health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "aws-cost-optimizer",
  "version": "1.0.0",
  "dependencies": {
    "ollama": "connected",
    "aws": "connected"
  }
}
```

#### GET /
Root endpoint with basic information.

**Response:**
```json
{
  "message": "AWS Cost Optimization Platform API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Cost Optimization

#### POST /api/v1/analyze-costs
Perform AI-powered cost analysis.

**Request Body:**
```json
{
  "query": "Analyze my AWS costs for the last 30 days",
  "time_period": "30_days",
  "services": ["EC2", "S3", "RDS"]
}
```

**Response:**
```json
{
  "analysis": "Detailed AI analysis of your costs...",
  "timestamp": "2024-01-15T10:30:00Z",
  "confidence": "High"
}
```

#### POST /api/v1/optimize
Get optimization recommendations.

**Request Body:**
```json
{
  "query": "Optimize my EC2 instances",
  "service": "ec2",
  "priority": "savings"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "service": "EC2",
      "resource": "i-1234567890abcdef0",
      "recommendation": "Downsize to t3.medium",
      "potential_savings": 45.00,
      "confidence": "High"
    }
  ],
  "potential_savings": 150.00,
  "implementation_plan": "Detailed implementation steps...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/v1/cost-data/{time_period}
Retrieve raw cost data.

**Parameters:**
- `time_period`: "7_days", "30_days", "90_days"

**Response:**
```json
{
  "total_cost": 1250.75,
  "period": "30_days",
  "daily_costs": [
    {"date": "2024-01-01", "cost": 42.50},
    {"date": "2024-01-02", "cost": 38.75}
  ],
  "top_services": [
    ["EC2-Instance", 450.00],
    ["S3", 125.50]
  ]
}
```

#### GET /api/v1/infrastructure-analysis
Get comprehensive infrastructure analysis.

**Response:**
```json
{
  "ec2_analysis": {
    "total_instances": 12,
    "instances": [
      {
        "instance_id": "i-1234567890abcdef0",
        "instance_type": "t3.large",
        "avg_cpu_utilization": 15.5,
        "recommendation": "Consider downsizing"
      }
    ],
    "underutilized_count": 8,
    "potential_monthly_savings": 200.00
  },
  "s3_analysis": {
    "total_buckets_analyzed": 5,
    "total_size_gb": 1024.5,
    "buckets": [
      {
        "bucket_name": "my-data-bucket",
        "size_gb": 512.25,
        "recommendations": ["Implement lifecycle policies"]
      }
    ]
  }
}
```

#### POST /api/v1/calculate-savings
Calculate potential savings from optimizations.

**Request Body:**
```json
{
  "ec2_data": {
    "instances": [...]
  },
  "s3_data": {
    "buckets": [...]
  }
}
```

**Response:**
```json
{
  "summary": {
    "total_monthly_savings": 250.00,
    "total_annual_savings": 3000.00,
    "confidence_level": "High"
  },
  "detailed_calculations": [...],
  "roi_analysis": {
    "implementation_cost": 300.00,
    "payback_period_months": 1.2,
    "three_year_savings": 9000.00,
    "three_year_roi_percentage": 2900.0
  }
}
```

### Agent Management

#### POST /api/v1/agents/execute
Execute a specific agent.

**Request Body:**
```json
{
  "agent_name": "cost_analyst",
  "query": "Analyze spending patterns",
  "context": {}
}
```

**Response:**
```json
{
  "agent_name": "cost_analyst",
  "response": "Analysis results...",
  "execution_time": 2.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST /api/v1/agents/multi-agent
Execute multiple agents.

**Request Body:**
```json
{
  "query": "Comprehensive analysis",
  "mode": "parallel"
}
```

**Response:**
```json
{
  "results": {
    "cost_analysis": "Cost analysis results...",
    "infrastructure_analysis": "Infrastructure results...",
    "financial_analysis": "Financial calculations...",
    "remediation": "Action plan..."
  },
  "execution_time": 5.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/v1/agents/status
Get agent health status.

**Response:**
```json
{
  "overall_health": "healthy",
  "agents": {
    "cost_analyst": "healthy",
    "infrastructure_analyst": "healthy",
    "financial_analyst": "healthy",
    "remediation_specialist": "healthy",
    "orchestrator": "healthy"
  },
  "healthy_agents": 5,
  "total_agents": 5
}
```

#### GET /api/v1/agents/capabilities
Get agent capabilities and descriptions.

**Response:**
```json
{
  "cost_analyst": {
    "description": "AWS Cost Analysis Expert",
    "capabilities": [
      "Historical spending analysis",
      "Cost trend identification",
      "Service-level cost breakdown"
    ],
    "tools": ["aws_cost_explorer", "memory"]
  }
}
```

### Reports

#### POST /api/v1/reports/generate
Generate cost optimization report.

**Request Body:**
```json
{
  "report_type": "comprehensive",
  "time_period": "30_days",
  "format": "json",
  "include_recommendations": true,
  "email_recipients": ["admin@company.com"]
}
```

**Response:**
```json
{
  "report_id": "report_20240115_103000",
  "report_path": "/reports/report_20240115_103000.json",
  "format": "json",
  "generated_at": "2024-01-15T10:30:00Z",
  "download_url": "/api/v1/reports/download/report_20240115_103000"
}
```

#### GET /api/v1/reports/download/{report_id}
Download generated report.

**Response:** File download (JSON, CSV, or PDF)

#### GET /api/v1/reports/list
List all generated reports.

**Response:**
```json
{
  "reports": [
    {
      "filename": "report_20240115_103000.json",
      "size_bytes": 15420,
      "created_at": "2024-01-15T10:30:00Z",
      "modified_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_reports": 1
}
```

## WebSocket API

### Connection

Connect to: `ws://localhost:8000/ws/cost-analysis`

### Message Format

All WebSocket messages follow this format:

```json
{
  "type": "message_type",
  "query": "user query",
  "service": "optional_service"
}
```

### Message Types

#### cost_analysis
Request cost analysis with real-time updates.

**Send:**
```json
{
  "type": "cost_analysis",
  "query": "Analyze my AWS costs"
}
```

**Receive:**
```json
{
  "type": "status",
  "message": "🔍 Analyzing AWS costs...",
  "progress": 10
}
```

#### optimization_request
Request optimization recommendations.

**Send:**
```json
{
  "type": "optimization_request",
  "query": "Optimize my infrastructure",
  "service": "ec2"
}
```

#### parallel_analysis
Run multiple agents in parallel.

**Send:**
```json
{
  "type": "parallel_analysis",
  "query": "Comprehensive analysis"
}
```

#### comprehensive_analysis
Full end-to-end analysis with all agents.

**Send:**
```json
{
  "type": "comprehensive_analysis",
  "query": "Complete optimization analysis"
}
```

### Response Message Types

#### ack
Acknowledgment that message was received.

```json
{
  "type": "ack",
  "message": "Request received, starting analysis..."
}
```

#### status
Progress update with current status.

```json
{
  "type": "status",
  "message": "🔍 Analyzing costs...",
  "progress": 25
}
```

#### agent_stream
Streaming response from an agent.

```json
{
  "type": "agent_stream",
  "agent": "cost_analyst",
  "content": "Current analysis shows...",
  "is_complete": false,
  "progress": 0.75
}
```

#### agent_result
Complete result from a specific agent.

```json
{
  "type": "agent_result",
  "agent": "cost_analyst",
  "result": "Complete analysis results..."
}
```

#### analysis_complete
Final analysis results.

```json
{
  "type": "analysis_complete",
  "result": "Final comprehensive results...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### error
Error message.

```json
{
  "type": "error",
  "message": "Analysis failed: connection timeout"
}
```

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **422**: Validation Error (invalid request body)
- **500**: Internal Server Error
- **503**: Service Unavailable (dependencies offline)

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {
    "field": "Additional error details"
  }
}
```

## Rate Limiting

Current rate limits (development):
- **General API**: 100 requests/minute
- **WebSocket**: 10 connections/IP
- **Report Generation**: 5 reports/hour

## Examples

### Python Client Example

```python
import requests
import asyncio
import websockets
import json

# REST API Example
def analyze_costs():
    response = requests.post(
        "http://localhost:8000/api/v1/analyze-costs",
        json={
            "query": "Analyze my costs",
            "time_period": "30_days"
        }
    )
    return response.json()

# WebSocket Example
async def websocket_analysis():
    uri = "ws://localhost:8000/ws/cost-analysis"
    
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "type": "cost_analysis",
            "query": "Analyze my infrastructure"
        }))
        
        # Listen for responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
            
            if data["type"] == "analysis_complete":
                break
```

### JavaScript/TypeScript Example

```typescript
// REST API Example
const analyzeCosts = async () => {
  const response = await fetch('/api/v1/analyze-costs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: 'Analyze my costs',
      time_period: '30_days'
    })
  });
  return response.json();
};

// WebSocket Example
const ws = new WebSocket('ws://localhost:8000/ws/cost-analysis');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'cost_analysis',
    query: 'Analyze my infrastructure'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json