from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import memory, calculator
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.config.settings import Settings
from src.tools.aws_tools_simple import EC2UtilizationTool, S3OptimizationTool

class InfrastructureAnalystAgent:
    """Specialized agent for AWS infrastructure optimization and resource analysis"""
    
    def __init__(self):
        self.settings = Settings()
        self.ec2_tool = EC2UtilizationTool()
        self.s3_tool = S3OptimizationTool()
        
        # Configure Ollama model
        try:
            self.model = OllamaModel(
                host=self.settings.OLLAMA_HOST,
                model_id=self.settings.OLLAMA_MODEL,
                temperature=0.1
            )
        except Exception:
            # Fallback to mock mode if Ollama not available
            self.model = None
        
        # Create specialized tools for infrastructure analysis
        self._setup_tools()
        
        # Initialize the Strands agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            tools=[
                self.analyze_ec2_utilization,
                self.analyze_s3_optimization,
                self.calculate_rightsizing_recommendations,
                self.assess_reserved_instance_opportunities,
                memory,
                calculator
            ],
            name="infrastructure_analyst"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Infrastructure Optimization Specialist with deep expertise in resource efficiency and cost optimization.

        Your specializations include:
        - EC2 instance rightsizing and utilization analysis
        - S3 storage optimization and lifecycle management
        - Resource allocation efficiency assessment
        - Performance vs cost trade-off analysis
        - Reserved Instance and Savings Plans recommendations
        - Auto-scaling and capacity planning optimization
        
        Analysis approach:
        1. Evaluate resource utilization patterns and efficiency
        2. Identify oversized, undersized, or idle resources
        3. Recommend specific technical optimizations
        4. Calculate potential cost savings from changes
        5. Assess performance impact of recommendations
        6. Provide implementation timelines and priorities
        
        Technical considerations:
        - CPU, memory, and network utilization patterns
        - Workload characteristics and scaling requirements
        - Regional pricing differences and availability zones
        - Storage access patterns and lifecycle requirements
        - Security and compliance implications
        - Business continuity and disaster recovery needs
        
        Always provide:
        - Specific technical recommendations with implementation steps
        - Quantified cost and performance impact estimates
        - Risk assessment for each recommendation
        - Priority ranking based on impact vs effort
        - Monitoring and validation strategies"""
    
    def _setup_tools(self):
        """Setup specialized tools for infrastructure analysis"""
        
        @tool
        def analyze_ec2_utilization() -> str:
            """Analyze EC2 instance utilization and identify optimization opportunities."""
            return self.ec2_tool._run()
        
        @tool
        def analyze_s3_optimization() -> str:
            """Analyze S3 storage and identify optimization opportunities."""
            return self.s3_tool._run()
        
        @tool
        def calculate_rightsizing_recommendations(ec2_data: str) -> str:
            """Calculate specific rightsizing recommendations for EC2 instances.
            
            Args:
                ec2_data: JSON string containing EC2 utilization data
            """
            try:
                data = json.loads(ec2_data)
                instances = data.get('instances', [])
                
                recommendations = []
                total_potential_savings = 0
                
                for instance in instances:
                    cpu_util = instance.get('avg_cpu_utilization', 0)
                    memory_util = instance.get('memory_utilization', 0)
                    current_type = instance.get('instance_type', '')
                    monthly_cost = instance.get('monthly_cost', 0)
                    
                    # Rightsizing logic
                    recommendation = self._calculate_instance_recommendation(
                        cpu_util, memory_util, current_type, monthly_cost
                    )
                    
                    if recommendation:
                        recommendations.append({
                            "instance_id": instance.get('instance_id'),
                            "current_type": current_type,
                            "current_monthly_cost": monthly_cost,
                            "cpu_utilization": cpu_util,
                            "memory_utilization": memory_util,
                            **recommendation
                        })
                        total_potential_savings += recommendation.get('monthly_savings', 0)
                
                return json.dumps({
                    "total_instances_analyzed": len(instances),
                    "instances_with_recommendations": len(recommendations),
                    "total_potential_monthly_savings": round(total_potential_savings, 2),
                    "recommendations": recommendations
                })
                
            except Exception as e:
                return f"Error calculating rightsizing recommendations: {str(e)}"
        
        @tool
        def assess_reserved_instance_opportunities(ec2_data: str) -> str:
            """Assess Reserved Instance opportunities based on usage patterns.
            
            Args:
                ec2_data: JSON string containing EC2 utilization data
            """
            try:
                data = json.loads(ec2_data)
                instances = data.get('instances', [])
                
                # Group by instance type and region
                instance_groups = {}
                for instance in instances:
                    instance_type = instance.get('instance_type', '')
                    region = instance.get('region', 'us-east-1')
                    key = f"{instance_type}_{region}"
                    
                    if key not in instance_groups:
                        instance_groups[key] = []
                    instance_groups[key].append(instance)
                
                ri_opportunities = []
                total_ri_savings = 0
                
                for group_key, group_instances in instance_groups.items():
                    if len(group_instances) >= 1:  # Consider RI for stable workloads
                        instance_type, region = group_key.split('_')
                        
                        # Calculate RI savings (typically 30-40% for 1-year terms)
                        total_monthly_cost = sum(inst.get('monthly_cost', 0) for inst in group_instances)
                        ri_discount = 0.35  # 35% average discount
                        monthly_ri_savings = total_monthly_cost * ri_discount
                        
                        ri_opportunities.append({
                            "instance_type": instance_type,
                            "region": region,
                            "instance_count": len(group_instances),
                            "total_monthly_cost": round(total_monthly_cost, 2),
                            "estimated_ri_monthly_savings": round(monthly_ri_savings, 2),
                            "annual_savings": round(monthly_ri_savings * 12, 2),
                            "recommendation": "1-year No Upfront RI" if monthly_ri_savings > 20 else "Monitor for 3 months"
                        })
                        
                        total_ri_savings += monthly_ri_savings
                
                return json.dumps({
                    "total_ri_opportunities": len(ri_opportunities),
                    "total_potential_monthly_ri_savings": round(total_ri_savings, 2),
                    "total_potential_annual_ri_savings": round(total_ri_savings * 12, 2),
                    "opportunities": ri_opportunities
                })
                
            except Exception as e:
                return f"Error assessing RI opportunities: {str(e)}"
        
        # Assign tools to instance
        self.analyze_ec2_utilization = analyze_ec2_utilization
        self.analyze_s3_optimization = analyze_s3_optimization
        self.calculate_rightsizing_recommendations = calculate_rightsizing_recommendations
        self.assess_reserved_instance_opportunities = assess_reserved_instance_opportunities
    
    def _calculate_instance_recommendation(self, cpu_util: float, memory_util: float, 
                                         current_type: str, monthly_cost: float) -> Dict[str, Any]:
        """Calculate specific instance recommendation based on utilization"""
        
        # Rightsizing logic based on utilization patterns
        if cpu_util < 20 and memory_util < 30:
            # Significantly underutilized - downsize
            recommended_type = self._get_smaller_instance_type(current_type)
            if recommended_type != current_type:
                savings_percentage = 0.4  # Typical 40% savings when downsizing
                return {
                    "action": "Downsize",
                    "recommended_type": recommended_type,
                    "monthly_savings": round(monthly_cost * savings_percentage, 2),
                    "reason": f"Low utilization: CPU {cpu_util}%, Memory {memory_util}%",
                    "confidence": "High",
                    "implementation_effort": "Low"
                }
        
        elif cpu_util > 80 or memory_util > 80:
            # Highly utilized - consider upsizing
            recommended_type = self._get_larger_instance_type(current_type)
            return {
                "action": "Consider Upsizing",
                "recommended_type": recommended_type,
                "monthly_savings": 0,  # No savings, but improved performance
                "reason": f"High utilization: CPU {cpu_util}%, Memory {memory_util}%",
                "confidence": "Medium",
                "implementation_effort": "Low"
            }
        
        elif 30 <= cpu_util <= 60 and 40 <= memory_util <= 70:
            # Well utilized - consider Reserved Instances
            return {
                "action": "Consider Reserved Instance",
                "recommended_type": current_type,
                "monthly_savings": round(monthly_cost * 0.35, 2),  # 35% RI discount
                "reason": f"Stable utilization: CPU {cpu_util}%, Memory {memory_util}%",
                "confidence": "High",
                "implementation_effort": "Low"
            }
        
        return None  # No recommendation
    
    def _get_smaller_instance_type(self, current_type: str) -> str:
        """Get a smaller instance type for downsizing"""
        downsize_map = {
            't3.medium': 't3.small',
            't3.large': 't3.medium',
            'm5.large': 'm5.medium',
            'm5.xlarge': 'm5.large',
            'c5.large': 'c5.medium',
            'c5.xlarge': 'c5.large'
        }
        return downsize_map.get(current_type, current_type)
    
    def _get_larger_instance_type(self, current_type: str) -> str:
        """Get a larger instance type for upsizing"""
        upsize_map = {
            't3.small': 't3.medium',
            't3.medium': 't3.large',
            'm5.medium': 'm5.large',
            'm5.large': 'm5.xlarge',
            'c5.medium': 'c5.large',
            'c5.large': 'c5.xlarge'
        }
        return upsize_map.get(current_type, current_type)
    
    async def analyze(self, query: str, context: Dict[str, Any] = None) -> str:
        """Perform infrastructure analysis based on query"""
        try:
            # Always try fallback first for reliability
            if self.model is None:
                return await self._fallback_analysis(query, context)
            
            # Try Strands agent, but fallback if it fails
            try:
                result = await asyncio.to_thread(self.agent, query)
                return str(result)
            except Exception as llm_error:
                return await self._fallback_analysis(query, context)
            
        except Exception as e:
            return await self._fallback_analysis(query, context)
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any] = None) -> str:
        """Fallback analysis when LLM not available"""
        try:
            # Get infrastructure data
            ec2_data = self.analyze_ec2_utilization()
            s3_data = self.analyze_s3_optimization()
            
            # Calculate recommendations
            rightsizing = self.calculate_rightsizing_recommendations(ec2_data)
            ri_opportunities = self.assess_reserved_instance_opportunities(ec2_data)
            
            # Parse JSON results
            import json
            try:
                ec2_json = json.loads(ec2_data) if ec2_data.startswith('{') else {}
                s3_json = json.loads(s3_data) if s3_data.startswith('{') else {}
                rightsizing_json = json.loads(rightsizing) if rightsizing.startswith('{') else {}
                ri_json = json.loads(ri_opportunities) if ri_opportunities.startswith('{') else {}
            except:
                ec2_json = {"total_instances": 0}
                s3_json = {"total_buckets": 0}
                rightsizing_json = {"total_potential_monthly_savings": 0}
                ri_json = {"total_potential_monthly_ri_savings": 0}
            
            # Extract key metrics
            total_instances = ec2_json.get('total_instances', 0)
            avg_utilization = ec2_json.get('avg_utilization', 0)
            total_buckets = s3_json.get('total_buckets', 0)
            rightsizing_savings = rightsizing_json.get('total_potential_monthly_savings', 0)
            ri_savings = ri_json.get('total_potential_monthly_ri_savings', 0)
            total_savings = rightsizing_savings + ri_savings
            
            # Generate intelligent analysis
            analysis_summary = []
            
            if total_instances > 0:
                analysis_summary.append(f"• Managing {total_instances} EC2 instances")
                if avg_utilization < 40:
                    analysis_summary.append(f"• ⚠️ Low average utilization: {avg_utilization:.1f}% - optimization opportunities")
                elif avg_utilization > 80:
                    analysis_summary.append(f"• ⚡ High utilization: {avg_utilization:.1f}% - may need capacity expansion")
                else:
                    analysis_summary.append(f"• ✅ Good utilization: {avg_utilization:.1f}%")
            else:
                analysis_summary.append("• No EC2 instances detected in current scope")
            
            if total_buckets > 0:
                analysis_summary.append(f"• {total_buckets} S3 buckets analyzed for optimization")
            
            # Optimization opportunities
            optimizations = []
            if rightsizing_savings > 0:
                optimizations.append(f"EC2 rightsizing could save ${rightsizing_savings:,.2f}/month")
            if ri_savings > 0:
                optimizations.append(f"Reserved Instances could save ${ri_savings:,.2f}/month")
            if total_buckets > 2:
                optimizations.append("S3 lifecycle policies could reduce storage costs")
            if avg_utilization < 30:
                optimizations.append("Consider auto-scaling to improve resource efficiency")
            
            # Priority recommendations
            priorities = []
            if rightsizing_savings > 100:
                priorities.append("🔥 HIGH: Implement EC2 rightsizing recommendations")
            if ri_savings > 200:
                priorities.append("📈 MEDIUM: Evaluate Reserved Instance purchases")
            if total_buckets > 0:
                priorities.append("💾 MEDIUM: Implement S3 storage optimization")
            priorities.append("📊 LOW: Set up resource utilization monitoring")
            
            return f"""🔧 AWS Infrastructure Analysis Results

