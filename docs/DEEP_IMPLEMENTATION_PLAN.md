# Deep Implementation Plan: Critical Issues Resolution

## Executive Summary

Based on comprehensive codebase analysis, this document provides a strategic, phase-based implementation plan to address the four critical issues identified in the CostSense-AI agent orchestration system. The plan emphasizes security-first approach, maintains system reliability during transitions, and includes comprehensive testing and monitoring strategies.

---

## Current State Analysis

### **Security Vulnerabilities Identified**
- **CRITICAL**: Zero PII detection mechanisms across all input channels
- **HIGH**: No input validation or sanitization in agent endpoints
- **HIGH**: Raw user input passed directly to LLM without filtering
- **MEDIUM**: Potential injection vulnerabilities in script generation (remediation agent)

### **System Resilience Gaps**
- **HIGH**: Basic fallback mechanisms but no circuit breaker patterns
- **HIGH**: AWS API calls lack retry logic and rate limiting
- **MEDIUM**: No graceful degradation under high load

### **Monitoring & Observability Deficits**
- **HIGH**: Basic file logging only - no structured logging or metrics
- **HIGH**: No performance monitoring or SLA tracking
- **MEDIUM**: No error rate monitoring or alerting

### **Prompt Engineering Issues**
- **HIGH**: Inconsistent output formats across agents
- **MEDIUM**: No few-shot learning examples in system prompts
- **MEDIUM**: No output validation or schema enforcement

---

# 🎯 PHASE 1: SECURITY FOUNDATION (Week 1-2)
*Priority: CRITICAL - Security vulnerabilities must be addressed first*

## 1.1 Comprehensive Safety Guards Architecture

### **Implementation Strategy**
Create a layered security approach with input validation, PII detection, output sanitization, and audit logging.

### **Technical Implementation**

