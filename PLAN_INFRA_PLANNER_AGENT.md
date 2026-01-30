# Infrastructure Planner Agent - Implementation Plan

## Executive Summary

Integrate VizCode's infrastructure diagram generation capabilities into CostSense-AI as a new "Infra Planner" agent, migrating from AWS-focused to Azure-focused architecture visualization using the existing Ollama LLM.

## Current State Analysis

### VizCode Current Architecture
- **Location**: `/Users/shishir/Workspace/Project/CostSense-AI/VizCode`
- **Tech Stack**: React + Express.js + OpenAI/Gemini
- **Focus**: AWS infrastructure diagrams with multi-cloud support
- **Components**: Monaco Editor, SVG rendering, DSL parser, icon library (751+ icons)

### CostSense-AI Current Architecture
- **Backend**: FastAPI + Python (port 8000)
- **Frontend**: React + TypeScript + Vite (port 3000)
- **LLM**: Ollama (llama3.2:latest on port 11434)
- **Agents**: Cost, Infrastructure, Financial, Optimization (using LangChain ReAct pattern)

## Integration Strategy

### Option 1: Native Python Integration (Recommended)
**Approach**: Rebuild VizCode's core logic in Python within FastAPI backend

**Pros**:
- Single unified backend (FastAPI)
- Use existing Ollama LLM infrastructure
- Consistent with other agents
- No dual server complexity
- Better performance (no HTTP proxy)

**Cons**:
- More initial development work
- Need to port DSL parser to Python
- SVG generation logic rewrite

### Option 2: Hybrid Integration
**Approach**: Keep VizCode Express backend, proxy through FastAPI

**Pros**:
- Faster initial integration
- Reuse existing VizCode backend
- Less code to write

**Cons**:
- Dual backend complexity
- Two LLM systems (Ollama + OpenAI/Gemini)
- Additional port management
- Harder to maintain

**Decision**: **Option 1 - Native Python Integration** for better long-term maintainability and consistency.

## Implementation Plan

### Phase 1: Agent Core Structure (Day 1)

#### 1.1 Create InfraPlannerAgent Class
**File**: `/backend/src/agents_langchain/infra_planner.py`

