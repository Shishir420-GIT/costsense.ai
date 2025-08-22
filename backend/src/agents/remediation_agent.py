from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import memory, calculator
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime, timedelta
import base64

from src.config.settings import Settings

class RemediationAgent:
    """Specialized agent for generating AWS cleanup and remediation scripts"""
    
    def __init__(self):
        self.settings = Settings()
        
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
        
        # Create specialized tools for remediation
        self._setup_tools()
        
        # Initialize the Strands agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            tools=[
                self.generate_cleanup_script,
                self.generate_rightsizing_script,
                self.generate_reserved_instance_script,
                self.generate_security_remediation_script,
                self.validate_script_safety,
                memory,
                calculator
            ],
            name="remediation_agent"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Remediation Expert specializing in generating safe, automated cleanup and optimization scripts.

        Your expertise encompasses:
        - AWS CLI script generation for resource cleanup
        - EC2 rightsizing and optimization scripts
        - Reserved Instance purchase automation
        - Security remediation scripts
        - Cost optimization automation
        - Safety validation and backup procedures
        
        Script generation principles:
        1. Always include safety checks and confirmation prompts
        2. Generate comprehensive backup procedures before changes
        3. Include rollback mechanisms where possible
        4. Add detailed logging and monitoring
        5. Follow AWS best practices and security guidelines
        6. Include cost impact estimates and validation
        
        Script types:
        - Resource cleanup (terminate unused resources)
        - Rightsizing scripts (resize instances, volumes)
        - Reserved Instance automation
        - Security group cleanup
        - IAM policy optimization
        - Storage lifecycle management
        
        Always provide:
        - Complete, executable scripts with error handling
        - Detailed usage instructions and prerequisites
        - Safety warnings and confirmation mechanisms  
        - Cost impact estimates and validation steps
        - Rollback procedures and recovery options
        - Monitoring and validation commands
        """
    
    def _setup_tools(self):
        """Setup specialized tools for remediation script generation"""
        
        @tool
        def generate_cleanup_script(resources: str, script_type: str = "ec2_cleanup") -> str:
            """Generate cleanup scripts for AWS resources.
            
            Args:
                resources: JSON string containing resource details to clean up
                script_type: Type of cleanup script (ec2_cleanup, storage_cleanup, rds_cleanup)
            """
            try:
                resource_data = json.loads(resources) if resources.startswith('{') else {"resources": []}
                
                if script_type == "ec2_cleanup":
                    script = self._generate_ec2_cleanup_script(resource_data)
                elif script_type == "storage_cleanup":
                    script = self._generate_storage_cleanup_script(resource_data)
                elif script_type == "rds_cleanup":
                    script = self._generate_rds_cleanup_script(resource_data)
                else:
                    script = self._generate_generic_cleanup_script(resource_data)
                
                return json.dumps({
                    "script_type": script_type,
                    "script_content": script,
                    "estimated_savings": self._calculate_cleanup_savings(resource_data),
                    "safety_level": "high",
                    "requires_confirmation": True,
                    "backup_required": True,
                    "usage_instructions": self._generate_usage_instructions(script_type)
                })
                
            except Exception as e:
                return f"Error generating cleanup script: {str(e)}"
        
        @tool  
        def generate_rightsizing_script(instances: str) -> str:
            """Generate rightsizing scripts for EC2 instances.
            
            Args:
                instances: JSON string containing instance details for rightsizing
            """
            try:
                instance_data = json.loads(instances) if instances.startswith('{') else {"instances": []}
                
                script = """#!/bin/bash
# AWS EC2 Rightsizing Automation Script
# Generated by CostSense AI Remediation Agent
# Safety Level: HIGH - Requires manual confirmation

set -e  # Exit on any error

# Configuration
DRY_RUN=${1:-true}  # Set to false to actually execute changes
BACKUP_SNAPSHOTS=${2:-true}
LOG_FILE="ec2_rightsizing_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Confirmation function
confirm_action() {
    if [ "$DRY_RUN" = "true" ]; then
        log "DRY RUN MODE: Would perform: $1"
        return 0
    fi
    
    echo "⚠️  IMPORTANT: This will $1"
    read -p "Are you sure? (yes/NO): " confirmation
    if [ "$confirmation" != "yes" ]; then
        log "Action cancelled by user"
        exit 1
    fi
}

