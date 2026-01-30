"""Agent Tools - Database query tools for LangChain agents"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.repositories import (
    DashboardRepository,
    VMRepository,
    StorageRepository,
    OptimizationRepository
)

# Import infrastructure planner tools from infra_tools package
from src.agents_langchain.infra_tools import INFRA_PLANNER_TOOLS


# ============================================================================
# COST ANALYSIS TOOLS
# ============================================================================

@tool
def get_total_monthly_cost() -> float:
    """Get the total Azure monthly cost.

    Returns:
        float: Total monthly cost in USD
    """
    db = SessionLocal()
    try:
        repo = DashboardRepository(db)
        data = repo.get_dashboard_summary()
        return data.get("total_monthly_cost", 0.0)
    finally:
        db.close()


@tool
def get_cost_trend(days: int = 30) -> List[Dict[str, Any]]:
    """Get daily cost trend for the specified number of days.

    Args:
        days: Number of days to retrieve (default: 30)

    Returns:
        List of daily cost records with date and cost
    """
    db = SessionLocal()
    try:
        repo = DashboardRepository(db)
        data = repo.get_dashboard_summary()
        daily_costs = data.get("daily_costs", [])
        return daily_costs[-days:] if len(daily_costs) > days else daily_costs
    finally:
        db.close()


@tool
def get_top_services(limit: int = 5) -> List[Dict[str, Any]]:
    """Get top Azure services by cost.

    Args:
        limit: Number of top services to return (default: 5)

    Returns:
        List of services with name and cost
    """
    db = SessionLocal()
    try:
        repo = DashboardRepository(db)
        data = repo.get_dashboard_summary()
        top_services = data.get("top_services", [])
        return top_services[:limit]
    finally:
        db.close()


@tool
def get_monthly_change_percent() -> float:
    """Get the monthly cost change percentage.

    Returns:
        float: Percentage change (positive for increase, negative for decrease)
    """
    db = SessionLocal()
    try:
        repo = DashboardRepository(db)
        data = repo.get_dashboard_summary()
        return data.get("monthly_change_percent", 0.0)
    finally:
        db.close()


# ============================================================================
# INFRASTRUCTURE TOOLS
# ============================================================================

@tool
def get_all_vms() -> List[Dict[str, Any]]:
    """Get all Azure virtual machines with their details.

    Returns:
        List of VMs with name, size, status, utilization, cost, and recommendations
    """
    db = SessionLocal()
    try:
        repo = VMRepository(db)
        return repo.get_all_vms()
    finally:
        db.close()


@tool
def get_vm_summary() -> Dict[str, Any]:
    """Get summary statistics for all VMs.

    Returns:
        Dictionary with total count, running/stopped counts, avg utilization, total cost
    """
    db = SessionLocal()
    try:
        repo = VMRepository(db)
        return repo.get_vms_summary()
    finally:
        db.close()


@tool
def get_underutilized_vms(cpu_threshold: float = 30.0) -> List[Dict[str, Any]]:
    """Get VMs with low CPU utilization.

    Args:
        cpu_threshold: CPU percentage threshold (default: 30%)

    Returns:
        List of underutilized VMs
    """
    db = SessionLocal()
    try:
        repo = VMRepository(db)
        summary = repo.get_vms_summary()
        return summary.get("underutilizedVMs", [])
    finally:
        db.close()


@tool
def get_vms_by_status(status: str) -> List[Dict[str, Any]]:
    """Get VMs filtered by status.

    Args:
        status: VM status (Running, Stopped, Deallocated)

    Returns:
        List of VMs with the specified status
    """
    db = SessionLocal()
    try:
        repo = VMRepository(db)
        all_vms = repo.get_all_vms()
        return [vm for vm in all_vms if vm.get("status") == status]
    finally:
        db.close()


@tool
def get_all_storage_accounts() -> List[Dict[str, Any]]:
    """Get all Azure storage accounts with their details.

    Returns:
        List of storage accounts with name, tier, size, cost, and optimization opportunities
    """
    db = SessionLocal()
    try:
        repo = StorageRepository(db)
        return repo.get_all_storage_accounts()
    finally:
        db.close()


@tool
def get_storage_summary() -> Dict[str, Any]:
    """Get summary statistics for all storage accounts.

    Returns:
        Dictionary with total count, total size, total cost, tier distribution
    """
    db = SessionLocal()
    try:
        repo = StorageRepository(db)
        return repo.get_storage_summary()
    finally:
        db.close()


@tool
def get_storage_by_tier(tier: str) -> List[Dict[str, Any]]:
    """Get storage accounts filtered by tier.

    Args:
        tier: Storage tier (Hot, Cool, Archive)

    Returns:
        List of storage accounts with the specified tier
    """
    db = SessionLocal()
    try:
        repo = StorageRepository(db)
        return repo.get_storage_by_tier(tier)
    finally:
        db.close()


# ============================================================================
# OPTIMIZATION TOOLS
# ============================================================================

@tool
def get_all_recommendations() -> List[Dict[str, Any]]:
    """Get all optimization recommendations.

    Returns:
        List of recommendations with savings, priority, impact, and implementation steps
    """
    db = SessionLocal()
    try:
        repo = OptimizationRepository(db)
        return repo.get_all_recommendations(status="pending")
    finally:
        db.close()


@tool
def get_recommendations_by_priority(priority: str) -> List[Dict[str, Any]]:
    """Get optimization recommendations filtered by priority.

    Args:
        priority: Priority level (High, Medium, Low)

    Returns:
        List of recommendations with the specified priority
    """
    db = SessionLocal()
    try:
        repo = OptimizationRepository(db)
        return repo.get_recommendations_by_priority(priority)
    finally:
        db.close()


@tool
def get_recommendations_by_category(category: str) -> List[Dict[str, Any]]:
    """Get optimization recommendations filtered by category.

    Args:
        category: Category (Compute, Storage, Network, Database, etc.)

    Returns:
        List of recommendations in the specified category
    """
    db = SessionLocal()
    try:
        repo = OptimizationRepository(db)
        return repo.get_recommendations_by_category(category)
    finally:
        db.close()


@tool
def get_optimization_summary() -> Dict[str, Any]:
    """Get summary of all optimization opportunities.

    Returns:
        Dictionary with total count, total savings, priority distribution
    """
    db = SessionLocal()
    try:
        repo = OptimizationRepository(db)
        return repo.get_optimization_summary()
    finally:
        db.close()


@tool
def get_total_potential_savings() -> Dict[str, float]:
    """Get total potential savings from all recommendations.

    Returns:
        Dictionary with monthly and annual savings
    """
    db = SessionLocal()
    try:
        repo = OptimizationRepository(db)
        summary = repo.get_optimization_summary()
        return {
            "monthly": summary.get("totalMonthlySavings", 0.0),
            "annual": summary.get("totalAnnualSavings", 0.0)
        }
    finally:
        db.close()


# ============================================================================
# FINANCIAL ANALYSIS TOOLS
# ============================================================================

@tool
def calculate_roi(implementation_cost: float, monthly_savings: float) -> Dict[str, float]:
    """Calculate ROI for an optimization initiative.

    Args:
        implementation_cost: One-time cost to implement
        monthly_savings: Expected monthly savings

    Returns:
        Dictionary with ROI percentage, payback months, annual savings
    """
    annual_savings = monthly_savings * 12
    roi_percentage = ((annual_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0
    payback_months = implementation_cost / monthly_savings if monthly_savings > 0 else 0

    return {
        "roi_percentage": round(roi_percentage, 2),
        "payback_months": round(payback_months, 1),
        "annual_savings": round(annual_savings, 2),
        "implementation_cost": implementation_cost,
        "monthly_savings": monthly_savings
    }


@tool
def project_costs(months: int = 6) -> Dict[str, Any]:
    """Project future costs based on current spending.

    Args:
        months: Number of months to project (default: 6)

    Returns:
        Dictionary with projected costs with and without optimization
    """
    db = SessionLocal()
    try:
        # Get current costs
        dashboard_repo = DashboardRepository(db)
        opt_repo = OptimizationRepository(db)

        dashboard_data = dashboard_repo.get_dashboard_summary()
        opt_summary = opt_repo.get_optimization_summary()

        current_monthly_cost = dashboard_data.get("total_monthly_cost", 0)
        potential_monthly_savings = opt_summary.get("totalMonthlySavings", 0)

        without_optimization = current_monthly_cost * months
        with_optimization = (current_monthly_cost - potential_monthly_savings) * months
        net_savings = without_optimization - with_optimization

        return {
            "months": months,
            "current_monthly_cost": round(current_monthly_cost, 2),
            "without_optimization": round(without_optimization, 2),
            "with_optimization": round(with_optimization, 2),
            "net_savings": round(net_savings, 2),
            "monthly_savings": round(potential_monthly_savings, 2)
        }
    finally:
        db.close()


# ============================================================================
# TOOL COLLECTIONS FOR AGENTS
# ============================================================================

COST_ANALYSIS_TOOLS = [
    get_total_monthly_cost,
    get_cost_trend,
    get_top_services,
    get_monthly_change_percent,
]

INFRASTRUCTURE_TOOLS = [
    get_all_vms,
    get_vm_summary,
    get_underutilized_vms,
    get_vms_by_status,
    get_all_storage_accounts,
    get_storage_summary,
    get_storage_by_tier,
]

OPTIMIZATION_TOOLS = [
    get_all_recommendations,
    get_recommendations_by_priority,
    get_recommendations_by_category,
    get_optimization_summary,
    get_total_potential_savings,
]

FINANCIAL_TOOLS = [
    calculate_roi,
    project_costs,
    get_total_potential_savings,
]

ALL_TOOLS = (
    COST_ANALYSIS_TOOLS +
    INFRASTRUCTURE_TOOLS +
    OPTIMIZATION_TOOLS +
    FINANCIAL_TOOLS +
    INFRA_PLANNER_TOOLS
)