```python
"""Infrastructure Planner Agent - Azure Architecture Diagrams"""

from typing import Dict, Any, Optional, List
import json
import logging
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from src.agents_langchain.tools import INFRA_PLANNER_TOOLS

logger = logging.getLogger(__name__)

class InfraPlannerAgent:
    """
    Azure Infrastructure Planning Agent

    Responsibilities:
    - Generate Azure architecture diagrams
    - Suggest optimal resource configurations
    - Create infrastructure-as-code blueprints
    - Visualize resource relationships
    """

    def __init__(self):
        """Initialize the infrastructure planner agent"""
        try:
            self.llm = ChatOllama(
                model="llama3.2:latest",
                temperature=0.3,  # Slightly higher for creative diagrams
            )
            self.llm.invoke("test")
            self.llm_available = True
            logger.info("Infra Planner Agent initialized with Ollama")
        except Exception as e:
            self.llm = None
            self.llm_available = False
            logger.warning(f"Ollama unavailable, using fallback: {e}")

        self.system_prompt = """You are an Azure Infrastructure Planning Expert.

Your role is to help design and visualize Azure cloud architectures.

When planning infrastructure:
1. Understand the requirements (workload type, scale, compliance)
2. Suggest appropriate Azure services
3. Design optimal architecture patterns
4. Generate DSL code for visualization
5. Provide cost estimates and best practices

Available Azure Services:
- Compute: VMs, App Service, Container Instances, AKS, Functions
- Storage: Blob Storage, File Storage, Disk Storage, Data Lake
- Database: SQL Database, Cosmos DB, PostgreSQL, MySQL
- Networking: Virtual Network, Load Balancer, Application Gateway, VPN Gateway
- Security: Key Vault, Security Center, Azure AD
- Monitoring: Application Insights, Log Analytics, Monitor

Output Format:
1. Architecture overview (text description)
2. DSL code for diagram visualization
3. Cost estimation
4. Implementation recommendations
"""

    async def plan(self, query: str) -> Dict[str, Any]:
        """
        Generate infrastructure plan and diagram

        Args:
            query: User's infrastructure requirements

        Returns:
            {
                "description": "Architecture overview",
                "dsl_code": "Diagram DSL code",
                "services": ["Azure service list"],
                "estimated_monthly_cost": 1234.56,
                "recommendations": ["Best practice suggestions"]
            }
        """
        if not self.llm_available:
            return self._fallback_plan(query)

        try:
            # Create LLM with tools
            llm_with_tools = self.llm.bind_tools(INFRA_PLANNER_TOOLS)

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
User Requirements: {query}

Generate an Azure infrastructure plan with:
1. Text description of the architecture
2. DSL code for diagram (use Azure service syntax)
3. List of Azure services used
4. Estimated monthly cost
5. Implementation recommendations
""")
            ]

            # ReAct loop
            max_iterations = 5
            for i in range(max_iterations):
                response = await llm_with_tools.ainvoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    # Parse LLM response into structured format
                    return self._parse_plan_response(response.content)

                # Execute tools
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    tool = next((t for t in INFRA_PLANNER_TOOLS if t.name == tool_name), None)
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

            # Fallback if max iterations reached
            return self._parse_plan_response(messages[-1].content if messages else "")

        except Exception as e:
            logger.error(f"Infrastructure planning failed: {e}")
            return self._fallback_plan(query)

    def _parse_plan_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured plan"""
        # TODO: Implement parser for LLM response
        # Extract DSL code blocks, services, costs, etc.
        return {
            "description": content,
            "dsl_code": "# DSL code will be extracted here",
            "services": [],
            "estimated_monthly_cost": 0.0,
            "recommendations": []
        }

    def _fallback_plan(self, query: str) -> Dict[str, Any]:
        """Fallback when LLM unavailable"""
        return {
            "description": f"Infrastructure plan for: {query}",
            "dsl_code": "# LLM unavailable - DSL generation requires Ollama",
            "services": ["Virtual Machines", "Virtual Network", "Storage Account"],
            "estimated_monthly_cost": 500.00,
            "recommendations": [
                "Enable Azure Security Center",
                "Configure backup policies",
                "Use managed identities for authentication"
            ]
        }

# Singleton instance
infra_planner = InfraPlannerAgent()
```

#### 1.2 Create Infrastructure Planner Tools
**File**: `/backend/src/agents_langchain/tools/infra_planner_tools.py`

```python
"""Infrastructure Planner Tools"""

from langchain.tools import tool
from typing import Dict, Any, List

@tool
def generate_azure_architecture_dsl(requirements: str) -> str:
    """
    Generate Azure architecture diagram DSL code

    Args:
        requirements: Infrastructure requirements description

    Returns:
        DSL code string for diagram visualization
    """
    # TODO: Implement DSL generator
    return "# Azure Architecture DSL"

@tool
def estimate_azure_costs(services: List[str]) -> Dict[str, Any]:
    """
    Estimate monthly costs for Azure services

    Args:
        services: List of Azure service names

    Returns:
        Cost breakdown by service
    """
    # TODO: Implement cost estimation
    return {
        "total_monthly_cost": 0.0,
        "breakdown": []
    }

@tool
def get_azure_service_recommendations(workload_type: str) -> List[str]:
    """
    Get Azure service recommendations for workload type

    Args:
        workload_type: Type of workload (web_app, data_pipeline, ml_training, etc.)

    Returns:
        List of recommended Azure services
    """
    recommendations = {
        "web_app": ["App Service", "SQL Database", "Application Insights", "CDN"],
        "data_pipeline": ["Data Factory", "Data Lake", "Databricks", "Event Hub"],
        "ml_training": ["Machine Learning", "Batch", "Storage Account", "Container Registry"],
        "microservices": ["AKS", "Container Instances", "Service Bus", "API Management"]
    }

    return recommendations.get(workload_type, ["Virtual Machines", "Virtual Network"])

@tool
def validate_azure_architecture(dsl_code: str) -> Dict[str, Any]:
    """
    Validate Azure architecture for best practices

    Args:
        dsl_code: DSL code to validate

    Returns:
        Validation results with warnings and suggestions
    """
    # TODO: Implement validation logic
    return {
        "valid": True,
        "warnings": [],
        "suggestions": []
    }

# Export tools list
INFRA_PLANNER_TOOLS = [
    generate_azure_architecture_dsl,
    estimate_azure_costs,
    get_azure_service_recommendations,
    validate_azure_architecture
]
```