Query: {query}

🏗️ Infrastructure Overview:
{chr(10).join(analysis_summary)}

💰 Optimization Opportunities:
{chr(10).join(f"• {opt}" for opt in optimizations) if optimizations else "• No major optimization opportunities identified"}

🎯 Priority Recommendations:
{chr(10).join(priorities)}

📊 Key Metrics:
• Total EC2 Instances: {total_instances}
• Average CPU Utilization: {avg_utilization:.1f}%
• S3 Buckets Analyzed: {total_buckets}
• Potential Monthly Savings: ${total_savings:,.2f}
• Rightsizing Savings: ${rightsizing_savings:,.2f}/month
• Reserved Instance Savings: ${ri_savings:,.2f}/month

🚀 Next Steps:
1. Review detailed rightsizing recommendations
2. Analyze Reserved Instance opportunities  
3. Implement S3 lifecycle policies
4. Set up automated resource monitoring
5. Plan phased optimization rollout

Generated by Infrastructure Analyst Agent - Professional AWS resource optimization"""
            
        except Exception as e:
            return f"Infrastructure Analysis completed with basic insights. Query: {query}. Note: Detailed analysis requires data connection. Error: {str(e)}"
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "ec2_rightsizing_analysis",
            "s3_optimization_analysis",
            "reserved_instance_assessment",
            "resource_utilization_monitoring",
            "performance_cost_optimization",
            "capacity_planning_analysis"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test data retrieval
            ec2_test = self.analyze_ec2_utilization()
            s3_test = self.analyze_s3_optimization()
            
            data_available = len(ec2_test) > 10 and len(s3_test) > 10
            model_available = self.model is not None
            
            return {
                "agent_name": "infrastructure_analyst",
                "healthy": data_available,
                "model_available": model_available,
                "data_available": data_available,
                "capabilities": self.get_capabilities(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": "infrastructure_analyst",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
infrastructure_analyst = InfrastructureAnalystAgent()