from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands_tools import memory, calculator
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.config.settings import Settings

class ComponentAdvisorAgent:
    """Specialized agent for AWS component recommendations and architecture solutions"""
    
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
        
        # Create specialized tools for component recommendations
        self._setup_tools()
        
        # Initialize the Strands agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            tools=[
                self.recommend_components,
                self.generate_architecture_solutions,
                self.calculate_pricing,
                self.assess_implementation_complexity,
                memory,
                calculator
            ],
            name="component_advisor"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Solution Architect Expert specializing in component recommendations and cost optimization.

        Your expertise encompasses:
        - AWS service selection based on application requirements
        - Cost-effective architecture design
        - Implementation complexity assessment
        - Scalability and performance optimization
        - Best practices and security considerations
        
        Analysis approach:
        1. Parse user requirements to understand application needs
        2. Recommend appropriate AWS services with specific configurations
        3. Provide accurate pricing estimates and monthly costs
        4. Generate top 2 architecture solutions with pros/cons
        5. Assess implementation complexity and timelines
        6. Consider cost optimization opportunities
        
        Component considerations:
        - Application type (web app, API, database, etc.)
        - Scale requirements (traffic, data, users)
        - Performance needs (latency, throughput)
        - Budget constraints and cost optimization
        - Development team expertise
        - Operational complexity preferences
        
        Always provide:
        - Specific AWS service recommendations with configurations
        - Accurate cost estimates with monthly projections
        - Multiple architecture options with trade-offs
        - Implementation guidance and complexity assessment
        - Cost optimization suggestions and alternatives"""
    
    def _setup_tools(self):
        """Setup specialized tools for component recommendations"""
        
        @tool
        def recommend_components(requirements: str) -> str:
            """Recommend AWS components based on application requirements.
            
            Args:
                requirements: User's application requirements and use case
            """
            try:
                # Parse requirements to identify key needs
                req_lower = requirements.lower()
                recommendations = []
                
                # Web application components
                if any(word in req_lower for word in ['web', 'frontend', 'app', 'website']):
                    recommendations.extend([
                        {
                            "service": "Amazon EC2",
                            "component": "t3.medium instance",
                            "description": "General purpose compute for web applications",
                            "pricing": "$0.0416/hour",
                            "use_case": "Web application hosting",
                            "monthly_cost_estimate": 30,
                            "setup_complexity": "Low"
                        },
                        {
                            "service": "Amazon CloudFront",
                            "component": "CDN Distribution",
                            "description": "Global content delivery network",
                            "pricing": "$0.085/GB transfer",
                            "use_case": "Static content delivery and caching",
                            "monthly_cost_estimate": 15,
                            "setup_complexity": "Low"
                        },
                        {
                            "service": "AWS Certificate Manager",
                            "component": "SSL/TLS Certificate",
                            "description": "Free SSL certificates for HTTPS",
                            "pricing": "Free",
                            "use_case": "Secure HTTPS connections",
                            "monthly_cost_estimate": 0,
                            "setup_complexity": "Low"
                        }
                    ])
                
                # Database components
                if any(word in req_lower for word in ['database', 'data', 'storage', 'db']):
                    if 'nosql' in req_lower or 'document' in req_lower:
                        recommendations.append({
                            "service": "Amazon DynamoDB",
                            "component": "On-Demand Table",
                            "description": "Serverless NoSQL database",
                            "pricing": "$1.25/GB/month + requests",
                            "use_case": "High-performance NoSQL applications",
                            "monthly_cost_estimate": 20,
                            "setup_complexity": "Low"
                        })
                    else:
                        recommendations.append({
                            "service": "Amazon RDS",
                            "component": "db.t3.micro PostgreSQL",
                            "description": "Managed relational database",
                            "pricing": "$0.018/hour",
                            "use_case": "Structured data and transactions",
                            "monthly_cost_estimate": 13,
                            "setup_complexity": "Low"
                        })
                
                # API and backend components
                if any(word in req_lower for word in ['api', 'backend', 'server', 'microservice']):
                    recommendations.extend([
                        {
                            "service": "AWS Lambda",
                            "component": "Serverless Functions",
                            "description": "Event-driven compute service",
                            "pricing": "$0.20/1M requests + $0.0000166667/GB-second",
                            "use_case": "API endpoints and background processing",
                            "monthly_cost_estimate": 8,
                            "setup_complexity": "Medium"
                        },
                        {
                            "service": "Amazon API Gateway",
                            "component": "REST API",
                            "description": "Managed API service",
                            "pricing": "$3.50/million requests",
                            "use_case": "API management and routing",
                            "monthly_cost_estimate": 12,
                            "setup_complexity": "Medium"
                        }
                    ])
                
                # File storage
                if any(word in req_lower for word in ['file', 'upload', 'image', 'document', 'storage']):
                    recommendations.append({
                        "service": "Amazon S3",
                        "component": "Standard Storage",
                        "description": "Object storage service",
                        "pricing": "$0.023/GB/month",
                        "use_case": "File storage, backups, and static assets",
                        "monthly_cost_estimate": 5,
                        "setup_complexity": "Low"
                    })
                
                # Monitoring and logging
                recommendations.append({
                    "service": "Amazon CloudWatch",
                    "component": "Monitoring & Logs",
                    "description": "Application monitoring and logging",
                    "pricing": "$0.50/GB ingested",
                    "use_case": "Performance monitoring and troubleshooting",
                    "monthly_cost_estimate": 10,
                    "setup_complexity": "Low"
                })
                
                return json.dumps({
                    "recommendations": recommendations[:6],  # Limit to top 6
                    "total_estimated_cost": sum(r["monthly_cost_estimate"] for r in recommendations[:6])
                })
                
            except Exception as e:
                return f"Error generating component recommendations: {str(e)}"
        
        @tool
        def generate_architecture_solutions(requirements: str, components: str) -> str:
            """Generate top 2 architecture solutions based on requirements and components.
            
            Args:
                requirements: User's application requirements
                components: JSON string of recommended components
            """
            try:
                req_lower = requirements.lower()
                is_web_app = any(word in req_lower for word in ['web', 'app', 'frontend'])
                needs_database = any(word in req_lower for word in ['database', 'data', 'user'])
                needs_api = any(word in req_lower for word in ['api', 'backend', 'server'])
                
                solutions = []
                
                # Serverless-first solution
                serverless_components = ['AWS Lambda', 'API Gateway', 'DynamoDB', 'S3', 'CloudFront']
                serverless_cost = 45
                if needs_database and 'nosql' not in req_lower:
                    serverless_components[2] = 'RDS Aurora Serverless'
                    serverless_cost = 52
                
                solutions.append({
                    "name": "Serverless-First Solution",
                    "architecture": serverless_components,
                    "total_monthly_cost": serverless_cost,
                    "pros": [
                        "Low operational overhead",
                        "Auto-scaling capabilities",
                        "Pay-per-use pricing model",
                        "High availability built-in"
                    ],
                    "cons": [
                        "Cold start latency",
                        "Vendor lock-in",
                        "Limited runtime duration",
                        "Debugging complexity"
                    ],
                    "implementation_time": "2-3 weeks",
                    "confidence": 92
                })
                
                # Traditional EC2 solution
                traditional_components = ['EC2 (t3.medium)', 'RDS PostgreSQL', 'S3', 'CloudFront', 'Application Load Balancer']
                traditional_cost = 68
                if not is_web_app:
                    traditional_components[3] = 'Route 53'
                    traditional_cost = 63
                
                solutions.append({
                    "name": "Traditional EC2 Solution",
                    "architecture": traditional_components,
                    "total_monthly_cost": traditional_cost,
                    "pros": [
                        "Full server control",
                        "Predictable performance",
                        "Easy debugging and monitoring",
                        "Flexible configuration"
                    ],
                    "cons": [
                        "Server management overhead",
                        "Fixed costs regardless of usage",
                        "Manual scaling required",
                        "Higher operational complexity"
                    ],
                    "implementation_time": "3-4 weeks",
                    "confidence": 88
                })
                
                # Container-based solution (if applicable)
                if needs_api or 'microservice' in req_lower:
                    container_components = ['Amazon ECS', 'Application Load Balancer', 'RDS', 'S3', 'CloudWatch']
                    solutions.append({
                        "name": "Container-Based Solution",
                        "architecture": container_components,
                        "total_monthly_cost": 75,
                        "pros": [
                            "Microservices architecture",
                            "Easy horizontal scaling",
                            "CI/CD friendly",
                            "Resource isolation"
                        ],
                        "cons": [
                            "Container orchestration complexity",
                            "Learning curve",
                            "Additional networking overhead",
                            "More moving parts"
                        ],
                        "implementation_time": "4-5 weeks",
                        "confidence": 85
                    })
                    # Keep only top 2 by confidence
                    solutions.sort(key=lambda x: x["confidence"], reverse=True)
                    solutions = solutions[:2]
                
                return json.dumps({"solutions": solutions})
                
            except Exception as e:
                return f"Error generating architecture solutions: {str(e)}"
        
        @tool
        def calculate_pricing(components: str, usage_pattern: str = "moderate") -> str:
            """Calculate detailed pricing for recommended components.
            
            Args:
                components: JSON string of components
                usage_pattern: Expected usage (light, moderate, heavy)
            """
            try:
                # Usage multipliers
                multipliers = {"light": 0.6, "moderate": 1.0, "heavy": 1.8}
                multiplier = multipliers.get(usage_pattern, 1.0)
                
                pricing_details = {
                    "usage_pattern": usage_pattern,
                    "multiplier": multiplier,
                    "cost_breakdown": [
                        {"category": "Compute", "monthly_cost": 35 * multiplier, "percentage": 45},
                        {"category": "Storage", "monthly_cost": 15 * multiplier, "percentage": 20},
                        {"category": "Network", "monthly_cost": 12 * multiplier, "percentage": 15},
                        {"category": "Database", "monthly_cost": 20 * multiplier, "percentage": 20}
                    ],
                    "total_monthly_cost": 82 * multiplier,
                    "annual_savings_opportunity": (82 * multiplier * 12) * 0.25,  # 25% potential savings
                    "optimization_tips": [
                        "Consider Reserved Instances for 20-40% savings",
                        "Implement auto-scaling to optimize compute costs",
                        "Use S3 Intelligent Tiering for storage optimization",
                        "Monitor and rightsize resources regularly"
                    ]
                }
                
                return json.dumps(pricing_details)
                
            except Exception as e:
                return f"Error calculating pricing: {str(e)}"
        
        @tool
        def assess_implementation_complexity(architecture: str) -> str:
            """Assess implementation complexity and provide guidance.
            
            Args:
                architecture: Architecture solution name or components
            """
            try:
                arch_lower = architecture.lower()
                
                if 'serverless' in arch_lower:
                    complexity = {
                        "overall_complexity": "Medium",
                        "setup_time": "2-3 weeks",
                        "team_size": "2-3 developers",
                        "required_skills": [
                            "AWS Lambda development",
                            "API Gateway configuration",
                            "DynamoDB/RDS knowledge",
                            "CloudFormation/SAM"
                        ],
                        "implementation_phases": [
                            {"phase": "Setup & Configuration", "duration": "3-5 days", "effort": "Low"},
                            {"phase": "Core Application Development", "duration": "1-2 weeks", "effort": "Medium"},
                            {"phase": "Integration & Testing", "duration": "3-5 days", "effort": "Medium"},
                            {"phase": "Deployment & Monitoring", "duration": "2-3 days", "effort": "Low"}
                        ],
                        "potential_blockers": [
                            "Lambda cold start optimization",
                            "API Gateway rate limiting",
                            "DynamoDB query patterns"
                        ]
                    }
                elif 'container' in arch_lower:
                    complexity = {
                        "overall_complexity": "High",
                        "setup_time": "4-5 weeks",
                        "team_size": "3-4 developers",
                        "required_skills": [
                            "Docker containerization",
                            "ECS/Fargate management",
                            "Load balancer configuration",
                            "Container orchestration"
                        ],
                        "implementation_phases": [
                            {"phase": "Containerization", "duration": "1 week", "effort": "Medium"},
                            {"phase": "ECS Setup & Configuration", "duration": "1 week", "effort": "High"},
                            {"phase": "Application Development", "duration": "2-3 weeks", "effort": "Medium"},
                            {"phase": "Deployment Pipeline", "duration": "3-5 days", "effort": "High"}
                        ],
                        "potential_blockers": [
                            "Container networking complexity",
                            "Service discovery setup",
                            "CI/CD pipeline configuration"
                        ]
                    }
                else:  # Traditional EC2
                    complexity = {
                        "overall_complexity": "Low",
                        "setup_time": "3-4 weeks",
                        "team_size": "2-3 developers",
                        "required_skills": [
                            "EC2 instance management",
                            "Load balancer setup",
                            "RDS database configuration",
                            "Basic AWS networking"
                        ],
                        "implementation_phases": [
                            {"phase": "Infrastructure Setup", "duration": "3-5 days", "effort": "Low"},
                            {"phase": "Application Development", "duration": "2-3 weeks", "effort": "Medium"},
                            {"phase": "Database Integration", "duration": "3-5 days", "effort": "Medium"},
                            {"phase": "Load Testing & Optimization", "duration": "3-5 days", "effort": "Low"}
                        ],
                        "potential_blockers": [
                            "Manual scaling configuration",
                            "Security group setup",
                            "Database connection management"
                        ]
                    }
                
                return json.dumps(complexity)
                
            except Exception as e:
                return f"Error assessing implementation complexity: {str(e)}"
        
        # Assign tools to instance
        self.recommend_components = recommend_components
        self.generate_architecture_solutions = generate_architecture_solutions
        self.calculate_pricing = calculate_pricing
        self.assess_implementation_complexity = assess_implementation_complexity
    
    async def analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform component recommendation analysis based on query"""
        try:
            # Use LLaMA 3.2 with Strands agent and tools orchestration
            if self.model is not None:
                # Create a comprehensive prompt for the agent to use its tools
                orchestration_prompt = f"""
                You are an AWS Solutions Architect. A user has asked: "{query}"

                Please analyze their requirements and provide AWS component recommendations using your tools:
                1. Use recommend_components to identify the best AWS services
                2. Use generate_architecture_solutions to create architecture options
                3. Use calculate_pricing to provide cost analysis
                
                Then provide a professional response explaining your recommendations.
                """
                
                # Let the Strands agent use its tools and generate response
                result = await asyncio.to_thread(self.agent, orchestration_prompt)
                
                # Check if the LLM response indicates an invalid or insufficient request
                llm_response = str(result).lower()
                is_valid_request = self._is_valid_technical_request(query, llm_response)
                
                if is_valid_request:
                    # Only get structured data for valid technical requests
                    components_result = self.recommend_components(query)
                    components_data = json.loads(components_result) if components_result.startswith('{') else {"recommendations": []}
                    
                    solutions_result = self.generate_architecture_solutions(query, components_result)
                    solutions_data = json.loads(solutions_result) if solutions_result.startswith('{') else {"solutions": []}
                    
                    pricing_result = self.calculate_pricing(components_result, self._determine_usage_pattern(query))
                    pricing_data = json.loads(pricing_result) if pricing_result.startswith('{') else {}
                    
                    return {
                        "response": str(result),  # Real LLM response
                        "recommendations": components_data.get("recommendations", []),
                        "solutions": solutions_data.get("solutions", []),
                        "pricing": pricing_data,
                        "analysis_metadata": {
                            "query_analyzed": query,
                            "timestamp": datetime.now().isoformat(),
                            "analysis_method": "llama_strands_orchestrated"
                        }
                    }
                else:
                    # Return only the LLM response without structured data for invalid requests
                    return {
                        "response": str(result),  # Real LLM response explaining the issue
                        "recommendations": [],
                        "solutions": [],
                        "pricing": {},
                        "analysis_metadata": {
                            "query_analyzed": query,
                            "timestamp": datetime.now().isoformat(),
                            "analysis_method": "llama_strands_orchestrated",
                            "request_type": "invalid_or_insufficient"
                        }
                    }
            else:
                # If no model, don't use fallback - raise error instead
                raise Exception("No LLM model available")
            
        except Exception as e:
            # Only fallback if absolutely necessary
            raise Exception(f"LLM orchestration failed: {str(e)}")
    
    async def _strands_orchestrated_analysis(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use Strands framework with LLM orchestration"""
        try:
            # Simpler approach: Let the LLM generate natural response while tools provide structured data
            llm_prompt = f"""
            You are an AWS Solutions Architect. A user has asked: "{query}"
            
            Please provide a professional, detailed analysis of their requirements and explain what AWS components would be best suited for their needs. 
            Focus on why specific components were chosen and how they work together to solve their problem.
            Be comprehensive but conversational in your explanation.
            """
            
            # Get LLM response
            if self.model is not None:
                llm_response = await asyncio.to_thread(self.agent, llm_prompt)
                
                # Get structured data from tools
                components_result = self.recommend_components(query)
                components_data = json.loads(components_result) if components_result.startswith('{') else {"recommendations": []}
                
                solutions_result = self.generate_architecture_solutions(query, components_result)
                solutions_data = json.loads(solutions_result) if solutions_result.startswith('{') else {"solutions": []}
                
                pricing_result = self.calculate_pricing(components_result, self._determine_usage_pattern(query))
                pricing_data = json.loads(pricing_result) if pricing_result.startswith('{') else {}
                
                top_solution = solutions_data.get("solutions", [{}])[0] if solutions_data.get("solutions") else {}
                complexity_result = self.assess_implementation_complexity(top_solution.get("name", ""))
                complexity_data = json.loads(complexity_result) if complexity_result.startswith('{') else {}
                
                return {
                    "response": str(llm_response),  # Use the LLM-generated response
                    "recommendations": components_data.get("recommendations", []),
                    "solutions": solutions_data.get("solutions", []),
                    "pricing": pricing_data,
                    "implementation_complexity": complexity_data,
                    "analysis_metadata": {
                        "query_analyzed": query,
                        "timestamp": datetime.now().isoformat(),
                        "components_recommended": len(components_data.get("recommendations", [])),
                        "solutions_generated": len(solutions_data.get("solutions", [])),
                        "analysis_method": "gemma_llm_orchestrated"
                    }
                }
            else:
                # Fallback if no model available
                raise Exception("No LLM model available for orchestration")
            
        except Exception as e:
            # If orchestrated analysis fails, fall back to basic analysis
            raise Exception(f"Strands orchestration failed: {str(e)}")
    
    async def _extract_structured_response(self, query: str, agent_response: str) -> Dict[str, Any]:
        """Extract structured data from agent response and combine with tool outputs"""
        try:
            # Still use tools directly to get structured data for frontend
            components_result = self.recommend_components(query)
            components_data = json.loads(components_result) if components_result.startswith('{') else {"recommendations": []}
            
            solutions_result = self.generate_architecture_solutions(query, components_result)
            solutions_data = json.loads(solutions_result) if solutions_result.startswith('{') else {"solutions": []}
            
            pricing_result = self.calculate_pricing(components_result, self._determine_usage_pattern(query))
            pricing_data = json.loads(pricing_result) if pricing_result.startswith('{') else {}
            
            top_solution = solutions_data.get("solutions", [{}])[0] if solutions_data.get("solutions") else {}
            complexity_result = self.assess_implementation_complexity(top_solution.get("name", ""))
            complexity_data = json.loads(complexity_result) if complexity_result.startswith('{') else {}
            
            return {
                "response": agent_response,  # Use the LLM-generated response
                "recommendations": components_data.get("recommendations", []),
                "solutions": solutions_data.get("solutions", []),
                "pricing": pricing_data,
                "implementation_complexity": complexity_data,
                "analysis_metadata": {
                    "query_analyzed": query,
                    "timestamp": datetime.now().isoformat(),
                    "components_recommended": len(components_data.get("recommendations", [])),
                    "solutions_generated": len(solutions_data.get("solutions", [])),
                    "analysis_method": "strands_llm_orchestrated"
                }
            }
            
        except Exception as e:
            return {
                "response": agent_response,  # Still use LLM response even if tools fail
                "recommendations": self._get_default_recommendations(),
                "solutions": self._get_default_solutions(),
                "error": f"Tool extraction failed: {str(e)}",
                "analysis_metadata": {
                    "query_analyzed": query,
                    "timestamp": datetime.now().isoformat(),
                    "analysis_method": "strands_llm_only"
                }
            }
    
    async def _generate_ai_response(self, query: str, components_data: Dict, solutions_data: Dict, pricing_data: Dict) -> str:
        """Generate AI response using Strands agent if available, otherwise use template"""
        try:
            if self.model is not None:
                # Try to use Strands agent for natural language generation
                context_prompt = f"""
                Based on the user query: "{query}"
                
                I have analyzed their requirements and generated:
                - {len(components_data.get('recommendations', []))} AWS component recommendations
                - {len(solutions_data.get('solutions', []))} architecture solutions
                - Detailed pricing breakdown with ${pricing_data.get('total_monthly_cost', 0)}/month estimated cost
                
                Please provide a professional, conversational response that explains these recommendations in context.
                Be specific about why these components were chosen and highlight the key benefits.
                """
                
                result = await asyncio.to_thread(self.agent, context_prompt)
                if result and len(str(result)) > 50:  # Ensure we got a meaningful response
                    return str(result)
            
            # Fallback to template-based response
            return self._generate_response_text(query, components_data, solutions_data)
            
        except Exception:
            # Always fallback to template if AI generation fails
            return self._generate_response_text(query, components_data, solutions_data)
    
    def _determine_usage_pattern(self, query: str) -> str:
        """Determine usage pattern from query context"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['startup', 'small', 'prototype', 'mvp', 'test']):
            return "light"
        elif any(word in query_lower for word in ['enterprise', 'large', 'scale', 'production', 'heavy', 'high traffic']):
            return "heavy"
        else:
            return "moderate"
    
    def _is_valid_technical_request(self, query: str, llm_response: str) -> bool:
        """Determine if the query is a valid technical request that should return structured data"""
        
        # Check if LLM response indicates invalid/insufficient request
        invalid_indicators = [
            "not a valid request",
            "not valid",
            "need more information",
            "provide more details",
            "specific requirements",
            "no specific requirements",
            "trying to test",
            "testing the limits",
            "ask for more information"
        ]
        
        if any(indicator in llm_response for indicator in invalid_indicators):
            return False
        
        # Check if query contains technical requirements
        technical_keywords = [
            'web', 'app', 'application', 'website', 'api', 'database', 'storage', 'server',
            'backend', 'frontend', 'microservice', 'service', 'data', 'analytics', 'ml',
            'machine learning', 'aws', 'cloud', 'compute', 'lambda', 'ec2', 'rds', 's3',
            'scaling', 'load', 'traffic', 'users', 'authentication', 'security', 'monitoring'
        ]
        
        query_lower = query.lower()
        has_technical_content = any(keyword in query_lower for keyword in technical_keywords)
        
        # Query should be reasonably long and contain technical content
        is_substantial_query = len(query.strip()) > 5 and has_technical_content
        
        return is_substantial_query
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback analysis when LLM not available"""
        try:
            # Generate component recommendations
            components_result = self.recommend_components(query)
            components_data = json.loads(components_result) if components_result.startswith('{') else {"recommendations": []}
            
            # Generate architecture solutions
            solutions_result = self.generate_architecture_solutions(query, components_result)
            solutions_data = json.loads(solutions_result) if solutions_result.startswith('{') else {"solutions": []}
            
            # Calculate pricing
            pricing_result = self.calculate_pricing(components_result)
            pricing_data = json.loads(pricing_result) if pricing_result.startswith('{') else {}
            
            # Generate response text based on query analysis
            response_text = self._generate_response_text(query, components_data, solutions_data)
            
            return {
                "response": response_text,
                "recommendations": components_data.get("recommendations", []),
                "solutions": solutions_data.get("solutions", []),
                "pricing": pricing_data,
                "analysis_metadata": {
                    "query_analyzed": query,
                    "timestamp": datetime.now().isoformat(),
                    "components_recommended": len(components_data.get("recommendations", [])),
                    "solutions_generated": len(solutions_data.get("solutions", []))
                }
            }
            
        except Exception as e:
            return {
                "response": f"I've analyzed your requirements for '{query}'. Here are my recommendations based on AWS best practices and cost optimization.",
                "recommendations": self._get_default_recommendations(),
                "solutions": self._get_default_solutions(),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_response_text(self, query: str, components_data: Dict, solutions_data: Dict) -> str:
        """Generate natural language response text"""
        req_lower = query.lower()
        
        # Analyze what type of application they're building
        app_type = "application"
        if any(word in req_lower for word in ['web', 'website', 'frontend']):
            app_type = "web application"
        elif any(word in req_lower for word in ['api', 'microservice', 'backend']):
            app_type = "API service"
        elif any(word in req_lower for word in ['mobile', 'app']):
            app_type = "mobile application backend"
        elif any(word in req_lower for word in ['data', 'analytics', 'ml']):
            app_type = "data processing system"
        
        recommendations_count = len(components_data.get("recommendations", []))
        solutions_count = len(solutions_data.get("solutions", []))
        
        total_cost = components_data.get("total_estimated_cost", 0)
        
        response = f"I've analyzed your requirements for a {app_type}. "
        
        if recommendations_count > 0:
            response += f"I've identified {recommendations_count} key AWS components that would be ideal for your use case, "
            response += f"with an estimated monthly cost of ${total_cost}. "
        
        if solutions_count > 0:
            response += f"I've also prepared {solutions_count} complete architecture solutions with detailed cost breakdowns and implementation guidance. "
        
        response += "Each recommendation includes pricing analysis, setup complexity assessment, and specific use case alignment. "
        response += "The solutions are ranked by confidence level and include pros/cons to help you make the best decision for your project."
        
        return response
    
    def _get_default_recommendations(self) -> List[Dict]:
        """Get default component recommendations as fallback"""
        return [
            {
                "service": "Amazon EC2",
                "component": "t3.medium instance",
                "description": "General purpose compute for applications",
                "pricing": "$0.0416/hour",
                "use_case": "Application hosting",
                "monthly_cost_estimate": 30,
                "setup_complexity": "Low"
            },
            {
                "service": "Amazon RDS",
                "component": "db.t3.micro PostgreSQL",
                "description": "Managed relational database",
                "pricing": "$0.018/hour",
                "use_case": "Application database",
                "monthly_cost_estimate": 13,
                "setup_complexity": "Low"
            },
            {
                "service": "Amazon S3",
                "component": "Standard Storage",
                "description": "Object storage service",
                "pricing": "$0.023/GB/month",
                "use_case": "File storage and backups",
                "monthly_cost_estimate": 5,
                "setup_complexity": "Low"
            }
        ]
    
    def _get_default_solutions(self) -> List[Dict]:
        """Get default architecture solutions as fallback"""
        return [
            {
                "name": "Serverless Solution",
                "architecture": ["AWS Lambda", "API Gateway", "DynamoDB", "S3", "CloudFront"],
                "total_monthly_cost": 45,
                "pros": ["Auto-scaling", "Pay-per-use", "Low operational overhead"],
                "cons": ["Cold start latency", "Vendor lock-in"],
                "implementation_time": "2-3 weeks",
                "confidence": 90
            },
            {
                "name": "Traditional EC2 Solution",
                "architecture": ["EC2 (t3.medium)", "RDS", "S3", "CloudFront", "ALB"],
                "total_monthly_cost": 68,
                "pros": ["Full control", "Predictable performance", "Easy debugging"],
                "cons": ["Server management", "Fixed costs"],
                "implementation_time": "3-4 weeks",
                "confidence": 85
            }
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "aws_component_recommendations",
            "architecture_solution_design",
            "cost_estimation_and_optimization",
            "implementation_complexity_assessment",
            "pricing_analysis",
            "solution_comparison"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test component recommendation
            test_result = self.recommend_components("simple web application")
            recommendations_available = len(test_result) > 10
            
            model_available = self.model is not None
            
            return {
                "agent_name": "component_advisor",
                "healthy": recommendations_available,
                "model_available": model_available,
                "recommendations_available": recommendations_available,
                "capabilities": self.get_capabilities(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": "component_advisor",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
component_advisor = ComponentAdvisorAgent()