#### 1.3 Update Tools Registry
**File**: `/backend/src/agents_langchain/tools/__init__.py`

```python
from .infra_planner_tools import INFRA_PLANNER_TOOLS

ALL_TOOLS = (
    COST_ANALYSIS_TOOLS +
    INFRASTRUCTURE_TOOLS +
    OPTIMIZATION_TOOLS +
    FINANCIAL_TOOLS +
    INFRA_PLANNER_TOOLS  # Add new tools
)
```

### Phase 2: DSL Parser & Generator (Day 2)

#### 2.1 Azure DSL Syntax Definition
**File**: `/backend/src/services/azure_dsl_parser.py`

```python
"""Azure Infrastructure DSL Parser"""

from typing import Dict, Any, List
import re

class AzureDSLParser:
    """
    Parser for Azure architecture DSL

    Syntax Example:
    ```
    # Define Azure resources
    vnet = VirtualNetwork("prod-vnet", "10.0.0.0/16")
    subnet = Subnet("app-subnet", "10.0.1.0/24", vnet)
    vm = VirtualMachine("web-vm", "Standard_D2s_v3", subnet)
    db = SQLDatabase("prod-db", "Standard_S1")
    storage = StorageAccount("prodsa", "Standard_LRS")

    # Define connections
    vm -> db
    vm -> storage
    ```
    """

    AZURE_SERVICES = {
        "VirtualMachine": {"category": "Compute", "icon": "azure-vm"},
        "AppService": {"category": "Compute", "icon": "azure-app-service"},
        "AKS": {"category": "Compute", "icon": "azure-kubernetes"},
        "Functions": {"category": "Compute", "icon": "azure-functions"},
        "VirtualNetwork": {"category": "Network", "icon": "azure-vnet"},
        "LoadBalancer": {"category": "Network", "icon": "azure-load-balancer"},
        "ApplicationGateway": {"category": "Network", "icon": "azure-app-gateway"},
        "SQLDatabase": {"category": "Database", "icon": "azure-sql"},
        "CosmosDB": {"category": "Database", "icon": "azure-cosmos"},
        "StorageAccount": {"category": "Storage", "icon": "azure-storage"},
        "BlobStorage": {"category": "Storage", "icon": "azure-blob"},
        "KeyVault": {"category": "Security", "icon": "azure-keyvault"},
    }

    def parse(self, dsl_code: str) -> Dict[str, Any]:
        """
        Parse DSL code into diagram structure

        Returns:
            {
                "resources": [{"id": "vm1", "type": "VirtualMachine", "name": "web-vm", "config": {...}}],
                "connections": [{"from": "vm1", "to": "db1"}],
                "groups": [{"name": "vnet", "resources": ["vm1", "db1"]}]
            }
        """
        resources = []
        connections = []
        groups = []

        # Parse resource definitions
        resource_pattern = r'(\w+)\s*=\s*(\w+)\((.*?)\)'
        for match in re.finditer(resource_pattern, dsl_code):
            var_name = match.group(1)
            service_type = match.group(2)
            args = match.group(3)

            if service_type in self.AZURE_SERVICES:
                resources.append({
                    "id": var_name,
                    "type": service_type,
                    "args": self._parse_args(args),
                    "icon": self.AZURE_SERVICES[service_type]["icon"]
                })

        # Parse connections
        connection_pattern = r'(\w+)\s*->\s*(\w+)'
        for match in re.finditer(connection_pattern, dsl_code):
            connections.append({
                "from": match.group(1),
                "to": match.group(2)
            })

        return {
            "resources": resources,
            "connections": connections,
            "groups": groups
        }

    def _parse_args(self, args_str: str) -> List[str]:
        """Parse function arguments"""
        # Simple CSV parsing (TODO: handle nested quotes)
        return [arg.strip().strip('"\'') for arg in args_str.split(',')]

    def generate_svg(self, diagram: Dict[str, Any]) -> str:
        """
        Generate SVG from diagram structure

        Args:
            diagram: Parsed diagram structure

        Returns:
            SVG markup string
        """
        # TODO: Implement SVG generation
        # Use layout algorithm (hierarchical, force-directed, etc.)
        return "<svg>...</svg>"

# Singleton
azure_dsl_parser = AzureDSLParser()
```