```python
# NEW FILE: backend/src/security/safety_guards.py
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, validator
import re
import hashlib
import logging
from datetime import datetime
from enum import Enum
import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PIIType(Enum):
    EMAIL = "email"
    SSN = "ssn" 
    CREDIT_CARD = "credit_card"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    AWS_KEY = "aws_key"
    PERSON_NAME = "person"
    ORGANIZATION = "organization"

class SafetyViolation(BaseModel):
    """Model for safety violations"""
    violation_type: str
    severity: SecurityLevel
    location: str
    description: str
    suggested_action: str
    detected_content: Optional[str] = None

class ComprehensiveSafetyGuard:
    """
    Multi-layered safety guard system for agent input/output validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize PII detection engines
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Load NLP model for advanced detection
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model not found, using basic patterns only")
            self.nlp = None
        
        # Compile regex patterns for performance
        self._compile_security_patterns()
        
        # Initialize audit logger
        self._setup_security_audit_logging()
    
    def _compile_security_patterns(self):
        """Compile regex patterns for efficient matching"""
        self.patterns = {
            PIIType.EMAIL: re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                re.IGNORECASE
            ),
            PIIType.SSN: re.compile(
                r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b'
            ),
            PIIType.CREDIT_CARD: re.compile(
                r'\b(?:\d[ -]*?){13,16}\b'
            ),
            PIIType.PHONE: re.compile(
                r'\b(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
            ),
            PIIType.IP_ADDRESS: re.compile(
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ),
            PIIType.AWS_KEY: re.compile(
                r'AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key',
                re.IGNORECASE
            )
        }
        
        # Malicious input patterns
        self.malicious_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'eval\s*\(', re.IGNORECASE),
            re.compile(r'exec\s*\(', re.IGNORECASE),
            re.compile(r'__import__', re.IGNORECASE),
            re.compile(r'subprocess|os\.system|os\.popen', re.IGNORECASE)
        ]
    
    def _setup_security_audit_logging(self):
        """Setup dedicated security audit logging"""
        self.audit_logger = logging.getLogger("security_audit")
        
        # Create separate log file for security events
        security_handler = logging.FileHandler(
            f"logs/security_audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        security_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
        )
        self.audit_logger.addHandler(security_handler)
        self.audit_logger.setLevel(logging.WARNING)
    
    def validate_and_sanitize_input(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        request_id: Optional[str] = None
    ) -> Tuple[str, List[SafetyViolation]]:
        """
        Comprehensive input validation and sanitization
        
        Returns:
            Tuple of (sanitized_input, violations_found)
        """
        violations = []
        original_input = user_input
        request_id = request_id or self._generate_request_id()
        
        # Step 1: Basic sanitization
        sanitized_input = self._basic_sanitization(user_input)
        
        # Step 2: PII Detection and handling
        pii_violations = self._detect_pii(sanitized_input, request_id)
        violations.extend(pii_violations)
        
        # Step 3: Malicious content detection
        malicious_violations = self._detect_malicious_content(sanitized_input, request_id)
        violations.extend(malicious_violations)
        
        # Step 4: Content length and structure validation
        structure_violations = self._validate_input_structure(sanitized_input)
        violations.extend(structure_violations)
        
        # Step 5: Advanced NLP-based analysis (if available)
        if self.nlp:
            nlp_violations = self._advanced_content_analysis(sanitized_input)
            violations.extend(nlp_violations)
        
        # Step 6: Final sanitization based on violations
        final_input = self._apply_final_sanitization(sanitized_input, violations)
        
        # Log security events
        if violations:
            self._log_security_event(request_id, original_input, violations, context)
        
        return final_input, violations
    
    def _basic_sanitization(self, text: str) -> str:
        """Apply basic sanitization rules"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Limit input length (prevent DoS)
        if len(sanitized) > 10000:  # 10KB limit
            sanitized = sanitized[:10000]
            self.logger.warning("Input truncated due to length limit")
        
        # Remove potentially dangerous HTML/JavaScript
        sanitized = re.sub(r'<[^>]*>', '', sanitized)
        
        # Escape special characters for safety
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for char, replacement in dangerous_chars.items():
            sanitized = sanitized.replace(char, replacement)
        
        return sanitized.strip()
    
    def _detect_pii(self, text: str, request_id: str) -> List[SafetyViolation]:
        """Comprehensive PII detection"""
        violations = []
        
        # Use Presidio for advanced PII detection
        try:
            results = self.analyzer.analyze(text=text, language='en')
            
            for result in results:
                violation = SafetyViolation(
                    violation_type=f"pii_{result.entity_type.lower()}",
                    severity=SecurityLevel.HIGH if result.entity_type in ['CREDIT_CARD', 'SSN'] else SecurityLevel.MEDIUM,
                    location=f"characters {result.start}-{result.end}",
                    description=f"Detected {result.entity_type} with confidence {result.score}",
                    suggested_action="Remove or anonymize PII before processing",
                    detected_content=text[result.start:result.end]
                )
                violations.append(violation)
                
        except Exception as e:
            self.logger.warning(f"Presidio analysis failed: {e}")
            # Fallback to regex patterns
            violations.extend(self._regex_pii_detection(text))
        
        return violations
    
    def _regex_pii_detection(self, text: str) -> List[SafetyViolation]:
        """Fallback regex-based PII detection"""
        violations = []
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                severity = SecurityLevel.CRITICAL if pii_type in [PIIType.SSN, PIIType.CREDIT_CARD] else SecurityLevel.HIGH
                
                violation = SafetyViolation(
                    violation_type=f"pii_{pii_type.value}",
                    severity=severity,
                    location=f"characters {match.start()}-{match.end()}",
                    description=f"Detected potential {pii_type.value}",
                    suggested_action="Remove or anonymize before processing",
                    detected_content=match.group()
                )
                violations.append(violation)
        
        return violations
    
    def _detect_malicious_content(self, text: str, request_id: str) -> List[SafetyViolation]:
        """Detect potentially malicious content"""
        violations = []
        
        for i, pattern in enumerate(self.malicious_patterns):
            matches = pattern.finditer(text)
            
            for match in matches:
                violation = SafetyViolation(
                    violation_type="malicious_content",
                    severity=SecurityLevel.CRITICAL,
                    location=f"characters {match.start()}-{match.end()}",
                    description=f"Detected potentially malicious pattern: {pattern.pattern[:50]}...",
                    suggested_action="Block request and investigate",
                    detected_content=match.group()[:100]
                )
                violations.append(violation)
                
                # Log critical security event immediately
                self.audit_logger.critical(
                    f"MALICIOUS_CONTENT_DETECTED - Request: {request_id}, Pattern: {i}, Content: {match.group()[:50]}"
                )
        
        return violations
    
    def _validate_input_structure(self, text: str) -> List[SafetyViolation]:
        """Validate input structure and format"""
        violations = []
        
        # Check for excessive repetition (potential DoS)
        if self._has_excessive_repetition(text):
            violations.append(SafetyViolation(
                violation_type="excessive_repetition",
                severity=SecurityLevel.MEDIUM,
                location="full_input",
                description="Input contains excessive repetition",
                suggested_action="Reject or truncate repetitive content"
            ))
        
        # Check for unusual encoding
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            violations.append(SafetyViolation(
                violation_type="encoding_issue",
                severity=SecurityLevel.LOW,
                location="full_input",
                description="Input contains unusual encoding",
                suggested_action="Normalize encoding"
            ))
        
        return violations
    
    def _advanced_content_analysis(self, text: str) -> List[SafetyViolation]:
        """Advanced NLP-based content analysis"""
        violations = []
        
        if not self.nlp:
            return violations
        
        try:
            doc = self.nlp(text)
            
            # Detect person names
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    violations.append(SafetyViolation(
                        violation_type="pii_person_name",
                        severity=SecurityLevel.MEDIUM,
                        location=f"characters {ent.start_char}-{ent.end_char}",
                        description=f"Detected person name: {ent.text}",
                        suggested_action="Consider anonymization",
                        detected_content=ent.text
                    ))
                
                # Detect organizations (potential sensitive info)
                elif ent.label_ == "ORG":
                    violations.append(SafetyViolation(
                        violation_type="potential_org_info",
                        severity=SecurityLevel.LOW,
                        location=f"characters {ent.start_char}-{ent.end_char}",
                        description=f"Detected organization: {ent.text}",
                        suggested_action="Review for sensitivity",
                        detected_content=ent.text
                    ))
        
        except Exception as e:
            self.logger.warning(f"NLP analysis failed: {e}")
        
        return violations
    
    def _has_excessive_repetition(self, text: str) -> bool:
        """Check for excessive repetition in text"""
        words = text.split()
        if len(words) < 10:
            return False
        
        # Check for repeated phrases
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        # If any word appears more than 30% of the time, it's excessive
        max_count = max(word_count.values())
        return max_count > len(words) * 0.3
    
    def _apply_final_sanitization(self, text: str, violations: List[SafetyViolation]) -> str:
        """Apply final sanitization based on detected violations"""
        sanitized = text
        
        # Remove or anonymize content based on violations
        for violation in violations:
            if violation.severity in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                if violation.detected_content:
                    # Replace with anonymized version
                    if violation.violation_type.startswith('pii_'):
                        replacement = f"[{violation.violation_type.upper()}_REDACTED]"
                        sanitized = sanitized.replace(violation.detected_content, replacement)
                    elif violation.violation_type == 'malicious_content':
                        # Remove malicious content entirely
                        sanitized = sanitized.replace(violation.detected_content, "[CONTENT_REMOVED]")
        
        return sanitized
    
    def _log_security_event(
        self, 
        request_id: str, 
        original_input: str, 
        violations: List[SafetyViolation],
        context: Dict[str, Any] = None
    ):
        """Log security events for audit and monitoring"""
        
        event_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "input_length": len(original_input),
            "violations_count": len(violations),
            "violations": [v.dict() for v in violations],
            "context": context or {},
            "input_hash": hashlib.sha256(original_input.encode()).hexdigest()[:16]
        }
        
        # Log based on highest severity
        max_severity = max([v.severity for v in violations], default=SecurityLevel.LOW)
        
        if max_severity == SecurityLevel.CRITICAL:
            self.audit_logger.critical(f"CRITICAL_SECURITY_VIOLATION: {event_data}")
        elif max_severity == SecurityLevel.HIGH:
            self.audit_logger.error(f"HIGH_SECURITY_VIOLATION: {event_data}")
        elif max_severity == SecurityLevel.MEDIUM:
            self.audit_logger.warning(f"MEDIUM_SECURITY_VIOLATION: {event_data}")
        else:
            self.audit_logger.info(f"LOW_SECURITY_VIOLATION: {event_data}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]}"
    
    def validate_output(self, output: str, agent_name: str) -> Tuple[str, List[SafetyViolation]]:
        """Validate agent output before returning to user"""
        violations = []
        
        # Check for leaked PII in output
        pii_violations = self._detect_pii(output, f"output_{agent_name}")
        violations.extend(pii_violations)
        
        # Check for potential data leakage
        if self._contains_internal_data(output):
            violations.append(SafetyViolation(
                violation_type="internal_data_leak",
                severity=SecurityLevel.HIGH,
                location="output",
                description="Output contains internal system information",
                suggested_action="Sanitize output before returning"
            ))
        
        # Apply output sanitization
        sanitized_output = self._sanitize_output(output, violations)
        
        return sanitized_output, violations
    
    def _contains_internal_data(self, output: str) -> bool:
        """Check if output contains internal system data"""
        internal_patterns = [
            r'arn:aws:[^:]*:[^:]*:\d{12}:',  # AWS ARNs with account IDs
            r'AKIA[0-9A-Z]{16}',  # AWS Access Keys
            r'aws_access_key_id.*=.*[A-Z0-9]{20}',
            r'localhost:\d+',  # Local endpoints
            r'/home/[^/\s]+',  # File paths
            r'password.*=.*\w+',  # Passwords in configs
        ]
        
        for pattern in internal_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True
        
        return False
    
    def _sanitize_output(self, output: str, violations: List[SafetyViolation]) -> str:
        """Sanitize output based on violations"""
        sanitized = output
        
        for violation in violations:
            if violation.detected_content and violation.severity in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                replacement = f"[{violation.violation_type.upper()}_SANITIZED]"
                sanitized = sanitized.replace(violation.detected_content, replacement)
        
        return sanitized

# Global instance
safety_guard = ComprehensiveSafetyGuard()
```

