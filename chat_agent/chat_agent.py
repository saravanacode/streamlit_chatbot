import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from chat_agent.tools import ToolsProvider
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from chat_agent.tools import PromptProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI
apiKey = os.environ.get("OPENAI_API_KEY")
if not apiKey:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

llm = init_chat_model("openai:gpt-4.1")

# Set up tools
tools = ToolsProvider.get_tools()
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

class State(TypedDict):
    """State type for the conversation graph."""
    messages: Annotated[list, add_messages]
   
def agent(state: State):
    """
    Agent function that processes the conversation state.
   
    Args:
        state (State): Current conversation state
       
    Returns:
        dict: Updated messages
    """
    try:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        print(f"Error in agent: {str(e)}")
        return {"messages": [{"role": "assistant", "content": "I encountered an error. Could you please rephrase your request?"}]}

# Build the conversation graph
graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", tools_condition, "tools")
graph_builder.add_edge("tools", "agent")
graph = graph_builder.compile()

def stream_graph_updates(query: str, conversation_history: list = None):
    """
    Stream updates from the conversation graph.
   
    Args:
        query (str): New message to process
        conversation_history (list): Previous conversation messages (optional)
       
    Returns:
        str: Last response from the assistant
    """
    last_response = None
    
    # Add system prompt
    system_prompt = PromptProvider.get_agent_system_prompt(query)
    formatted_messages = [system_prompt]
   
    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = "assistant" if msg.get("sender") == "system" else "user"
                formatted_messages.append({
                    "role": role,
                    "content": msg.get("message", "")
                })
   
    # Add the new message
    formatted_messages.append({
        "role": "user",
        "content": query
    })
   
    # Process the conversation through the graph
    try:
        for event in graph.stream({"messages": formatted_messages}):
            for value in event.values():
                last_response = value["messages"][-1].content
                print("Assistant:", last_response)
    except Exception as e:
        print(f"Error in stream_graph_updates: {str(e)}")
        last_response = "I apologize, but I encountered an error processing your message. Could you please rephrase your question?"

    return last_response

def get_tools():
    """Get all available tools."""
    return [
        ToolsProvider.weatherapi_get,
        ToolsProvider.retrive_from_qdrant,
    ]