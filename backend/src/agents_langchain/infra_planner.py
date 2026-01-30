"""Infrastructure Planner Agent - Azure Architecture Design and Visualization"""

from typing import Dict, Any, Optional, List
import json
import logging
import re
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from .infra_tools.infra_planner_tools import INFRA_PLANNER_TOOLS
from .svg_generator_new import generate_architecture_svg

logger = logging.getLogger(__name__)


class InfraPlannerAgent:
    """
    Azure Infrastructure Planning Agent

    Responsibilities:
    - Generate Azure architecture diagrams from requirements
    - Suggest optimal resource configurations
    - Create DSL code for visualization
    - Estimate costs and provide recommendations
    """

    def __init__(self):
        """Initialize the infrastructure planner agent"""
        try:
            self.llm = ChatOllama(
                model="llama3.2:latest",
                temperature=0.3,  # Slightly higher for creative designs
            )
            # Test connection
            self.llm.invoke("test")
            self.llm_available = True
            logger.info("Infra Planner Agent initialized with Ollama")
        except Exception as e:
            self.llm = None
            self.llm_available = False
            logger.warning(f"Ollama unavailable for Infra Planner, using fallback: {e}")

        self.system_prompt = """You are an Azure Infrastructure Planning Expert and Architecture Designer.

Your role is to help design optimal Azure cloud architectures based on user requirements.

When planning infrastructure:
1. **Understand Requirements**: Analyze workload type, scale, compliance, budget
2. **Suggest Services**: Recommend appropriate Azure services
3. **Design Architecture**: Create well-architected solutions following Azure best practices
4. **Generate DSL**: Produce clear DSL code for diagram visualization
5. **Estimate Costs**: Provide realistic monthly cost estimates
6. **Best Practices**: Include security, reliability, and cost optimization recommendations

Available Azure Services Categories:
- **Compute**: Virtual Machines, App Service, Container Instances, AKS, Functions
- **Storage**: Blob Storage, File Storage, Disk Storage, Data Lake
- **Database**: SQL Database, Cosmos DB, PostgreSQL, MySQL
- **Networking**: Virtual Network, Load Balancer, Application Gateway, VPN Gateway
- **Security**: Key Vault, Security Center, Azure AD
- **Monitoring**: Application Insights, Log Analytics, Monitor
- **Integration**: Logic Apps, Service Bus, Event Grid

Azure Well-Architected Framework Pillars:
1. Cost Optimization
2. Operational Excellence
3. Performance Efficiency
4. Reliability
5. Security

Output Format:
Provide a comprehensive infrastructure plan with:
1. **Architecture Overview** (2-3 sentences describing the solution)
2. **DSL Code** (clean, properly formatted DSL for diagram)
3. **Services Used** (list of Azure services)
4. **Cost Estimate** (realistic monthly cost in USD)
5. **Recommendations** (3-5 best practice suggestions)
"""

    async def plan(self, requirements: str) -> Dict[str, Any]:
        """
        Generate infrastructure plan and architecture

        Args:
            requirements: User's infrastructure requirements (natural language)

        Returns:
            {
                "description": "Architecture overview",
                "dsl_code": "Diagram DSL code",
                "services": ["Azure service list"],
                "estimated_monthly_cost": 1234.56,
                "recommendations": ["Best practice suggestions"],
                "svg_diagram": "<svg>...</svg>"  # Future: actual SVG rendering
            }
        """
        if not self.llm_available:
            return self._fallback_plan(requirements)

        try:
            # Create LLM with tools
            llm_with_tools = self.llm.bind_tools(INFRA_PLANNER_TOOLS)

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Infrastructure Requirements: {requirements}

Please generate a complete Azure infrastructure plan:

1. Use the available tools to:
   - generate_azure_architecture_dsl() to create DSL code
   - get_azure_service_recommendations() if you need service suggestions
   - estimate_azure_costs() to calculate costs
   - validate_azure_architecture() to check best practices

2. Provide a comprehensive plan with:
   - Clear architecture description
   - Complete DSL code for visualization
   - List of all Azure services used
   - Realistic cost estimate
   - 3-5 implementation recommendations

