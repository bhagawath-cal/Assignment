"""
LangGraph agent for natural language queries against Neo4j.

This agent requires:
- LangChain dependencies installed
- Deepseek API key configured in .env file
"""
from typing import TypedDict, Annotated, Sequence
import operator
from app.config import settings

# Required imports - fail if not available
try:
    from langchain_core.messages import HumanMessage, AIMessage
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from app.agents.neo4j_tool import execute_neo4j_query
except (ImportError, TypeError, AttributeError) as e:
    raise ImportError(
        f"LangChain dependencies are required but not available: {e}\n"
        "Please install: pip install langchain langchain-openai langgraph langchain-community"
    )


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]


def create_agent():
    """
    Create a LangGraph agent with Neo4j query capabilities.
    
    Requires Deepseek API key to be configured in .env file.
    """
    # Check if Deepseek API key is configured
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        raise ValueError(
            "Deepseek API key is required but not configured.\n"
            "Please set OPENAI_API_KEY in your .env file."
        )
    
    # Initialize the LLM
    try:
        llm = ChatOpenAI(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            temperature=0,
            api_key=settings.openai_api_key,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Deepseek LLM: {e}\n"
            "Please check your OPENAI_API_KEY in .env file."
        )
    
    # Define tools
    tools = [execute_neo4j_query]
    tool_node = ToolNode(tools)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the agent node
    def agent_node(state: AgentState):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Define routing logic
    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, end
        return END
    
    # Build the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()




# Lazy agent creation - don't create at module load time
_agent_instance = None

def get_agent_instance():
    """Get or create the agent instance lazily."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_agent()
    return _agent_instance

# For backward compatibility, create agent on first access
# But wrap it so import doesn't fail
class LazyAgent:
    def __getattr__(self, name):
        return getattr(get_agent_instance(), name)
    def invoke(self, *args, **kwargs):
        return get_agent_instance().invoke(*args, **kwargs)

agent = LazyAgent()