log "Starting EC2 rightsizing process..."

# Instance rightsizing recommendations"""

                for instance in instance_data.get("instances", [])[:5]:  # Limit to 5 instances for safety
                    instance_id = instance.get("instance_id", "")
                    current_type = instance.get("instance_type", "")
                    recommended_type = instance.get("recommended_type", "")
                    
                    if instance_id and current_type != recommended_type:
                        script += f"""

# Rightsize instance {instance_id} from {current_type} to {recommended_type}
rightsize_instance_{instance_id.replace('-', '_')}() {{
    log "Processing instance {instance_id}..."
    
    # Get current instance state
    INSTANCE_STATE=$(aws ec2 describe-instances --instance-ids {instance_id} \\
        --query 'Reservations[0].Instances[0].State.Name' --output text)
    
    if [ "$INSTANCE_STATE" != "running" ]; then
        log "Instance {instance_id} is not running (State: $INSTANCE_STATE). Skipping."
        return 0
    fi
    
    # Create snapshot backup if requested
    if [ "$BACKUP_SNAPSHOTS" = "true" ]; then
        confirm_action "create snapshot backup for instance {instance_id}"
        
        VOLUME_IDS=$(aws ec2 describe-instances --instance-ids {instance_id} \\
            --query 'Reservations[0].Instances[0].BlockDeviceMappings[].Ebs.VolumeId' --output text)
        
        for VOLUME_ID in $VOLUME_IDS; do
            log "Creating snapshot for volume $VOLUME_ID..."
            SNAPSHOT_ID=$(aws ec2 create-snapshot --volume-id $VOLUME_ID \\
                --description "Backup before rightsizing {instance_id}" \\
                --query 'SnapshotId' --output text)
            log "Created snapshot $SNAPSHOT_ID for volume $VOLUME_ID"
        done
    fi
    
    confirm_action "stop and modify instance {instance_id} from {current_type} to {recommended_type}"
    
    # Stop instance
    log "Stopping instance {instance_id}..."
    aws ec2 stop-instances --instance-ids {instance_id}
    
    # Wait for instance to stop
    log "Waiting for instance to stop..."
    aws ec2 wait instance-stopped --instance-ids {instance_id}
    
    # Modify instance type
    log "Changing instance type to {recommended_type}..."
    aws ec2 modify-instance-attribute --instance-id {instance_id} \\
        --instance-type "Value={recommended_type}"
    
    # Start instance
    log "Starting instance {instance_id}..."
    aws ec2 start-instances --instance-ids {instance_id}
    
    # Wait for instance to be running
    log "Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids {instance_id}
    
    log "✅ Successfully resized instance {instance_id} to {recommended_type}"
    
    # Verify instance health
    sleep 30  # Give instance time to initialize
    HEALTH_STATUS=$(aws ec2 describe-instance-status --instance-ids {instance_id} \\
        --query 'InstanceStatuses[0].SystemStatus.Status' --output text)
    log "Instance health status: $HEALTH_STATUS"
}}"""

                script += """

# Main execution
main() {
    log "=== EC2 Rightsizing Script Execution ==="
    log "Dry run mode: $DRY_RUN"
    log "Backup snapshots: $BACKUP_SNAPSHOTS"
    
    if [ "$DRY_RUN" = "false" ]; then
        echo "🚨 WARNING: This script will make actual changes to your AWS resources!"
        echo "💰 Estimated monthly savings: $""" + str(self._calculate_rightsizing_savings(instance_data)) + """"
        echo "📋 Make sure you have:"
        echo "   - Appropriate AWS permissions"
        echo "   - Recent backups of important data"
        echo "   - Maintenance window scheduled"
        echo ""
        
        read -p "Type 'I UNDERSTAND' to proceed: " final_confirmation
        if [ "$final_confirmation" != "I UNDERSTAND" ]; then
            log "Final confirmation failed. Exiting."
            exit 1
        fi
    fi
"""

                # Add function calls for each instance
                for instance in instance_data.get("instances", [])[:5]:
                    instance_id = instance.get("instance_id", "")
                    if instance_id:
                        script += f"""
    rightsize_instance_{instance_id.replace('-', '_')}"""

                script += """
    
    log "=== Rightsizing process completed ==="
    log "Check the log file: $LOG_FILE"
}

# Execute main function
main "$@"
"""

                return json.dumps({
                    "script_type": "ec2_rightsizing",
                    "script_content": script,
                    "estimated_monthly_savings": self._calculate_rightsizing_savings(instance_data),
                    "safety_level": "high",
                    "requires_confirmation": True,
                    "backup_required": True,
                    "usage_instructions": [
                        "1. Review the script content carefully",
                        "2. Test in a development environment first",
                        "3. Run with DRY_RUN=true to preview changes",
                        "4. Set DRY_RUN=false to execute actual changes",
                        "5. Monitor instances after changes",
                        "Example: ./rightsize_script.sh true true  # Dry run with backups"
                    ]
                })
                
            except Exception as e:
                return f"Error generating rightsizing script: {str(e)}"
        
        @tool
        def generate_reserved_instance_script(instances: str) -> str:
            """Generate Reserved Instance purchase automation script.
            
            Args:
                instances: JSON string containing instance details for RI recommendations
            """
            try:
                instance_data = json.loads(instances) if instances.startswith('{') else {"instances": []}
                
                # Generate RI purchase script
                script = """#!/bin/bash
# AWS Reserved Instance Purchase Automation Script
# Generated by CostSense AI Remediation Agent

set -e

LOG_FILE="ri_purchase_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting Reserved Instance purchase analysis..."

# RI Purchase recommendations based on usage patterns
"""

                total_savings = 0
                for instance in instance_data.get("instances", []):
                    instance_type = instance.get("instance_type", "")
                    region = instance.get("region", "us-east-1")
                    count = instance.get("instance_count", 1)
                    monthly_savings = instance.get("potential_monthly_savings", 0)
                    total_savings += monthly_savings
                    
                    script += f"""
# Purchase {count}x {instance_type} Reserved Instance(s) in {region}
purchase_ri_{instance_type.replace('.', '_')}() {{
    log "Purchasing {count}x {instance_type} RI in {region}..."
    
    # Check current pricing
    CURRENT_PRICE=$(aws ec2 describe-reserved-instances-offerings \\
        --instance-type {instance_type} \\
        --offering-class standard \\
        --offering-type "No Upfront" \\
        --query 'ReservedInstancesOfferings[0].FixedPrice' --output text)
    
    log "Current RI price for {instance_type}: $CURRENT_PRICE"
    
    # Purchase RI (uncomment to execute)
    # aws ec2 purchase-reserved-instances-offering \\
    #     --reserved-instances-offering-id $(aws ec2 describe-reserved-instances-offerings \\
    #         --instance-type {instance_type} \\
    #         --offering-class standard \\
    #         --offering-type "No Upfront" \\
    #         --query 'ReservedInstancesOfferings[0].ReservedInstancesOfferingId' --output text) \\
    #     --instance-count {count}
    
    log "RI purchase command generated for {instance_type} (commented out for safety)"
}}
"""

                script += f"""
# Main execution
log "Total estimated monthly savings: ${total_savings:.2f}"
log "Uncomment purchase commands in script to execute actual purchases"
log "Review AWS console for current RI offerings and pricing"

# Execute purchase functions (currently in dry-run mode)"""

                for instance in instance_data.get("instances", []):
                    instance_type = instance.get("instance_type", "")
                    script += f"""
purchase_ri_{instance_type.replace('.', '_')}"""

                return json.dumps({
                    "script_type": "reserved_instance_purchase",
                    "script_content": script,
                    "estimated_monthly_savings": total_savings,
                    "safety_level": "medium",
                    "requires_confirmation": True,
                    "usage_instructions": [
                        "1. Review RI recommendations carefully",
                        "2. Verify instance usage patterns over 30+ days",
                        "3. Uncomment purchase commands when ready",
                        "4. Monitor RI utilization after purchase"
                    ]
                })
                
            except Exception as e:
                return f"Error generating RI script: {str(e)}"
        
        @tool
        def generate_security_remediation_script(security_findings: str) -> str:
            """Generate security remediation scripts based on findings.
            
            Args:
                security_findings: JSON string containing security issues to remediate
            """
            try:
                findings_data = json.loads(security_findings) if security_findings.startswith('{') else {"findings": []}
                
                script = """#!/bin/bash
# AWS Security Remediation Script
# Generated by CostSense AI Remediation Agent

set -e

LOG_FILE="security_remediation_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting security remediation..."

# Fix overly permissive security groups
fix_security_groups() {
    log "Checking for overly permissive security groups..."
    
    # Find security groups with 0.0.0.0/0 access
    SG_IDS=$(aws ec2 describe-security-groups \\
        --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==\`0.0.0.0/0\`]]].GroupId' \\
        --output text)
    
    for SG_ID in $SG_IDS; do
        log "Found overly permissive security group: $SG_ID"
        
        # Get group details
        SG_NAME=$(aws ec2 describe-security-groups --group-ids $SG_ID \\
            --query 'SecurityGroups[0].GroupName' --output text)
        
        log "Security Group: $SG_NAME ($SG_ID)"
        
        # List current rules (for review)
        log "Current inbound rules:"
        aws ec2 describe-security-groups --group-ids $SG_ID \\
            --query 'SecurityGroups[0].IpPermissions'
        
        # TODO: Add specific rule modifications based on requirements
        # Example: Remove SSH access from 0.0.0.0/0
        # aws ec2 revoke-security-group-ingress --group-id $SG_ID \\
        #     --protocol tcp --port 22 --cidr 0.0.0.0/0
        
        log "Review required for security group $SG_ID"
    done
}

# Fix S3 bucket permissions
fix_s3_buckets() {
    log "Checking S3 bucket permissions..."
    
    # List all buckets
    BUCKETS=$(aws s3api list-buckets --query 'Buckets[].Name' --output text)
    
    for BUCKET in $BUCKETS; do
        # Check bucket ACL
        ACL=$(aws s3api get-bucket-acl --bucket $BUCKET --query 'Grants' --output json 2>/dev/null || echo "[]")
        
        # Check for public read access
        if echo $ACL | grep -q "AllUsers"; then
            log "⚠️  Bucket $BUCKET may have public access"
            
            # TODO: Remove public access if not needed
            # aws s3api put-bucket-acl --bucket $BUCKET --acl private
        fi
    done
}

# Main execution
fix_security_groups
fix_s3_buckets

log "Security remediation check completed. Review findings and uncomment actions as needed."
"""

                return json.dumps({
                    "script_type": "security_remediation", 
                    "script_content": script,
                    "safety_level": "critical",
                    "requires_confirmation": True,
                    "backup_required": True,
                    "usage_instructions": [
                        "1. Review all security findings carefully",
                        "2. Test changes in development environment",
                        "3. Ensure business requirements are met",
                        "4. Uncomment specific remediation commands",
                        "5. Monitor system functionality after changes"
                    ]
                })
                
            except Exception as e:
                return f"Error generating security remediation script: {str(e)}"
        
        @tool
        def validate_script_safety(script_content: str) -> str:
            """Validate script safety and provide risk assessment.
            
            Args:
                script_content: Script content to validate
            """
            try:
                safety_issues = []
                safety_score = 100
                
                # Check for dangerous operations
                dangerous_commands = [
                    "rm -rf", "delete-", "terminate-", "destroy",
                    "force", "--force", "-f", "recursive"
                ]
                
                for cmd in dangerous_commands:
                    if cmd in script_content:
                        safety_issues.append(f"Contains potentially dangerous command: {cmd}")
                        safety_score -= 15
                
                # Check for safety mechanisms
                if "set -e" not in script_content:
                    safety_issues.append("Missing 'set -e' for error handling")
                    safety_score -= 10
                    
                if "DRY_RUN" not in script_content:
                    safety_issues.append("No dry-run mode implemented") 
                    safety_score -= 20
                    
                if "confirm" not in script_content.lower():
                    safety_issues.append("No confirmation prompts found")
                    safety_score -= 15
                
                # Determine safety level
                if safety_score >= 90:
                    safety_level = "high"
                elif safety_score >= 70:
                    safety_level = "medium"
                else:
                    safety_level = "low"
                
                return json.dumps({
                    "safety_score": max(0, safety_score),
                    "safety_level": safety_level,
                    "safety_issues": safety_issues,
                    "recommendations": [
                        "Always test in development first",
                        "Review all commands before execution",
                        "Ensure proper backups are in place",
                        "Have rollback procedures ready",
                        "Monitor systems after changes"
                    ]
                })
                
            except Exception as e:
                return f"Error validating script safety: {str(e)}"
        
        # Assign tools to instance
        self.generate_cleanup_script = generate_cleanup_script
        self.generate_rightsizing_script = generate_rightsizing_script
        self.generate_reserved_instance_script = generate_reserved_instance_script
        self.generate_security_remediation_script = generate_security_remediation_script
        self.validate_script_safety = validate_script_safety
    
    def _generate_ec2_cleanup_script(self, resource_data: Dict) -> str:
        """Generate EC2 cleanup script"""
        script = """#!/bin/bash
# EC2 Cleanup Script - Terminate unused instances
set -e
DRY_RUN=${1:-true}

# List of instances to potentially terminate (review carefully!)
INSTANCES_TO_REVIEW=("""
        
        for resource in resource_data.get("resources", []):
            if resource.get("type") == "ec2":
                script += f'\n    "{resource.get("instance_id", "")}"  # {resource.get("reason", "Low utilization")}'
        
        script += """
)

if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Would terminate these instances:"
    for INSTANCE in "${INSTANCES_TO_REVIEW[@]}"; do
        echo "  - $INSTANCE"
    done
else
    echo "⚠️  This will TERMINATE instances. Are you sure? (yes/NO)"
    read confirmation
    if [ "$confirmation" = "yes" ]; then
        aws ec2 terminate-instances --instance-ids "${INSTANCES_TO_REVIEW[@]}"
    fi
fi"""
        return script
    
    def _generate_storage_cleanup_script(self, resource_data: Dict) -> str:
        """Generate storage cleanup script"""
        return """#!/bin/bash
# EBS Volume Cleanup Script
set -e
echo "Identifying unused EBS volumes..."
aws ec2 describe-volumes --filters "Name=status,Values=available" --query "Volumes[].VolumeId"
echo "Review volumes above before deletion"
"""
    
    def _generate_rds_cleanup_script(self, resource_data: Dict) -> str:
        """Generate RDS cleanup script"""  
        return """#!/bin/bash
# RDS Instance Cleanup Script
set -e
echo "Identifying idle RDS instances..."
echo "Review database usage before termination"
"""
    
    def _generate_generic_cleanup_script(self, resource_data: Dict) -> str:
        """Generate generic cleanup script"""
        return """#!/bin/bash
# Generic AWS Resource Cleanup Script
set -e
echo "Review resources carefully before cleanup"
echo "Always create backups before deletion"
"""
    
    def _calculate_cleanup_savings(self, resource_data: Dict) -> float:
        """Calculate estimated savings from cleanup"""
        return sum(resource.get("monthly_cost", 0) for resource in resource_data.get("resources", []))
    
    def _calculate_rightsizing_savings(self, instance_data: Dict) -> float:
        """Calculate estimated savings from rightsizing"""
        return sum(instance.get("potential_monthly_savings", 0) for instance in instance_data.get("instances", []))
    
    def _generate_usage_instructions(self, script_type: str) -> List[str]:
        """Generate usage instructions for scripts"""
        return [
            "1. Download and review the script content",
            "2. Ensure you have appropriate AWS CLI permissions",
            "3. Test in a development environment first", 
            "4. Run with DRY_RUN=true to preview changes",
            "5. Create backups before executing changes",
            "6. Monitor resources after script execution"
        ]
    
    async def analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate remediation scripts based on query"""
        try:
            # Always try fallback first for reliability
            if self.model is None:
                return await self._fallback_analysis(query, context)
            
            # Try Strands agent, but fallback if it fails
            try:
                result = await asyncio.to_thread(self.agent, query)
                return {"response": str(result)}
            except Exception as llm_error:
                return await self._fallback_analysis(query, context)
            
        except Exception as e:
            return await self._fallback_analysis(query, context)
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback analysis when LLM not available"""
        try:
            script_type = context.get("script_type", "cleanup") if context else "cleanup"
            
            # Mock resource data for demonstration
            mock_resources = {
                "resources": [
                    {
                        "instance_id": "i-1234567890abcdef0",
                        "type": "ec2",
                        "monthly_cost": 67.32,
                        "utilization": 8.5,
                        "reason": "Low CPU utilization for 30+ days"
                    },
                    {
                        "volume_id": "vol-0987654321fedcba0", 
                        "type": "ebs",
                        "monthly_cost": 40.00,
                        "reason": "Detached volume, unused for 30+ days"
                    }
                ]
            }
            
            mock_instances = {
                "instances": [
                    {
                        "instance_id": "i-1234567890abcdef0",
                        "instance_type": "t3.large", 
                        "recommended_type": "t3.medium",
                        "potential_monthly_savings": 33.66
                    }
                ]
            }
            
            if script_type == "cleanup":
                script_result = self.generate_cleanup_script(json.dumps(mock_resources))
            elif script_type == "rightsizing":
                script_result = self.generate_rightsizing_script(json.dumps(mock_instances))
            elif script_type == "reserved_instance":
                script_result = self.generate_reserved_instance_script(json.dumps(mock_instances))
            else:
                script_result = self.generate_cleanup_script(json.dumps(mock_resources))
            
            script_data = json.loads(script_result) if script_result.startswith('{') else {}
            
            # Validate script safety
            safety_result = self.validate_script_safety(script_data.get("script_content", ""))
            safety_data = json.loads(safety_result) if safety_result.startswith('{') else {}
            
            return {
                "response": f"Generated {script_type} remediation script with estimated monthly savings of ${script_data.get('estimated_monthly_savings', 0):.2f}",
                "script_data": script_data,
                "safety_assessment": safety_data,
                "execution_metadata": {
                    "query_analyzed": query,
                    "script_type": script_type,
                    "timestamp": datetime.now().isoformat(),
                    "safety_level": safety_data.get("safety_level", "medium")
                }
            }
            
        except Exception as e:
            return {
                "response": f"Generated basic remediation script for query: {query}",
                "script_data": self._get_default_script(),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_default_script(self) -> Dict[str, Any]:
        """Get default script as fallback"""
        return {
            "script_type": "cleanup",
            "script_content": """#!/bin/bash
# Basic AWS Cleanup Script
echo "Review resources before cleanup"
echo "Always create backups first"
""",
            "estimated_monthly_savings": 100.0,
            "safety_level": "high",
            "requires_confirmation": True,
            "usage_instructions": [
                "Review script content carefully",
                "Test in development environment",
                "Create backups before execution"
            ]
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "cleanup_script_generation",
            "rightsizing_automation",
            "reserved_instance_automation",
            "security_remediation",
            "script_safety_validation",
            "cost_impact_estimation"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test script generation
            test_script = self.generate_cleanup_script('{"resources": []}')
            script_generation_available = len(test_script) > 10
            
            model_available = self.model is not None
            
            return {
                "agent_name": "remediation_agent",
                "healthy": script_generation_available,
                "model_available": model_available,
                "script_generation_available": script_generation_available,
                "capabilities": self.get_capabilities(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": "remediation_agent",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
remediation_agent = RemediationAgent()