Focus on Azure best practices: security, reliability, scalability, and cost optimization.
""")
            ]

            # ReAct loop for tool calling
            max_iterations = 5
            final_response = None

            for iteration in range(max_iterations):
                response = await llm_with_tools.ainvoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    # Agent has finished reasoning and has final answer
                    final_response = response.content
                    break

                # Execute all tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Find and execute the tool
                    tool = next((t for t in INFRA_PLANNER_TOOLS if t.name == tool_name), None)
                    if tool:
                        try:
                            result = tool.invoke(tool_args)
                            messages.append(ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call["id"]
                            ))
                            logger.info(f"Infra Planner tool executed: {tool_name}")
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e}")
                            messages.append(ToolMessage(
                                content=f"Tool '{tool_name}' failed: {str(e)}",
                                tool_call_id=tool_call["id"]
                            ))

            # Parse the final response
            if final_response:
                return self._parse_llm_response(final_response, requirements)
            else:
                # Fallback if max iterations reached
                return self._fallback_plan(requirements)

        except Exception as e:
            logger.error(f"Infrastructure planning failed: {e}")
            return self._fallback_plan(requirements)

    def _parse_llm_response(self, response_text: str, requirements: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured infrastructure plan

        Args:
            response_text: Raw LLM response
            requirements: Original user requirements

        Returns:
            Structured plan dictionary
        """
        plan = {
            "description": "",
            "dsl_code": "",
            "services": [],
            "estimated_monthly_cost": 0.0,
            "recommendations": [],
            "svg_diagram": ""
        }

        # Extract description (first paragraph or section)
        description_match = re.search(r'(?:Architecture Overview|Description)[:\s]*\n(.*?)(?:\n\n|\n#|\nDSL|$)', response_text, re.DOTALL | re.IGNORECASE)
        if description_match:
            plan["description"] = description_match.group(1).strip()
        else:
            # Use first meaningful paragraph
            paragraphs = [p.strip() for p in response_text.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                plan["description"] = paragraphs[0]

        # Extract DSL code (from code blocks)
        dsl_match = re.search(r'```(?:dsl|python)?\n(.*?)```', response_text, re.DOTALL)
        if dsl_match:
            plan["dsl_code"] = dsl_match.group(1).strip()
        else:
            # Look for DSL-like content (lines with '=' and service names)
            dsl_lines = []
            for line in response_text.split('\n'):
                if '=' in line and any(service in line for service in ['VirtualNetwork', 'AppService', 'SQLDatabase', 'StorageAccount', 'VirtualMachine']):
                    dsl_lines.append(line.strip())
                elif '->' in line:
                    dsl_lines.append(line.strip())
            if dsl_lines:
                plan["dsl_code"] = '\n'.join(dsl_lines)

        # Extract services (look for Azure service names)
        azure_services = [
            'Virtual Machine', 'App Service', 'AKS', 'Functions', 'Container Instances',
            'Virtual Network', 'Load Balancer', 'Application Gateway', 'VPN Gateway',
            'SQL Database', 'Cosmos DB', 'PostgreSQL', 'MySQL',
            'Storage Account', 'Blob Storage', 'File Storage', 'Data Lake',
            'Key Vault', 'Security Center', 'Azure AD',
            'Application Insights', 'Log Analytics', 'Monitor'
        ]
        found_services = set()
        response_lower = response_text.lower()
        for service in azure_services:
            if service.lower() in response_lower:
                found_services.add(service)
        plan["services"] = sorted(list(found_services))

        # Extract cost estimate
        cost_match = re.search(r'\$?\s*(\d{1,5}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|per month|monthly)?', response_text)
        if cost_match:
            cost_str = cost_match.group(1).replace(',', '')
            try:
                plan["estimated_monthly_cost"] = float(cost_str)
            except ValueError:
                pass

        # Extract recommendations (look for bullet points or numbered lists)
        recommendations = []
        in_recommendations = False
        for line in response_text.split('\n'):
            line = line.strip()
            if 'recommendation' in line.lower() or 'best practice' in line.lower():
                in_recommendations = True
                continue
            if in_recommendations:
                if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                    rec = re.sub(r'^[-*•\d.)\s]+', '', line).strip()
                    if len(rec) > 10:  # Meaningful recommendation
                        recommendations.append(rec)
                elif len(recommendations) > 0 and len(line) < 5:
                    # End of recommendations section
                    break

        plan["recommendations"] = recommendations[:5]  # Limit to top 5

        # If we didn't extract enough info, use fallback
        if not plan["dsl_code"] or not plan["services"]:
            logger.warning("LLM response parsing incomplete, using fallback")
            fallback = self._fallback_plan(requirements)
            if not plan["dsl_code"]:
                plan["dsl_code"] = fallback["dsl_code"]
            if not plan["services"]:
                plan["services"] = fallback["services"]
            if not plan["description"]:
                plan["description"] = fallback["description"]
            if plan["estimated_monthly_cost"] == 0.0:
                plan["estimated_monthly_cost"] = fallback["estimated_monthly_cost"]
            if not plan["recommendations"]:
                plan["recommendations"] = fallback["recommendations"]

        # Generate architecture diagram with arrows and proper layout
        plan["svg_diagram"] = generate_architecture_svg(plan["services"])

        return plan

    def _fallback_plan(self, requirements: str) -> Dict[str, Any]:
        """
        Fallback infrastructure plan when LLM is unavailable

        Args:
            requirements: User requirements

        Returns:
            Basic infrastructure plan
        """
        requirements_lower = requirements.lower()

        # Determine workload type
        workload_type = 'web_app'  # default
        if any(word in requirements_lower for word in ['data', 'analytics', 'pipeline', 'etl']):
            workload_type = 'data_pipeline'
        elif any(word in requirements_lower for word in ['ml', 'machine learning', 'ai', 'training']):
            workload_type = 'ml_training'
        elif any(word in requirements_lower for word in ['microservice', 'container', 'kubernetes', 'docker']):
            workload_type = 'microservices'
        elif any(word in requirements_lower for word in ['api', 'rest', 'endpoint']):
            workload_type = 'api'

        # Use tools to generate plan
        from .infra_tools.infra_planner_tools import (
            generate_azure_architecture_dsl,
            get_azure_service_recommendations,
            estimate_azure_costs,
            validate_azure_architecture
        )

        # Generate DSL
        dsl_code = generate_azure_architecture_dsl.invoke({"requirements": requirements})

        # Get service recommendations
        service_recs = get_azure_service_recommendations.invoke({"workload_type": workload_type})

        # Extract service names from DSL
        services = []
        for line in dsl_code.split('\n'):
            for service in ['VirtualMachine', 'AppService', 'AKS', 'SQLDatabase', 'CosmosDB', 'StorageAccount', 'VirtualNetwork', 'LoadBalancer', 'KeyVault', 'ApplicationInsights']:
                if service in line:
                    # Convert to readable format
                    readable = ' '.join(re.findall('[A-Z][a-z]*', service))
                    if readable not in services:
                        services.append(readable)

        # Estimate costs
        cost_estimate = estimate_azure_costs.invoke({"services": services})

        # Validate
        validation = validate_azure_architecture.invoke({"dsl_code": dsl_code})

        return {
            "description": f"Azure {workload_type.replace('_', ' ').title()} architecture based on your requirements. This design includes core services for {workload_type.replace('_', ' ')} with security, monitoring, and scalability built in.",
            "dsl_code": dsl_code,
            "services": services,
            "estimated_monthly_cost": cost_estimate.get("total_monthly_cost", 500.0),
            "recommendations": validation.get("suggestions", [
                "Enable Azure Security Center for threat protection",
                "Configure automated backups for all data services",
                "Use Azure Policy to enforce organizational standards",
                "Implement Azure Monitor for comprehensive observability"
            ])[:5],
            "svg_diagram": generate_architecture_svg(services)
        }

    def _generate_simple_svg(self, services: List[str]) -> str:
        """
        Generate a proper Azure architecture diagram with layers and connections

        Args:
            services: List of service names

        Returns:
            SVG markup string with proper architecture layout
        """
        # Categorize services by layer
        presentation_layer = []
        application_layer = []
        data_layer = []
        security_layer = []
        monitoring_layer = []
        network_layer = []

        for service in services:
            service_lower = service.lower()
            if any(word in service_lower for word in ['gateway', 'load balancer', 'cdn', 'firewall', 'front door']):
                presentation_layer.append(service)
            elif any(word in service_lower for word in ['app service', 'function', 'aks', 'container', 'virtual machine', 'vm']):
                application_layer.append(service)
            elif any(word in service_lower for word in ['sql', 'cosmos', 'database', 'storage', 'blob', 'data']):
                data_layer.append(service)
            elif any(word in service_lower for word in ['key vault', 'security', 'defender', 'sentinel']):
                security_layer.append(service)
            elif any(word in service_lower for word in ['insights', 'monitor', 'log', 'analytics']):
                monitoring_layer.append(service)
            elif any(word in service_lower for word in ['virtual network', 'vnet', 'subnet', 'nsg']):
                network_layer.append(service)
            else:
                # Default to application layer
                application_layer.append(service)

        # Calculate dimensions
        max_services_per_layer = max(
            len(presentation_layer) or 1,
            len(application_layer) or 1,
            len(data_layer) or 1,
            1  # Minimum width
        )

        width = 200 + (max_services_per_layer * 200)
        height = 800

        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .layer-bg {{ fill: #f5f5f5; stroke: #ccc; stroke-width: 2; opacity: 0.3; }}
      .layer-title {{ fill: #2E2E38; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: 600; }}
      .service-box {{ fill: #FFE600; stroke: #2E2E38; stroke-width: 2; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2)); }}
      .service-text {{ fill: #2E2E38; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 500; }}
      .network-bg {{ fill: #e3f2fd; stroke: #1976d2; stroke-width: 2; stroke-dasharray: 5,5; }}
      .security-bg {{ fill: #fff3e0; stroke: #f57c00; stroke-width: 2; }}
      .connection {{ stroke: #666; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
      .title-text {{ fill: #2E2E38; font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#666" />
    </marker>
  </defs>

  <!-- Title -->
  <text x="{width/2}" y="30" class="title-text" text-anchor="middle">Azure Infrastructure Architecture</text>

  <!-- Network Boundary -->
  <rect x="50" y="60" width="{width-100}" height="650" class="network-bg" rx="10"/>
  <text x="70" y="85" class="layer-title">Virtual Network</text>
'''

        y_pos = 120
        connections = []
        layer_positions = {}

        # Render Presentation Layer
        if presentation_layer:
            svg += f'  <text x="70" y="{y_pos - 10}" class="layer-title">Presentation Layer</text>\n'
            positions = self._render_layer_services(presentation_layer, y_pos, width, '#1976d2')
            layer_positions['presentation'] = positions
            svg += positions['svg']
            y_pos += 120

        # Render Application Layer
        if application_layer:
            svg += f'  <text x="70" y="{y_pos - 10}" class="layer-title">Application Layer</text>\n'
            positions = self._render_layer_services(application_layer, y_pos, width, '#FFE600')
            layer_positions['application'] = positions
            svg += positions['svg']
            y_pos += 120

        # Render Data Layer
        if data_layer:
            svg += f'  <text x="70" y="{y_pos - 10}" class="layer-title">Data Layer</text>\n'
            positions = self._render_layer_services(data_layer, y_pos, width, '#4caf50')
            layer_positions['data'] = positions
            svg += positions['svg']
            y_pos += 120

        # Render Security & Monitoring in sidebar
        sidebar_x = width - 180
        sidebar_y = 120

        if security_layer:
            svg += f'''  <rect x="{sidebar_x - 10}" y="{sidebar_y}" width="170" height="{len(security_layer) * 60 + 40}" class="security-bg" rx="5"/>
  <text x="{sidebar_x}" y="{sidebar_y + 25}" class="layer-title">Security</text>\n'''
            for i, service in enumerate(security_layer):
                box_y = sidebar_y + 40 + (i * 60)
                svg += f'''  <rect x="{sidebar_x}" y="{box_y}" width="150" height="40" class="service-box" rx="5"/>
  <text x="{sidebar_x + 75}" y="{box_y + 25}" class="service-text" text-anchor="middle">{service}</text>\n'''
            sidebar_y += len(security_layer) * 60 + 60

        if monitoring_layer:
            svg += f'''  <text x="{sidebar_x}" y="{sidebar_y + 15}" class="layer-title">Monitoring</text>\n'''
            for i, service in enumerate(monitoring_layer):
                box_y = sidebar_y + 30 + (i * 55)
                svg += f'''  <rect x="{sidebar_x}" y="{box_y}" width="150" height="35" class="service-box" rx="5" opacity="0.8"/>
  <text x="{sidebar_x + 75}" y="{box_y + 22}" class="service-text" text-anchor="middle" font-size="11">{service}</text>\n'''

        # Draw connections between layers
        if 'presentation' in layer_positions and 'application' in layer_positions:
            for pres_pos in layer_positions['presentation']['boxes']:
                for app_pos in layer_positions['application']['boxes']:
                    svg += f'  <path d="M {pres_pos["cx"]} {pres_pos["bottom"]} L {app_pos["cx"]} {app_pos["top"]}" class="connection"/>\n'

        if 'application' in layer_positions and 'data' in layer_positions:
            for app_pos in layer_positions['application']['boxes']:
                for data_pos in layer_positions['data']['boxes']:
                    svg += f'  <path d="M {data_pos["cx"]} {data_pos["top"]} L {app_pos["cx"]} {app_pos["bottom"]}" class="connection"/>\n'

        svg += '</svg>'
        return svg

    def _render_layer_services(self, services: List[str], y_pos: int, total_width: int, color: str) -> Dict[str, Any]:
        """Helper to render services in a layer"""
        box_width = 160
        spacing = 20
        total_boxes_width = len(services) * box_width + (len(services) - 1) * spacing
        start_x = (total_width - total_boxes_width) / 2

        svg = ''
        boxes = []

        for i, service in enumerate(services):
            x = start_x + (i * (box_width + spacing))
            svg += f'''  <rect x="{x}" y="{y_pos}" width="{box_width}" height="50" class="service-box" rx="5"/>
  <text x="{x + box_width/2}" y="{y_pos + 30}" class="service-text" text-anchor="middle">{service}</text>\n'''
            boxes.append({
                'cx': x + box_width/2,
                'top': y_pos,
                'bottom': y_pos + 50
            })

        return {'svg': svg, 'boxes': boxes}


# Singleton instance
infra_planner = InfraPlannerAgent()