#### 2.2 DSL Generator from LLM
**File**: `/backend/src/services/azure_dsl_generator.py`

```python
"""Generate DSL code from natural language using LLM"""

from typing import Dict, Any
from langchain_ollama import ChatOllama

class AzureDSLGenerator:
    """Generate Azure architecture DSL from requirements"""

    def __init__(self):
        self.llm = ChatOllama(model="llama3.2:latest", temperature=0.2)

    async def generate(self, requirements: str) -> str:
        """
        Generate DSL code from requirements

        Args:
            requirements: Natural language infrastructure requirements

        Returns:
            DSL code string
        """
        prompt = f"""Convert these infrastructure requirements into Azure DSL code.

Requirements: {requirements}

Available Azure Services:
- VirtualMachine(name, size, subnet)
- AppService(name, plan, runtime)
- AKS(name, node_count, node_size)
- VirtualNetwork(name, cidr)
- Subnet(name, cidr, vnet)
- SQLDatabase(name, tier)
- CosmosDB(name, api)
- StorageAccount(name, tier)
- LoadBalancer(name, type)
- ApplicationGateway(name, tier)
- KeyVault(name)

Syntax:
```
resource_var = ServiceType(name, config...)
resource1 -> resource2  # Connection
```

Generate ONLY the DSL code, no explanations:"""

        response = await self.llm.ainvoke(prompt)

        # Extract code block
        content = response.content if hasattr(response, 'content') else str(response)

        # Extract from markdown code block if present
        if '```' in content:
            code_blocks = content.split('```')
            for block in code_blocks:
                if any(service in block for service in ['VirtualMachine', 'AppService', 'VirtualNetwork']):
                    return block.strip()

        return content.strip()

