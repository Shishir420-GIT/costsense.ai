from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from ..ai import get_ollama_client, SystemPrompts
from ..agents import get_orchestrator
from ..cache import get_cache_instance, Cache
from ..middleware import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = datetime.utcnow()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    intent: Optional[str] = None
    tool_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    cache: Cache = Depends(get_cache_instance),
):
    """
    Chat endpoint with intent detection and tool routing

    Supports:
    - Natural language cost queries
    - Analysis requests
    - Optimization recommendations
    - General questions
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())

    # Load conversation history
    history = await cache.get_session(session_id) or {"messages": []}
    messages = history.get("messages", [])

    # Add user message to history
    messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        # Step 1: Detect intent
        ollama_client = await get_ollama_client()

        intent_prompt = f"""User message: "{request.message}"

Classify this message and extract relevant information."""

        intent_result = await ollama_client.generate_json(
            prompt=intent_prompt,
            system_prompt=SystemPrompts.INTENT_DETECTION,
            temperature=0.1,
        )

        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.5)
        entities = intent_result.get("entities", {})

        logger.info(
            "Intent detected",
            intent=intent,
            confidence=confidence,
            session_id=session_id,
        )

        # Step 2: Route to appropriate handler
        response_text = ""
        tool_used = None
        response_data = None

        if intent == "cost_query" and confidence > 0.6:
            response_text, response_data = await handle_cost_query(request, entities)
            tool_used = "cost_query"

        elif intent == "cost_analysis" and confidence > 0.6:
            response_text, response_data = await handle_analysis_request(request, entities)
            tool_used = "analysis"

        elif intent == "optimization" and confidence > 0.6:
            response_text, response_data = await handle_optimization_request(request, entities)
            tool_used = "optimization"

        elif intent == "ticket_creation" and confidence > 0.6:
            response_text, response_data = await handle_ticket_creation(request, entities)
            tool_used = "ticket_creation"

        else:
            # General response
            response_text = await handle_general_query(request, messages, ollama_client)
            tool_used = "general"

        # Add assistant response to history
        messages.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "intent": intent,
            "tool_used": tool_used,
        })

        # Save conversation history (last 20 messages)
        history["messages"] = messages[-20:]
        history["last_updated"] = datetime.utcnow().isoformat()
        await cache.set_session(session_id, history, ttl=3600)

        return ChatResponse(
            message=response_text,
            session_id=session_id,
            intent=intent,
            tool_used=tool_used,
            data=response_data,
        )

    except Exception as e:
        logger.error("Chat error", error=str(e), session_id=session_id)

        error_message = "I apologize, but I encountered an error processing your request. Please try rephrasing your question or contact support."

        messages.append({
            "role": "assistant",
            "content": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        })

        history["messages"] = messages[-20:]
        await cache.set_session(session_id, history, ttl=3600)

        return ChatResponse(
            message=error_message,
            session_id=session_id,
        )


async def handle_cost_query(request: ChatRequest, entities: Dict) -> tuple[str, Dict]:
    """Handle cost-related queries"""
    # In a real implementation, query the database based on entities
    # For now, return a helpful response

    days = entities.get("days", 30)
    provider = entities.get("provider", "all")

    response = f"""I can help you analyze your cloud costs. Based on your question, I understand you're interested in costs for the past {days} days across {provider} provider(s).

To get the exact data, use the API endpoint:
GET /api/costs/summary?days={days}

Or I can provide a more detailed analysis if you ask me to "analyze my costs" or "find optimization opportunities"."""

    data = {
        "suggested_endpoint": f"/api/costs/summary?days={days}",
        "parameters": {"days": days, "provider": provider},
    }

    return response, data


async def handle_analysis_request(request: ChatRequest, entities: Dict) -> tuple[str, Dict]:
    """Handle analysis requests using agents"""
    response = """I'll analyze your cloud costs using my AI agents. This will take a moment...

**Analysis Pipeline:**
1. 🔍 Cost Analysis Agent - Analyzing spending patterns
2. 💡 Optimization Agent - Identifying savings opportunities
3. 📊 Aggregating results

To run the full analysis, use:
POST /api/analysis/run

Or create an investigation:
POST /api/investigations/

Would you like me to explain any specific cost patterns or anomalies you've noticed?"""

    data = {
        "suggested_action": "create_investigation",
        "endpoints": {
            "analysis": "/api/analysis/run",
            "investigation": "/api/investigations/",
        },
    }

    return response, data


async def handle_optimization_request(request: ChatRequest, entities: Dict) -> tuple[str, Dict]:
    """Handle optimization requests"""
    response = """I can help you find cost optimization opportunities!

**What I'll analyze:**
- Underutilized resources
- Over-provisioned services
- Idle resources
- Reserved instance opportunities
- Rightsizing recommendations

**Next steps:**
1. Run a full optimization analysis
2. Review recommendations
3. Create ServiceNow tickets for approved actions

To get started:
POST /api/investigations/ with optimization focus

Would you like me to explain any specific optimization strategies?"""

    data = {
        "suggested_action": "run_optimization",
        "optimization_types": [
            "underutilized_resources",
            "rightsizing",
            "reserved_instances",
            "idle_resources",
        ],
    }

    return response, data


async def handle_ticket_creation(request: ChatRequest, entities: Dict) -> tuple[str, Dict]:
    """Handle ticket creation requests"""
    response = """I can help you create a ServiceNow ticket for cost optimization actions.

**Ticket Creation Process:**
1. Draft the ticket with details
2. Review and approve
3. Submit to ServiceNow

To create a ticket:
POST /api/tickets/ with ticket details

Then approve it:
POST /api/tickets/{id}/approve

All tickets require human approval before being sent to ServiceNow. This ensures you have full control over what actions are taken.

What would you like the ticket to address?"""

    data = {
        "suggested_action": "create_ticket",
        "endpoints": {
            "create": "/api/tickets/",
            "approve": "/api/tickets/{id}/approve",
        },
        "requires_approval": True,
    }

    return response, data


async def handle_general_query(
    request: ChatRequest,
    messages: List[Dict],
    ollama_client
) -> str:
    """Handle general questions with context"""
    # Build context from recent messages
    context = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in messages[-5:]  # Last 5 messages
    ])

    prompt = f"""Conversation history:
{context}

Current question: {request.message}

Provide a helpful, friendly response about cloud cost management. If the question is about capabilities, explain what you can do with CostSense AI."""

    system_prompt = """You are a helpful cloud cost management assistant. You help users:
- Understand their cloud costs
- Find optimization opportunities
- Create tickets for cost-saving actions
- Explain cost patterns and anomalies

Be friendly, concise, and actionable. Always guide users toward specific features or endpoints they can use."""

    response = await ollama_client.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
    )

    return response


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    cache: Cache = Depends(get_cache_instance),
):
    """Get chat history for a session"""
    history = await cache.get_session(session_id)

    if not history:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": history.get("messages", []),
        "last_updated": history.get("last_updated"),
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    cache: Cache = Depends(get_cache_instance),
):
    """Clear chat history for a session"""
    await cache.delete_session(session_id)

    return {"message": "Chat history cleared", "session_id": session_id}