### **Integration Points**

```python
# NEW FILE: backend/src/security/middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
from .safety_guards import safety_guard, SecurityLevel

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for all API endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security checks for health endpoints
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        # Extract request body if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Parse JSON body
                    body_data = json.loads(body.decode())
                    
                    # Validate each string field
                    sanitized_data = {}
                    violations_found = []
                    
                    for key, value in body_data.items():
                        if isinstance(value, str):
                            sanitized_value, violations = safety_guard.validate_and_sanitize_input(
                                value, 
                                context={"endpoint": request.url.path, "field": key},
                                request_id=request.headers.get("x-request-id")
                            )
                            sanitized_data[key] = sanitized_value
                            violations_found.extend(violations)
                        else:
                            sanitized_data[key] = value
                    
                    # Block request if critical violations found
                    critical_violations = [v for v in violations_found if v.severity == SecurityLevel.CRITICAL]
                    if critical_violations:
                        raise HTTPException(
                            status_code=400,
                            detail="Request blocked due to security policy violations"
                        )
                    
                    # Replace request body with sanitized version
                    sanitized_body = json.dumps(sanitized_data).encode()
                    
                    # Create new request with sanitized body
                    async def receive():
                        return {"type": "http.request", "body": sanitized_body}
                    
                    request._receive = receive
            
            except json.JSONDecodeError:
                # Non-JSON request, skip body validation
                pass
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Security validation error: {str(e)}")
        
        # Continue with request
        response = await call_next(request)
        
        return response
```

## 1.2 Implementation Timeline & Dependencies

### **Week 1: Core Security Infrastructure**
- **Days 1-2**: Implement `ComprehensiveSafetyGuard` class
- **Days 3-4**: Create security middleware and integration points
- **Days 5-6**: Add comprehensive testing and validation
- **Day 7**: Deploy to staging environment

### **Week 2: Integration & Hardening**
- **Days 8-9**: Integrate security guards into all agent endpoints
- **Days 10-11**: Implement output validation for all agents
- **Days 12-13**: Add security monitoring and alerting
- **Day 14**: Production deployment and monitoring

---

# 🚀 PHASE 2: PROMPT ENGINEERING ENHANCEMENT (Week 2-3)
*Priority: HIGH - Directly impacts user experience and output quality*

## 2.1 Structured Prompt Framework

### **Implementation Strategy**
Create a centralized prompt management system with versioning, A/B testing capabilities, and structured output enforcement.