azure_dsl_generator = AzureDSLGenerator()
```

### Phase 3: API Endpoints (Day 3)

#### 3.1 Create Infrastructure Planner Router
**File**: `/backend/src/routers/infra_planner.py`

```python
"""Infrastructure Planner API Endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from src.agents_langchain.infra_planner import infra_planner
from src.services.azure_dsl_parser import azure_dsl_parser
from src.services.azure_dsl_generator import azure_dsl_generator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/infra-planner", tags=["Infrastructure Planner"])

class InfraPlanRequest(BaseModel):
    requirements: str
    existing_resources: Optional[Dict[str, Any]] = None

class InfraPlanResponse(BaseModel):
    description: str
    dsl_code: str
    svg_diagram: str
    services: list
    estimated_monthly_cost: float
    recommendations: list
    timestamp: str

class DSLParseRequest(BaseModel):
    dsl_code: str

class DSLParseResponse(BaseModel):
    diagram: Dict[str, Any]
    svg: str
    valid: bool
    errors: list

@router.post("/plan", response_model=InfraPlanResponse)
async def create_infrastructure_plan(request: InfraPlanRequest):
    """
    Generate Azure infrastructure plan from requirements

    - **requirements**: Natural language description of infrastructure needs
    - **existing_resources**: Optional dict of existing Azure resources
    """
    try:
        # Generate plan using agent
        plan = await infra_planner.plan(request.requirements)

        # Parse DSL and generate SVG
        diagram = azure_dsl_parser.parse(plan["dsl_code"])
        svg = azure_dsl_parser.generate_svg(diagram)

        return InfraPlanResponse(
            description=plan["description"],
            dsl_code=plan["dsl_code"],
            svg_diagram=svg,
            services=plan["services"],
            estimated_monthly_cost=plan["estimated_monthly_cost"],
            recommendations=plan["recommendations"],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Infrastructure planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-dsl", response_model=DSLParseResponse)
async def parse_dsl(request: DSLParseRequest):
    """
    Parse DSL code and generate diagram

    - **dsl_code**: Azure infrastructure DSL code
    """
    try:
        diagram = azure_dsl_parser.parse(request.dsl_code)
        svg = azure_dsl_parser.generate_svg(diagram)

        # Validate
        valid = len(diagram["resources"]) > 0
        errors = [] if valid else ["No valid resources found in DSL"]

        return DSLParseResponse(
            diagram=diagram,
            svg=svg,
            valid=valid,
            errors=errors
        )
    except Exception as e:
        logger.error(f"DSL parsing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/azure-services")
async def get_azure_services():
    """Get list of supported Azure services for DSL"""
    return {
        "services": list(azure_dsl_parser.AZURE_SERVICES.keys()),
        "categories": {
            "Compute": ["VirtualMachine", "AppService", "AKS", "Functions"],
            "Network": ["VirtualNetwork", "LoadBalancer", "ApplicationGateway"],
            "Database": ["SQLDatabase", "CosmosDB"],
            "Storage": ["StorageAccount", "BlobStorage"],
            "Security": ["KeyVault"]
        }
    }
```

#### 3.2 Register Router
**File**: `/backend/src/main.py`

```python
from src.routers import infra_planner

# Add to app
app.include_router(infra_planner.router)
```

### Phase 4: Frontend Integration (Day 4)

#### 4.1 Create InfraPlanner Page
**File**: `/frontend/src/pages/InfraPlanner.tsx`

```typescript
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Network, Loader2, Download } from 'lucide-react';

interface InfraPlan {
  description: string;
  dsl_code: string;
  svg_diagram: string;
  services: string[];
  estimated_monthly_cost: number;
  recommendations: string[];
}

export default function InfraPlanner() {
  const [requirements, setRequirements] = useState('');
  const [plan, setPlan] = useState<InfraPlan | null>(null);
  const [loading, setLoading] = useState(false);

  const generatePlan = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/infra-planner/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements })
      });

      const data = await response.json();
      setPlan(data);
    } catch (error) {
      console.error('Failed to generate plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadSVG = () => {
    if (!plan) return;

    const blob = new Blob([plan.svg_diagram], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'azure-architecture.svg';
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-ey-black flex items-center gap-3">
            <Network className="h-8 w-8 text-ey-yellow" />
            Azure Infrastructure Planner
          </h1>
          <p className="text-gray-600 mt-2">
            Describe your infrastructure requirements and get an optimized Azure architecture
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <Card className="shadow-lg">
            <CardHeader className="bg-gradient-to-r from-ey-black to-ey-black-light text-ey-yellow">
              <CardTitle>Requirements</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <Textarea
                placeholder="Describe your infrastructure needs...

Example:
I need a web application with:
- High availability web tier (3 instances)
- SQL database with read replicas
- Blob storage for static assets
- Load balancer
- Application monitoring"
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
                className="min-h-[300px] font-mono text-sm"
              />

              <Button
                onClick={generatePlan}
                disabled={loading || !requirements.trim()}
                className="mt-4 w-full bg-ey-yellow text-ey-black hover:bg-ey-yellow-dark font-semibold"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Plan...
                  </>
                ) : (
                  'Generate Architecture Plan'
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Output Section */}
          <Card className="shadow-lg">
            <CardHeader className="bg-gradient-to-r from-ey-black to-ey-black-light text-ey-yellow">
              <CardTitle className="flex items-center justify-between">
                <span>Architecture Diagram</span>
                {plan && (
                  <Button
                    onClick={downloadSVG}
                    size="sm"
                    variant="outline"
                    className="text-ey-yellow border-ey-yellow hover:bg-ey-yellow hover:text-ey-black"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download SVG
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {!plan && !loading && (
                <div className="flex items-center justify-center h-[300px] text-gray-400">
                  Enter requirements and click Generate to see your architecture
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center h-[300px]">
                  <Loader2 className="h-12 w-12 animate-spin text-ey-yellow" />
                </div>
              )}

              {plan && (
                <div
                  className="border rounded-lg p-4 bg-white overflow-auto"
                  dangerouslySetInnerHTML={{ __html: plan.svg_diagram }}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Plan Details */}
        {plan && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Description & Services */}
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Architecture Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700">{plan.description}</p>

                  <h4 className="text-ey-black mt-4">Azure Services Used:</h4>
                  <ul className="list-disc list-inside">
                    {plan.services.map((service, idx) => (
                      <li key={idx} className="text-gray-600">{service}</li>
                    ))}
                  </ul>

                  <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="text-sm font-semibold text-ey-black">
                      Estimated Monthly Cost: <span className="text-2xl">${plan.estimated_monthly_cost.toFixed(2)}</span>
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* DSL Code & Recommendations */}
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>DSL Code</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs font-mono">
                  {plan.dsl_code}
                </pre>

                <h4 className="text-ey-black mt-6 mb-2 font-semibold">Recommendations:</h4>
                <ul className="space-y-2">
                  {plan.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-ey-yellow mt-1">✓</span>
                      <span className="text-gray-700 text-sm">{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
```

#### 4.2 Add Route
**File**: `/frontend/src/App.tsx`

```typescript
import InfraPlanner from './pages/InfraPlanner';

// Add to routes
<Route path="/infra-planner" element={<InfraPlanner />} />
```

#### 4.3 Add Navigation Link
**File**: `/frontend/src/components/Layout.tsx` (or wherever navigation is)

```typescript
<NavLink to="/infra-planner" className="nav-link">
  <Network className="h-5 w-5" />
  <span>Infra Planner</span>
</NavLink>
```

### Phase 5: Azure Icon Integration (Day 5)

#### 5.1 Copy Azure Icons from VizCode
**Location**: `/VizCode/public/icons/Azure/`

**Action**: Copy all Azure icons to `/frontend/public/icons/azure/`

```bash
cp -r /Users/shishir/Workspace/Project/CostSense-AI/VizCode/public/icons/Azure/* \
     /Users/shishir/Workspace/Project/CostSense-AI/frontend/public/icons/azure/
```

#### 5.2 Create Icon Mapping
**File**: `/frontend/src/utils/azureIcons.ts`

```typescript
export const AZURE_ICONS: Record<string, string> = {
  'azure-vm': '/icons/azure/Virtual-Machine.svg',
  'azure-app-service': '/icons/azure/App-Service.svg',
  'azure-kubernetes': '/icons/azure/Kubernetes-Service.svg',
  'azure-functions': '/icons/azure/Function-Apps.svg',
  'azure-vnet': '/icons/azure/Virtual-Networks.svg',
  'azure-load-balancer': '/icons/azure/Load-Balancer.svg',
  'azure-app-gateway': '/icons/azure/Application-Gateway.svg',
  'azure-sql': '/icons/azure/SQL-Database.svg',
  'azure-cosmos': '/icons/azure/Cosmos-DB.svg',
  'azure-storage': '/icons/azure/Storage-Accounts.svg',
  'azure-blob': '/icons/azure/Blob-Storage.svg',
  'azure-keyvault': '/icons/azure/Key-Vault.svg',
  // Add more mappings...
};

export function getAzureIcon(serviceName: string): string {
  return AZURE_ICONS[serviceName] || '/icons/azure/default.svg';
}
```

### Phase 6: Testing & Refinement (Day 6)

#### 6.1 Unit Tests
**File**: `/backend/tests/test_infra_planner.py`

```python
import pytest
from src.agents_langchain.infra_planner import infra_planner
from src.services.azure_dsl_parser import azure_dsl_parser

@pytest.mark.asyncio
async def test_infra_planner_basic():
    """Test basic infrastructure planning"""
    query = "I need a simple web app with database"
    result = await infra_planner.plan(query)

    assert "description" in result
    assert "dsl_code" in result
    assert len(result["services"]) > 0

def test_dsl_parser():
    """Test DSL parsing"""
    dsl = """
    vnet = VirtualNetwork("prod-vnet", "10.0.0.0/16")
    vm = VirtualMachine("web-vm", "Standard_D2s_v3", vnet)
    db = SQLDatabase("prod-db", "Standard_S1")
    vm -> db
    """

    diagram = azure_dsl_parser.parse(dsl)

    assert len(diagram["resources"]) == 3
    assert len(diagram["connections"]) == 1
    assert diagram["connections"][0]["from"] == "vm"
    assert diagram["connections"][0]["to"] == "db"
```

#### 6.2 Integration Tests
**File**: `/backend/tests/test_infra_planner_api.py`

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_plan_endpoint():
    """Test /api/v1/infra-planner/plan endpoint"""
    response = client.post(
        "/api/v1/infra-planner/plan",
        json={"requirements": "Web app with database"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "dsl_code" in data
    assert "svg_diagram" in data

def test_parse_dsl_endpoint():
    """Test /api/v1/infra-planner/parse-dsl endpoint"""
    dsl_code = 'vm = VirtualMachine("test-vm", "Standard_B2s")'

    response = client.post(
        "/api/v1/infra-planner/parse-dsl",
        json={"dsl_code": dsl_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert len(data["diagram"]["resources"]) == 1
```

### Phase 7: Documentation (Day 7)

#### 7.1 API Documentation
**File**: `/docs/INFRA_PLANNER_API.md`

```markdown
# Infrastructure Planner API

## Endpoints

### POST /api/v1/infra-planner/plan
Generate Azure infrastructure plan from requirements

**Request:**
```json
{
  "requirements": "I need a web app with HA, database, and storage",
  "existing_resources": {} // optional
}
```

**Response:**
```json
{
  "description": "Architecture overview...",
  "dsl_code": "vnet = VirtualNetwork(...)",
  "svg_diagram": "<svg>...</svg>",
  "services": ["App Service", "SQL Database", "Storage Account"],
  "estimated_monthly_cost": 450.00,
  "recommendations": ["Enable auto-scaling", "..."],
  "timestamp": "2025-12-07T10:30:00Z"
}
```

### POST /api/v1/infra-planner/parse-dsl
Parse DSL code and generate diagram

### GET /api/v1/infra-planner/azure-services
Get list of supported Azure services
```

#### 7.2 User Guide
**File**: `/docs/INFRA_PLANNER_USER_GUIDE.md`

```markdown
# Infrastructure Planner User Guide

## Getting Started

1. Navigate to **Infra Planner** in the sidebar
2. Describe your infrastructure requirements in natural language
3. Click **Generate Architecture Plan**
4. Review the generated diagram and recommendations

## Example Requirements

### Web Application
```
I need a production web application with:
- High availability (3 instances minimum)
- SQL database with read replicas
- Blob storage for user uploads
- Content delivery network
- Application monitoring
```

### Data Pipeline
```
Build a data processing pipeline with:
- Event ingestion from multiple sources
- Data lake for raw storage
- Databricks for processing
- SQL database for analytics
- Power BI integration
```

## DSL Syntax

The Infrastructure Planner uses a simple DSL:

```python
# Define resources
vnet = VirtualNetwork("prod-vnet", "10.0.0.0/16")
subnet = Subnet("app-subnet", "10.0.1.0/24", vnet)
vm = VirtualMachine("web-vm", "Standard_D2s_v3", subnet)
db = SQLDatabase("prod-db", "Standard_S1")

# Define connections
vm -> db
```

## Best Practices

1. **Be Specific**: Include scale requirements, compliance needs, etc.
2. **Review Costs**: Check estimated monthly costs before implementation
3. **Follow Recommendations**: The planner suggests Azure best practices
4. **Iterate**: Refine requirements based on initial plan
```

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 1. Agent Core | 1 day | InfraPlannerAgent, tools, routing |
| 2. DSL Parser | 1 day | Parser, generator, SVG renderer |
| 3. API Endpoints | 1 day | FastAPI routes, request/response models |
| 4. Frontend | 1 day | InfraPlanner page, navigation |
| 5. Icons | 0.5 days | Azure icon integration |
| 6. Testing | 1 day | Unit tests, integration tests |
| 7. Documentation | 0.5 days | API docs, user guide |

**Total: 6 days**

## Success Metrics

- ✅ Generate valid Azure architecture diagrams from natural language
- ✅ Parse and visualize custom DSL code
- ✅ Provide accurate cost estimates (±15% of actual)
- ✅ Render diagrams in <2 seconds
- ✅ Support 20+ Azure services
- ✅ Integration with existing Ollama LLM
- ✅ Clickable UI integration from sidebar

## Technical Debt & Future Enhancements

### Future Features (Post-MVP)
1. **Terraform Export**: Generate Terraform .tf files from DSL
2. **ARM Template Export**: Generate ARM templates
3. **Multi-Region Support**: Design cross-region architectures
4. **Cost Optimization**: Suggest cheaper alternatives
5. **Compliance Checks**: HIPAA, PCI-DSS, SOC 2 validation
6. **Interactive Editing**: Drag-and-drop diagram editor
7. **Version Control**: Save and compare architecture versions

### Known Limitations (MVP)
- SVG generation is basic (no advanced layouts)
- Cost estimates are approximate (not real Azure pricing API)
- Limited to ~20 common Azure services
- No real-time validation against Azure quotas
- DSL parser doesn't support complex nesting

## Migration Notes from VizCode

### What We're Keeping
- Icon library (751 icons including Azure)
- DSL concept (simplified for Azure)
- SVG rendering approach

### What We're Changing
- Backend: Express.js → FastAPI (Python)
- LLM: OpenAI/Gemini → Ollama (llama3.2)
- Focus: AWS → Azure
- Integration: Standalone → Embedded in CostSense-AI

### Files NOT Needed from VizCode
- `/backend/backend.cjs` - Replaced by FastAPI
- `/backend/services/aiService.cjs` - Using Ollama directly
- `/backend/controllers/chatController.cjs` - Using InfraPlannerAgent
- OpenAI/Gemini API keys - Not needed with Ollama

## Security Considerations

1. **Input Validation**: Sanitize all user requirements input
2. **DSL Sandboxing**: Parse DSL safely (no eval/exec)
3. **Rate Limiting**: Limit plan generation requests (5/min per user)
4. **Cost Caps**: Warn if estimated cost exceeds thresholds
5. **SVG Sanitization**: Clean SVG output to prevent XSS

## Next Steps

1. ✅ Get user approval on plan
2. ⏳ Create Phase 1: Agent core structure
3. ⏳ Create Phase 2: DSL parser & generator
4. ⏳ Create Phase 3: API endpoints
5. ⏳ Create Phase 4: Frontend integration
6. ⏳ Create Phase 5: Azure icon integration
7. ⏳ Create Phase 6: Testing
8. ⏳ Create Phase 7: Documentation

---

**Plan Author**: Claude Code
**Plan Date**: 2025-12-07
**Target Completion**: 2025-12-13 (6 business days)
