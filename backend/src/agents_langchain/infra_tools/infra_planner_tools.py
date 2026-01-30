"""Infrastructure Planner Tools for Azure Architecture Generation"""

from langchain.tools import tool
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@tool
def generate_azure_architecture_dsl(requirements: str) -> str:
    """
    Generate Azure architecture diagram DSL code from requirements.

    This tool creates infrastructure-as-code DSL syntax for Azure resources
    based on natural language requirements.

    Args:
        requirements: Infrastructure requirements description

    Returns:
        DSL code string for diagram visualization
    """
    # Basic template-based DSL generation
    # This will be enhanced by the LLM's reasoning

    dsl_lines = ["# Azure Infrastructure Architecture", ""]

    requirements_lower = requirements.lower()

    # Detect common patterns and generate appropriate resources
    if any(word in requirements_lower for word in ['web', 'app', 'website', 'frontend']):
        dsl_lines.extend([
            "# Web Tier",
            'vnet = VirtualNetwork("prod-vnet", "10.0.0.0/16")',
            'web_subnet = Subnet("web-subnet", "10.0.1.0/24", vnet)',
            'app_service = AppService("web-app", "Premium_P1v2", web_subnet)',
            ""
        ])

    if any(word in requirements_lower for word in ['database', 'db', 'sql', 'data']):
        dsl_lines.extend([
            "# Database Tier",
            'db_subnet = Subnet("db-subnet", "10.0.2.0/24", vnet)',
            'sql_db = SQLDatabase("prod-db", "Standard_S1", db_subnet)',
            ""
        ])

    if any(word in requirements_lower for word in ['storage', 'blob', 'files', 'upload']):
        dsl_lines.extend([
            "# Storage",
            'storage = StorageAccount("prodsa", "Standard_LRS")',
            ""
        ])

    if any(word in requirements_lower for word in ['load balance', 'ha', 'high availability', 'redundan']):
        dsl_lines.extend([
            "# Load Balancing",
            'lb = LoadBalancer("prod-lb", "Standard")',
            ""
        ])

    if any(word in requirements_lower for word in ['monitor', 'observ', 'logging', 'insights']):
        dsl_lines.extend([
            "# Monitoring",
            'app_insights = ApplicationInsights("prod-insights")',
            ""
        ])

    if any(word in requirements_lower for word in ['security', 'secrets', 'keys', 'vault']):
        dsl_lines.extend([
            "# Security",
            'key_vault = KeyVault("prod-keyvault")',
            ""
        ])

    # Add connections
    dsl_lines.append("# Connections")
    if 'app_service' in '\n'.join(dsl_lines) and 'sql_db' in '\n'.join(dsl_lines):
        dsl_lines.append('app_service -> sql_db')
    if 'app_service' in '\n'.join(dsl_lines) and 'storage' in '\n'.join(dsl_lines):
        dsl_lines.append('app_service -> storage')
    if 'app_service' in '\n'.join(dsl_lines) and 'key_vault' in '\n'.join(dsl_lines):
        dsl_lines.append('app_service -> key_vault')
    if 'lb' in '\n'.join(dsl_lines) and 'app_service' in '\n'.join(dsl_lines):
        dsl_lines.append('lb -> app_service')

    return '\n'.join(dsl_lines)


@tool
def estimate_azure_costs(services: List[str]) -> Dict[str, Any]:
    """
    Estimate monthly costs for Azure services.

    Provides cost estimates based on standard Azure pricing for common
    service tiers. These are approximations for planning purposes.

    Args:
        services: List of Azure service names

    Returns:
        Cost breakdown by service with total monthly estimate
    """
    # Approximate monthly costs for common Azure services (USD)
    # These are baseline estimates for standard tiers
    service_costs = {
        'VirtualMachine': 75.00,  # Standard_D2s_v3
        'AppService': 55.00,  # Premium P1v2
        'AKS': 150.00,  # 3 nodes Standard_D2s_v3
        'Functions': 20.00,  # Consumption plan
        'VirtualNetwork': 5.00,
        'Subnet': 0.00,  # Free
        'LoadBalancer': 18.00,  # Standard
        'ApplicationGateway': 125.00,  # Standard v2
        'SQLDatabase': 100.00,  # Standard S1
        'CosmosDB': 175.00,  # 400 RU/s
        'StorageAccount': 25.00,  # Standard LRS, 1TB
        'BlobStorage': 20.00,  # Standard, 1TB
        'KeyVault': 5.00,
        'ApplicationInsights': 15.00,
        'LogAnalytics': 30.00
    }

    breakdown = []
    total = 0.0

    for service in services:
        # Extract service type from DSL (e.g., "AppService" from "app_service = AppService(...)")
        service_type = service
        for known_service in service_costs.keys():
            if known_service.lower() in service.lower():
                service_type = known_service
                break

        cost = service_costs.get(service_type, 50.00)  # Default $50 if unknown
        breakdown.append({
            'service': service_type,
            'monthly_cost': cost,
            'notes': 'Standard tier estimate'
        })
        total += cost

    return {
        'total_monthly_cost': round(total, 2),
        'breakdown': breakdown,
        'currency': 'USD',
        'disclaimer': 'Estimates based on standard tiers. Actual costs may vary based on usage and region.'
    }