```python
# NEW FILE: backend/src/prompts/prompt_manager.py
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, validator
from enum import Enum
import json
from datetime import datetime
import hashlib

class OutputFormat(Enum):
    JSON = "json"
    STRUCTURED_TEXT = "structured_text"
    MARKDOWN = "markdown"

class PromptVersion(BaseModel):
    version: str
    prompt_content: str
    examples: List[Dict[str, str]]
    output_format: OutputFormat
    created_at: datetime
    performance_metrics: Optional[Dict[str, float]] = None

class PromptTemplate(BaseModel):
    """Enhanced prompt template with examples and validation"""
    
    agent_role: str
    domain: str
    core_capabilities: List[str]
    available_tools: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    examples: List[Dict[str, Any]]
    quality_guidelines: List[str]
    error_handling_instructions: List[str]

class EnhancedPromptManager:
    """Centralized prompt management with versioning and optimization"""
    
    def __init__(self):
        self.prompt_templates = {}
        self.active_versions = {}
        self.performance_data = {}
        
        # Load default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates for all agents"""
        
        # Cost Analyst Enhanced Prompt
        self.register_prompt_template(
            agent_name="cost_analyst",
            template=PromptTemplate(
                agent_role="AWS Cost Analysis Expert",
                domain="Cloud Cost Optimization",
                core_capabilities=[
                    "Historical spending pattern analysis with statistical significance testing",
                    "Multi-dimensional cost trend identification and forecasting",
                    "Advanced anomaly detection using ML and statistical methods",
                    "Service-level cost attribution and root cause analysis",
                    "ROI-based recommendation prioritization"
                ],
                available_tools=[
                    "get_cost_data_with_validation",
                    "analyze_trends_with_confidence", 
                    "detect_anomalies_advanced",
                    "generate_cost_forecast",
                    "calculate_cost_attribution"
                ],
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 5, "maxLength": 1000},
                        "context": {
                            "type": "object",
                            "properties": {
                                "previous_analysis": {"type": "string"},
                                "business_context": {"type": "string"},
                                "user_constraints": {"type": "object"}
                            }
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "time_period": {"enum": ["7_days", "30_days", "90_days", "1_year"]},
                                "confidence_threshold": {"type": "number", "minimum": 0.5, "maximum": 1.0},
                                "include_forecast": {"type": "boolean"},
                                "focus_services": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "executive_summary": {"type": "string", "minLength": 50},
                        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "analysis_metadata": {
                            "type": "object",
                            "properties": {
                                "data_freshness_hours": {"type": "number"},
                                "coverage_percentage": {"type": "number"},
                                "baseline_period": {"type": "string"}
                            },
                            "required": ["data_freshness_hours", "coverage_percentage"]
                        },
                        "key_insights": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"enum": ["trend", "anomaly", "optimization", "forecast"]},
                                    "finding": {"type": "string", "minLength": 20},
                                    "evidence": {"type": "string"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                    "impact": {"enum": ["critical", "high", "medium", "low"]},
                                    "business_context": {"type": "string"}
                                },
                                "required": ["category", "finding", "evidence", "confidence", "impact"]
                            },
                            "minItems": 1
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string", "minLength": 30},
                                    "action_items": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    },
                                    "effort_estimate": {"type": "string"},
                                    "cost_impact": {
                                        "type": "object",
                                        "properties": {
                                            "monthly_savings": {"type": "number", "minimum": 0},
                                            "implementation_cost": {"type": "number", "minimum": 0},
                                            "payback_period": {"type": "string"},
                                            "annual_impact": {"type": "number"}
                                        },
                                        "required": ["monthly_savings"]
                                    },
                                    "risk_assessment": {
                                        "type": "object",
                                        "properties": {
                                            "level": {"enum": ["low", "medium", "high"]},
                                            "factors": {"type": "array", "items": {"type": "string"}},
                                            "mitigation": {"type": "string"}
                                        },
                                        "required": ["level"]
                                    },
                                    "priority": {"enum": ["p0", "p1", "p2", "p3"]}
                                },
                                "required": ["title", "description", "action_items", "cost_impact", "priority"]
                            }
                        },
                        "next_steps": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "minItems": 2
                        }
                    },
                    "required": ["executive_summary", "confidence_score", "key_insights", "recommendations", "next_steps"]
                },
                examples=[
                    {
                        "input": {
                            "query": "Analyze EC2 cost trends over the last 90 days and identify optimization opportunities",
                            "parameters": {
                                "time_period": "90_days",
                                "confidence_threshold": 0.8,
                                "focus_services": ["EC2", "EBS"]
                            }
                        },
                        "output": {
                            "executive_summary": "EC2 costs have increased 23% over 90 days ($12,450 to $15,300) primarily due to m5.large instance scaling in us-east-1. Identified $3,200/month optimization potential through rightsizing and Reserved Instance purchases.",
                            "confidence_score": 0.87,
                            "analysis_metadata": {
                                "data_freshness_hours": 2,
                                "coverage_percentage": 94.5,
                                "baseline_period": "Previous 90 days"
                            },
                            "key_insights": [
                                {
                                    "category": "trend",
                                    "finding": "EC2 costs increased 23% over 90 days with 15% growth in last 30 days",
                                    "evidence": "Daily cost analysis shows consistent upward trend (R² = 0.82, p < 0.001)",
                                    "confidence": 0.89,
                                    "impact": "high",
                                    "business_context": "Growth-driven scaling but inefficient instance utilization detected"
                                }
                            ],
                            "recommendations": [
                                {
                                    "title": "EC2 Rightsizing for Underutilized Instances",
                                    "description": "15 m5.large instances running at <30% CPU utilization can be downsized to m5.medium",
                                    "action_items": [
                                        "Review CPU and memory utilization metrics for identified instances",
                                        "Test application performance on smaller instance types",
                                        "Implement gradual downsizing with rollback plan"
                                    ],
                                    "effort_estimate": "3-4 engineer days",
                                    "cost_impact": {
                                        "monthly_savings": 1850.00,
                                        "implementation_cost": 200.00,
                                        "payback_period": "immediate",
                                        "annual_impact": 22200.00
                                    },
                                    "risk_assessment": {
                                        "level": "low",
                                        "factors": ["No service interruption", "Reversible changes", "Gradual rollout"],
                                        "mitigation": "Monitor performance closely during transition"
                                    },
                                    "priority": "p1"
                                }
                            ],
                            "next_steps": [
                                "Implement high-priority rightsizing recommendations",
                                "Set up automated cost monitoring alerts for >10% monthly increases",
                                "Schedule Reserved Instance evaluation for stable workloads"
                            ]
                        }
                    }
                ],
                quality_guidelines=[
                    "All cost figures must be quantified with specific dollar amounts",
                    "Confidence scores must be based on statistical analysis, not subjective assessment",
                    "Recommendations must include implementation effort estimates in engineer-hours/days",
                    "All findings must cite specific evidence (metrics, percentages, time periods)",
                    "Business impact must be explained in terms understandable to non-technical stakeholders"
                ],
                error_handling_instructions=[
                    "If data quality is insufficient (confidence < 0.6): Acknowledge limitations and request additional data",
                    "If analysis is ambiguous: Present multiple scenarios with probability weightings", 
                    "If recommendations conflict with business constraints: Explain trade-offs and alternatives",
                    "If AWS API failures occur: Use cached data when available and note data staleness"
                ]
            )
        )
    
    def generate_enhanced_prompt(
        self, 
        agent_name: str, 
        version: Optional[str] = None,
        personalization: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate enhanced prompt with examples and structured output requirements"""
        
        template = self.get_prompt_template(agent_name, version)
        if not template:
            raise ValueError(f"No prompt template found for agent: {agent_name}")
        
        # Build the enhanced prompt
        prompt = f"""# {template.agent_role.upper()}

## IDENTITY & EXPERTISE
You are a {template.agent_role} specializing in {template.domain}.

### Core Capabilities
{chr(10).join(f"- {capability}" for capability in template.core_capabilities)}

### Available Tools
{chr(10).join(f"- {tool}" for tool in template.available_tools)}

## INPUT PROCESSING

### Expected Input Schema
```json
{json.dumps(template.input_schema, indent=2)}
```

### Input Validation Rules
- All string inputs will be sanitized and validated for security
- PII detection is active - personal information will be redacted
- Input length is limited to prevent DoS attacks
- Malicious content patterns will be blocked

## OUTPUT REQUIREMENTS

### Required Output Schema
```json
{json.dumps(template.output_schema, indent=2)}
```

### Output Format Rules
- ALWAYS respond with valid JSON matching the exact schema above
- Include all required fields - partial responses are not acceptable
- Confidence scores must be calculated based on data quality and analysis certainty
- All numeric values must be properly formatted (no NaN, Infinity, or null)
- String fields must not be empty unless explicitly optional

### Quality Standards
{chr(10).join(f"- {guideline}" for guideline in template.quality_guidelines)}

## ANALYSIS EXAMPLES

{self._format_examples(template.examples)}

## ERROR HANDLING & EDGE CASES

{chr(10).join(f"- {instruction}" for instruction in template.error_handling_instructions)}

### Escalation Triggers
Escalate to human supervision when:
- Confidence score drops below 0.5 due to data quality issues
- Potential cost impact exceeds $5,000/month (business critical)
- Security or compliance implications detected in analysis
- Conflicting recommendations from multiple data sources

## PERFORMANCE EXPECTATIONS

- Response time target: <5 seconds for standard queries
- Minimum confidence threshold: 0.6 for actionable recommendations
- Data freshness requirement: Flag if analysis data >24 hours old
- Error recovery: Always provide partial results with clear limitations noted

---

**CRITICAL**: You must ALWAYS respond with valid JSON matching the output schema. Text-only responses will be rejected by the validation system.
"""

        # Add personalization if provided
        if personalization:
            prompt += f"\n\n## PERSONALIZATION\nUser Preferences: {json.dumps(personalization, indent=2)}"
        
        return prompt
    
    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples in a clear, structured way"""
        formatted_examples = []
        
        for i, example in enumerate(examples, 1):
            formatted_example = f"""
### Example {i}

**Input:**
```json
{json.dumps(example['input'], indent=2)}
```

**Expected Output:**
```json
{json.dumps(example['output'], indent=2)}
```
"""
            formatted_examples.append(formatted_example)
        
        return "\n".join(formatted_examples)
    
    def register_prompt_template(self, agent_name: str, template: PromptTemplate):
        """Register a new prompt template"""
        if agent_name not in self.prompt_templates:
            self.prompt_templates[agent_name] = {}
        
        version_id = self._generate_version_id(template)
        
        version = PromptVersion(
            version=version_id,
            prompt_content=self.generate_enhanced_prompt(agent_name),
            examples=template.examples,
            output_format=OutputFormat.JSON,
            created_at=datetime.now()
        )
        
        self.prompt_templates[agent_name][version_id] = {
            "template": template,
            "version": version
        }
        
        # Set as active version if it's the first one
        if agent_name not in self.active_versions:
            self.active_versions[agent_name] = version_id
    
    def get_prompt_template(self, agent_name: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        """Get prompt template for an agent"""
        if agent_name not in self.prompt_templates:
            return None
        
        version_id = version or self.active_versions.get(agent_name)
        if not version_id or version_id not in self.prompt_templates[agent_name]:
            return None
        
        return self.prompt_templates[agent_name][version_id]["template"]
    
    def _generate_version_id(self, template: PromptTemplate) -> str:
        """Generate version ID based on template content"""
        content = json.dumps(template.dict(), sort_keys=True)
        hash_digest = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"v{datetime.now().strftime('%Y%m%d')}_{hash_digest}"

# Global prompt manager instance
prompt_manager = EnhancedPromptManager()
```

