"""
Chat endpoint with LangGraph agent for Neo4j queries.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

# Lazy import to avoid issues if LangChain has compatibility problems
_agent_cache = None
_AgentState_cache = None
_HumanMessage_cache = None
_AIMessage_cache = None

def get_agent():
    """Lazy import of the agent - requires LangChain and Deepseek API key."""
    global _agent_cache, _AgentState_cache, _HumanMessage_cache, _AIMessage_cache
    
    if _agent_cache is not None:
        return _agent_cache, _AgentState_cache, _HumanMessage_cache, _AIMessage_cache
    
    try:
        # Import the agent getter function and required LangChain components
        from app.agents.chat_agent import get_agent_instance, AgentState
        from langchain_core.messages import HumanMessage, AIMessage
        
        _agent_cache = get_agent_instance()
        _AgentState_cache = AgentState
        _HumanMessage_cache = HumanMessage
        _AIMessage_cache = AIMessage
        
        return _agent_cache, _AgentState_cache, _HumanMessage_cache, _AIMessage_cache
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangChain dependencies are required but not available: {str(e)}\n"
                  "Please install: pip install langchain langchain-openai langgraph langchain-community"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize chat agent: {str(e)}"
        )


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    response: str
    query_executed: bool = False


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that uses LangGraph agent to answer questions about the movie database.
    
    The agent can execute Neo4j Cypher queries to answer questions like:
    - "Show related items with high enrichment scores"
    - "List entities connected to X with property Y"
    - "What movies did Leonardo DiCaprio star in?"
    - "Find movies with high enrichment scores"
    """
    try:
        agent, AgentState, HumanMessage, AIMessage = get_agent()
        
        # Convert conversation history to LangChain messages
        messages = []
        for msg in request.conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add the current user message
        messages.append(HumanMessage(content=request.message))
        
        # Create initial state
        initial_state: AgentState = {"messages": messages}
        
        # Invoke the agent
        result = agent.invoke(initial_state)
        
        # Get the last AI message
        last_message = result["messages"][-1]
        response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Check if a query was executed (simple heuristic: if response contains query results)
        query_executed = "query" in response_text.lower() or "cypher" in response_text.lower() or "{" in response_text
        
        return ChatResponse(
            response=response_text,
            query_executed=query_executed
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@router.get("/chat/examples")
async def get_chat_examples():
    """Get example queries for the chat endpoint."""
    return {
        "examples": [
            "Show movies with high enrichment scores",
            "List all actors who worked with Christopher Nolan",
            "Find movies connected to Leonardo DiCaprio",
            "Show related items with high enrichment scores",
            "What genres does Inception belong to?",
            "List entities connected to Drama genre",
        ]
    }