@tool
def get_azure_service_recommendations(workload_type: str) -> List[str]:
    """
    Get Azure service recommendations for a specific workload type.

    Suggests optimal Azure services based on common architecture patterns
    and best practices for different workload categories.

    Args:
        workload_type: Type of workload (web_app, data_pipeline, ml_training, microservices, etc.)

    Returns:
        List of recommended Azure services with brief descriptions
    """
    recommendations = {
        'web_app': [
            'App Service - Managed web hosting with auto-scaling',
            'SQL Database - Managed relational database',
            'Application Insights - Application monitoring and analytics',
            'CDN - Content delivery for static assets',
            'Key Vault - Secure secrets management',
            'Application Gateway - Web traffic load balancer with WAF'
        ],
        'data_pipeline': [
            'Data Factory - Orchestrate ETL workflows',
            'Data Lake Storage - Scalable data lake',
            'Databricks - Apache Spark analytics',
            'Event Hubs - Real-time data ingestion',
            'Synapse Analytics - Data warehousing',
            'Power BI - Business intelligence dashboards'
        ],
        'ml_training': [
            'Machine Learning - MLOps platform',
            'Batch - Large-scale compute jobs',
            'Storage Account - Training data storage',
            'Container Registry - Docker image hosting',
            'GPU VMs - High-performance computing',
            'Notebooks - Jupyter notebook environment'
        ],
        'microservices': [
            'AKS (Azure Kubernetes Service) - Container orchestration',
            'Container Instances - Serverless containers',
            'Service Bus - Message queue',
            'API Management - API gateway',
            'Container Registry - Image storage',
            'Application Insights - Distributed tracing'
        ],
        'api': [
            'API Management - API gateway and developer portal',
            'Functions - Serverless compute',
            'Cosmos DB - Global distributed NoSQL',
            'Application Insights - API monitoring',
            'Key Vault - API key management',
            'CDN - Cache API responses'
        ],
        'iot': [
            'IoT Hub - Device connectivity',
            'Stream Analytics - Real-time analytics',
            'Time Series Insights - IoT data analysis',
            'Cosmos DB - Device data storage',
            'Event Hubs - High-throughput ingestion',
            'Functions - Event processing'
        ],
        'static_site': [
            'Static Web Apps - Jamstack hosting',
            'CDN - Global content delivery',
            'Storage Account - Static file hosting',
            'Functions - Backend APIs',
            'Application Insights - Analytics'
        ]
    }

    # Normalize workload type
    workload_lower = workload_type.lower().replace(' ', '_').replace('-', '_')

    # Try exact match first
    if workload_lower in recommendations:
        return recommendations[workload_lower]

    # Try partial match
    for key, services in recommendations.items():
        if key in workload_lower or workload_lower in key:
            return services

    # Default recommendation
    return [
        'Virtual Machines - General-purpose compute',
        'Virtual Network - Network isolation',
        'Storage Account - General storage',
        'Application Insights - Monitoring',
        'Key Vault - Security'
    ]


@tool
def validate_azure_architecture(dsl_code: str) -> Dict[str, Any]:
    """
    Validate Azure architecture DSL for best practices and common issues.

    Checks for security, reliability, and cost optimization best practices.

    Args:
        dsl_code: DSL code to validate

    Returns:
        Validation results with warnings and suggestions
    """
    warnings = []
    suggestions = []
    errors = []

    dsl_lower = dsl_code.lower()

    # Security checks
    if 'virtualnetwork' in dsl_lower or 'vnet' in dsl_lower:
        if 'keyvault' not in dsl_lower:
            warnings.append('Consider adding Key Vault for secure secrets management')
    else:
        errors.append('Virtual Network not found - all resources should be in a VNet for security')

    # High availability checks
    if 'appservice' in dsl_lower or 'virtualmachine' in dsl_lower:
        if 'loadbalancer' not in dsl_lower and 'applicationgateway' not in dsl_lower:
            warnings.append('Consider adding Load Balancer or Application Gateway for high availability')

    # Monitoring checks
    if 'applicationinsights' not in dsl_lower and 'loganalytics' not in dsl_lower:
        warnings.append('Add Application Insights or Log Analytics for monitoring and diagnostics')

    # Database checks
    if 'sqldatabase' in dsl_lower or 'cosmosdb' in dsl_lower:
        if 'backup' not in dsl_lower:
            suggestions.append('Enable automated backups for your databases')

    # Storage checks
    if 'storageaccount' in dsl_lower or 'blobstorage' in dsl_lower:
        suggestions.append('Consider using lifecycle management policies to optimize storage costs')

    # Cost optimization suggestions
    if 'virtualmachine' in dsl_lower:
        suggestions.append('Consider using Azure Spot VMs for non-critical workloads to reduce costs')
        suggestions.append('Enable auto-shutdown schedules for development/test VMs')

    # General best practices
    suggestions.extend([
        'Use Azure Policy to enforce organizational standards',
        'Enable Azure Security Center for threat protection',
        'Implement tags for resource organization and cost tracking',
        'Use managed identities instead of storing credentials'
    ])

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'suggestions': suggestions[:5],  # Limit to top 5 suggestions
        'score': 100 - (len(errors) * 30) - (len(warnings) * 10)
    }


# Export tools list
INFRA_PLANNER_TOOLS = [
    generate_azure_architecture_dsl,
    estimate_azure_costs,
    get_azure_service_recommendations,
    validate_azure_architecture
]