## 2.2 Output Validation & Schema Enforcement

```python
# NEW FILE: backend/src/validation/output_validator.py
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional, Union
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    is_valid: bool
    validated_output: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []
    confidence_penalty: float = 0.0

class OutputValidator:
    """Comprehensive output validation for agent responses"""
    
    def __init__(self):
        self.schema_cache = {}
    
    def validate_agent_output(
        self, 
        output: str, 
        agent_name: str, 
        expected_schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate agent output against expected schema"""
        
        try:
            # Try to parse JSON
            if not output.strip():
                return ValidationResult(
                    is_valid=False,
                    errors=["Empty output received"],
                    confidence_penalty=0.5
                )
            
            # Handle both JSON and text responses
            if output.strip().startswith('{'):
                try:
                    parsed_output = json.loads(output)
                except json.JSONDecodeError as e:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Invalid JSON format: {str(e)}"],
                        confidence_penalty=0.3
                    )
            else:
                # Convert text to structured format
                parsed_output = self._convert_text_to_structured(output, agent_name)
            
            # Schema validation if provided
            errors = []
            warnings = []
            confidence_penalty = 0.0
            
            if expected_schema:
                validation_errors = self._validate_against_schema(parsed_output, expected_schema)
                errors.extend(validation_errors)
                
                if validation_errors:
                    confidence_penalty += 0.2
            
            # Content quality validation
            quality_issues = self._validate_content_quality(parsed_output, agent_name)
            warnings.extend(quality_issues)
            
            if quality_issues:
                confidence_penalty += len(quality_issues) * 0.1
            
            # Security validation
            security_issues = self._validate_output_security(parsed_output)
            if security_issues:
                errors.extend(security_issues)
                confidence_penalty += 0.4
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                validated_output=parsed_output,
                errors=errors,
                warnings=warnings,
                confidence_penalty=min(confidence_penalty, 0.8)  # Cap penalty
            )
            
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                confidence_penalty=0.5
            )
    
    def _validate_against_schema(self, output: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate output against JSON schema"""
        try:
            from jsonschema import validate, ValidationError as JsonSchemaValidationError
            validate(instance=output, schema=schema)
            return []
        except JsonSchemaValidationError as e:
            return [f"Schema validation error: {e.message}"]
        except ImportError:
            # Fallback to basic validation if jsonschema not available
            return self._basic_schema_validation(output, schema)
    
    def _basic_schema_validation(self, output: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Basic schema validation without jsonschema library"""
        errors = []
        
        # Check required fields
        required_fields = schema.get('properties', {}).keys()
        for field in required_fields:
            if field not in output:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_content_quality(self, output: Dict[str, Any], agent_name: str) -> List[str]:
        """Validate content quality and completeness"""
        warnings = []
        
        # Check confidence scores
        if 'confidence_score' in output:
            confidence = output['confidence_score']
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                warnings.append("Invalid confidence score format or range")
            elif confidence < 0.6:
                warnings.append(f"Low confidence score: {confidence}")
        
        # Check for placeholder content
        str_content = json.dumps(output)
        placeholder_patterns = ['[PLACEHOLDER]', 'TODO', 'TBD', 'FIXME', 'XXX']
        for pattern in placeholder_patterns:
            if pattern in str_content:
                warnings.append(f"Placeholder content detected: {pattern}")
        
        # Agent-specific validations
        if agent_name == 'cost_analyst':
            warnings.extend(self._validate_cost_analyst_content(output))
        elif agent_name == 'infrastructure_analyst':
            warnings.extend(self._validate_infrastructure_content(output))
        
        return warnings
    
    def _validate_cost_analyst_content(self, output: Dict[str, Any]) -> List[str]:
        """Validate cost analyst specific content"""
        warnings = []
        
        # Check for specific cost figures
        if 'recommendations' in output:
            for rec in output['recommendations']:
                if 'cost_impact' in rec:
                    cost_impact = rec['cost_impact']
                    if 'monthly_savings' in cost_impact:
                        if not isinstance(cost_impact['monthly_savings'], (int, float)) or cost_impact['monthly_savings'] < 0:
                            warnings.append("Invalid monthly savings format or negative value")
        
        # Check for quantified findings
        if 'key_insights' in output:
            for insight in output['key_insights']:
                finding = insight.get('finding', '')
                if not any(char.isdigit() for char in finding):
                    warnings.append("Key insights should include quantified data")
        
        return warnings
    
    def _validate_infrastructure_content(self, output: Dict[str, Any]) -> List[str]:
        """Validate infrastructure analyst specific content"""
        warnings = []
        
        # Check for technical specificity
        if 'recommendations' in output:
            for rec in output['recommendations']:
                if 'instance_type' in rec or 'ec2' in rec.get('description', '').lower():
                    if not any(word in rec.get('description', '') for word in ['CPU', 'memory', 'utilization']):
                        warnings.append("Infrastructure recommendations should include technical details")
        
        return warnings
    
    def _validate_output_security(self, output: Dict[str, Any]) -> List[str]:
        """Check output for security issues"""
        errors = []
        
        # Convert to string for pattern matching
        output_str = json.dumps(output)
        
        # Check for potential data leaks
        security_patterns = [
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'aws_secret_access_key',
            r'password\s*[:=]\s*\w+',
            r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, output_str, re.IGNORECASE):
                errors.append(f"Potential security leak detected: {pattern}")
        
        return errors
    
    def _convert_text_to_structured(self, text_output: str, agent_name: str) -> Dict[str, Any]:
        """Convert text output to structured format"""
        
        # Basic structure for text responses
        structured = {
            "analysis_summary": text_output[:500] + "..." if len(text_output) > 500 else text_output,
            "format": "text_response",
            "confidence_score": 0.7,  # Default confidence for text responses
            "key_insights": [],
            "recommendations": [],
            "next_steps": ["Review detailed analysis", "Consider implementing suggestions"],
            "validation_notes": ["Response was in text format and converted to structured format"]
        }
        
        # Try to extract structured information from text
        lines = text_output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers
            if line.startswith('#') or line.startswith('**'):
                if 'recommendation' in line.lower():
                    current_section = 'recommendations'
                elif 'insight' in line.lower() or 'finding' in line.lower():
                    current_section = 'insights'
                elif 'next step' in line.lower():
                    current_section = 'next_steps'
            
            # Extract content based on current section
            elif current_section == 'recommendations' and line.startswith('•') or line.startswith('-'):
                structured['recommendations'].append({
                    "title": "Extracted Recommendation",
                    "description": line[1:].strip(),
                    "priority": "medium"
                })
            elif current_section == 'insights' and (line.startswith('•') or line.startswith('-')):
                structured['key_insights'].append({
                    "finding": line[1:].strip(),
                    "confidence": 0.7,
                    "category": "analysis"
                })
        
        return structured

# Global validator instance
output_validator = OutputValidator()
```

## 2.3 Implementation Timeline

### **Week 2: Core Prompt Enhancement**
- **Days 8-9**: Implement `EnhancedPromptManager` with template system
- **Days 10-11**: Create enhanced prompts for all agents with examples
- **Days 12-13**: Implement output validation and schema enforcement
- **Day 14**: Integration testing and performance validation

### **Week 3: Advanced Features & Optimization**
- **Days 15-16**: Add A/B testing framework for prompt optimization
- **Days 17-18**: Implement personalization and context management
- **Days 19-20**: Performance tuning and cache optimization
- **Day 21**: Production deployment and monitoring

---

# ⚡ PHASE 3: CIRCUIT BREAKER RESILIENCE (Week 3-4)
*Priority: HIGH - Critical for production stability*

## 3.1 Advanced Circuit Breaker Implementation

```python
# NEW FILE: backend/src/resilience/circuit_breaker.py
from typing import Any, Callable, Dict, Optional, Union
import asyncio
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Fast-fail mode
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5                    # Failures before opening
    success_threshold: int = 3                    # Successes to close from half-open
    recovery_timeout: int = 60                    # Seconds before attempting recovery
    timeout: int = 10                            # Request timeout in seconds
    expected_exceptions: tuple = (Exception,)     # Exceptions to count as failures
    
    # Advanced features
    sliding_window_size: int = 100               # Size of metrics sliding window
    failure_rate_threshold: float = 0.5          # Failure rate (0.0-1.0) to trigger opening
    slow_call_threshold: int = 5                 # Seconds to consider a call "slow"
    slow_call_rate_threshold: float = 0.3        # Rate of slow calls to trigger opening
    minimum_requests: int = 10                   # Minimum requests before calculating rates

@dataclass
class CallResult:
    """Result of a circuit breaker call"""
    success: bool
    duration: float
    timestamp: float
    error: Optional[Exception] = None

class CircuitBreakerMetrics:
    """Advanced metrics collection for circuit breaker"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.call_history: deque = deque(maxlen=window_size)
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0
        self.avg_response_time = 0.0
        
    def record_call(self, result: CallResult):
        """Record a call result"""
        self.call_history.append(result)
        self.total_calls += 1
        
        if result.success:
            self.total_successes += 1
        else:
            self.total_failures += 1
            if isinstance(result.error, asyncio.TimeoutError):
                self.total_timeouts += 1
    
    def get_failure_rate(self) -> float:
        """Get current failure rate in sliding window"""
        if len(self.call_history) == 0:
            return 0.0
        
        failures = sum(1 for call in self.call_history if not call.success)
        return failures / len(self.call_history)
    
    def get_slow_call_rate(self, threshold: int) -> float:
        """Get rate of slow calls in sliding window"""
        if len(self.call_history) == 0:
            return 0.0
        
        slow_calls = sum(1 for call in self.call_history if call.duration > threshold)
        return slow_calls / len(self.call_history)
    
    def get_average_response_time(self) -> float:
        """Get average response time in sliding window"""
        if len(self.call_history) == 0:
            return 0.0
        
        durations = [call.duration for call in self.call_history]
        return statistics.mean(durations)
    
    def get_percentile_response_time(self, percentile: float) -> float:
        """Get percentile response time (e.g., 95th percentile)"""
        if len(self.call_history) == 0:
            return 0.0
        
        durations = sorted([call.duration for call in self.call_history])
        index = int(len(durations) * percentile / 100)
        return durations[min(index, len(durations) - 1)]

class AdvancedCircuitBreaker:
    """
    Production-ready circuit breaker with advanced features:
    - Sliding window failure rate calculation
    - Slow call detection
    - Gradual recovery
    - Comprehensive metrics
    - Health monitoring
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics(self.config.sliding_window_size)
        
        # State management
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state_changed_at = time.time()
        
        # Advanced features
        self.half_open_calls = 0
        self.max_half_open_calls = 3
        
        self.logger = logger.getChild(f"circuit_breaker.{name}")
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        # Limit concurrent calls in half-open state
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.max_half_open_calls:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is HALF_OPEN with max concurrent calls reached"
                )
            self.half_open_calls += 1
        
        # Execute the function with timeout and metrics
        start_time = time.time()
        try:
            # Apply timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Record successful call
            duration = time.time() - start_time
            call_result = CallResult(
                success=True,
                duration=duration,
                timestamp=start_time
            )
            self.metrics.record_call(call_result)
            self._on_success()
            
            return result
            
        except self.config.expected_exceptions as e:
            # Record failed call
            duration = time.time() - start_time
            call_result = CallResult(
                success=False,
                duration=duration,
                timestamp=start_time,
                error=e
            )
            self.metrics.record_call(call_result)
            self._on_failure(e)
            raise
        
        finally:
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls = max(0, self.half_open_calls - 1)
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success in closed state
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self, exception: Exception):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Single failure in half-open state transitions back to open
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            # Check if we should open based on failure count or rate
            should_open = False
            
            # Simple failure count check
            if self.failure_count >= self.config.failure_threshold:
                should_open = True
            
            # Advanced: failure rate check
            if (len(self.metrics.call_history) >= self.config.minimum_requests and
                self.metrics.get_failure_rate() >= self.config.failure_rate_threshold):
                should_open = True
            
            # Advanced: slow call rate check
            if (len(self.metrics.call_history) >= self.config.minimum_requests and
                self.metrics.get_slow_call_rate(self.config.slow_call_threshold) >= self.config.slow_call_rate_threshold):
                should_open = True
                
            if should_open:
                self._transition_to_open()
        
        self.logger.warning(
            f"Circuit breaker call failed",
            extra={
                "state": self.state.value,
                "failure_count": self.failure_count,
                "failure_rate": self.metrics.get_failure_rate(),
                "exception": str(exception)
            }
        )
    
    def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_changed_at = time.time()
        self.half_open_calls = 0
        
        self.logger.error(
            f"Circuit breaker transitioned from {old_state.value} to OPEN",
            extra={
                "failure_count": self.failure_count,
                "failure_rate": self.metrics.get_failure_rate(),
                "total_calls": self.metrics.total_calls
            }
        )
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = time.time()
        self.success_count = 0
        self.half_open_calls = 0
        
        self.logger.info(f"Circuit breaker transitioned from {old_state.value} to HALF_OPEN")
    
    def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        
        self.logger.info(f"Circuit breaker transitioned from {old_state.value} to CLOSED")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_rate": self.metrics.get_failure_rate(),
            "slow_call_rate": self.metrics.get_slow_call_rate(self.config.slow_call_threshold),
            "average_response_time": self.metrics.get_average_response_time(),
            "p95_response_time": self.metrics.get_percentile_response_time(95),
            "total_calls": self.metrics.total_calls,
            "calls_in_window": len(self.metrics.call_history),
            "last_failure_time": self.last_failure_time,
            "state_changed_at": self.state_changed_at,
            "time_in_current_state": time.time() - self.state_changed_at,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "timeout": self.config.timeout,
                "failure_rate_threshold": self.config.failure_rate_threshold
            }
        }
    
    def reset(self):
        """Manually reset circuit breaker to closed state"""
        self._transition_to_closed()
        self.logger.info("Circuit breaker manually reset to CLOSED state")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """Centralized management of circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self.default_configs: Dict[str, CircuitBreakerConfig] = {
            "aws_api": CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                timeout=10,
                failure_rate_threshold=0.4
            ),
            "llm_api": CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30,
                failure_rate_threshold=0.3
            ),
            "database": CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=15,
                timeout=5,
                failure_rate_threshold=0.5
            )
        }
    
    def get_circuit_breaker(self, name: str, service_type: str = None) -> AdvancedCircuitBreaker:
        """Get or create circuit breaker for service"""
        if name not in self.circuit_breakers:
            config = self.default_configs.get(service_type, CircuitBreakerConfig())
            self.circuit_breakers[name] = AdvancedCircuitBreaker(name, config)
        
        return self.circuit_breakers[name]
    
    def get_all_health_status(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers"""
        return {
            "total_circuit_breakers": len(self.circuit_breakers),
            "circuit_breakers": {
                name: cb.get_health_status() 
                for name, cb in self.circuit_breakers.items()
            },
            "summary": {
                "open_count": sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN),
                "half_open_count": sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.HALF_OPEN),
                "closed_count": sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.CLOSED)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_all(self):
        """Reset all circuit breakers to closed state"""
        for cb in self.circuit_breakers.values():
            cb.reset()

# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()
```

## 3.2 Integration with Existing Agents

```python
# ENHANCEMENT TO: backend/src/tools/aws_tools_enhanced.py
from src.resilience.circuit_breaker import circuit_breaker_manager, CircuitBreakerOpenException
import asyncio

class ResilientAWSCostTool(AWSCostExplorerTool):
    """AWS Cost tool enhanced with circuit breaker protection"""
    
    def __init__(self):
        super().__init__()
        self.circuit_breaker = circuit_breaker_manager.get_circuit_breaker(
            "aws_cost_explorer", 
            "aws_api"
        )
    
    async def get_cost_data(self, time_period: str = "30_days", **kwargs) -> str:
        """Get cost data with circuit breaker protection"""
        
        try:
            result = await self.circuit_breaker.call(
                self._fetch_cost_data_internal,
                time_period,
                **kwargs
            )
            return result
            
        except CircuitBreakerOpenException as e:
            # Return cached data or graceful degradation
            self.logger.warning(f"Circuit breaker open, using fallback: {e}")
            return await self._get_cached_or_fallback_data(time_period, **kwargs)
        
        except Exception as e:
            # Log error and return fallback
            self.logger.error(f"AWS API call failed: {e}")
            return await self._get_cached_or_fallback_data(time_period, **kwargs)
    
    async def _fetch_cost_data_internal(self, time_period: str, **kwargs) -> str:
        """Internal method that performs actual AWS API call"""
        # This would be the existing AWS API logic
        return await super()._run(time_period)
    
    async def _get_cached_or_fallback_data(self, time_period: str, **kwargs) -> str:
        """Return cached data or fallback response when API is unavailable"""
        
        # Try to get cached data first
        cached_data = await self._get_cached_data(time_period)
        if cached_data:
            return cached_data
        
        # Return graceful degradation response
        fallback_response = {
            "error": "AWS Cost Explorer temporarily unavailable",
            "status": "degraded_service",
            "message": "Using fallback data. Some information may be incomplete.",
            "fallback_data": {
                "total_cost": "unavailable",
                "period": time_period,
                "daily_costs": [],
                "top_services": [],
                "analysis_date": datetime.now().isoformat(),
                "data_source": "fallback"
            },
            "recommendations": [
                "Check AWS service status",
                "Retry request in a few minutes",
                "Review cached reports for historical data"
            ]
        }
        
        return json.dumps(fallback_response, indent=2)
```

Continue with comprehensive implementation plan covering Phase 4 (Monitoring) and detailed execution roadmap...

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze current codebase for safety vulnerabilities", "status": "completed", "activeForm": "Analyzing current codebase for safety vulnerabilities"}, {"content": "Design comprehensive safety guard architecture", "status": "completed", "activeForm": "Designing comprehensive safety guard architecture"}, {"content": "Create enhanced prompt engineering framework", "status": "completed", "activeForm": "Creating enhanced prompt engineering framework"}, {"content": "Implement circuit breaker resilience patterns", "status": "completed", "activeForm": "Implementing circuit breaker resilience patterns"}, {"content": "Design comprehensive monitoring and observability system", "status": "in_progress", "activeForm": "Designing comprehensive monitoring system"}, {"content": "Create detailed implementation roadmap with dependencies", "status": "pending", "activeForm": "Creating detailed implementation roadmap"}]