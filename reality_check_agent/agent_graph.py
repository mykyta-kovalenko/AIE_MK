from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from typing import Dict, Any

from agent_state import RealityCheckState
from tools.reddit_search import reddit_search_tool
from tools.tavily_search import tavily_search_tool
from tools.arxiv_search import arxiv_search_tool  
from tools.llm_reasoner import llm_reasoner_tool

def reddit_search_node(state: RealityCheckState) -> RealityCheckState:
    """Search Reddit for discussions about the topic."""
    print(f"🔍 Searching Reddit for: {state['topic']}")
    
    reddit_results = reddit_search_tool(state['topic'])
    
    return {
        **state,
        "reddit_results": reddit_results,
        "current_step": "reddit_complete"
    }

def web_search_node(state: RealityCheckState) -> RealityCheckState:
    """Search the web using Tavily for current discussions."""
    print(f"🌐 Searching web for: {state['topic']}")
    
    web_results = tavily_search_tool(state['topic'])
    
    return {
        **state,
        "web_results": web_results,
        "current_step": "web_complete"
    }

def academic_search_node(state: RealityCheckState) -> RealityCheckState:
    """Search Arxiv for academic research."""
    print(f"📚 Searching academic research for: {state['topic']}")
    
    academic_results = arxiv_search_tool(state['topic'])
    
    return {
        **state,
        "academic_results": academic_results,
        "current_step": "academic_complete"
    }

def synthesis_node(state: RealityCheckState) -> RealityCheckState:
    """Synthesize insights using LLM."""
    print(f"🧠 Synthesizing insights for: {state['topic']}")
    
    inputs = {
        "topic": state['topic'],
        "reddit_results": state.get('reddit_results', ''),
        "web_results": state.get('web_results', ''),
        "academic_results": state.get('academic_results', '')
    }
    
    final_analysis = llm_reasoner_tool(inputs)
    
    return {
        **state,
        "final_analysis": final_analysis,
        "current_step": "complete"
    }

def should_continue(state: RealityCheckState) -> str:
    """Determine the next step in the workflow."""
    current_step = state.get("current_step", "start")
    
    if current_step == "start":
        return "reddit_search"
    elif current_step == "reddit_complete":
        return "web_search"
    elif current_step == "web_complete":
        return "academic_search"
    elif current_step == "academic_complete":
        return "synthesis"
    else:
        return END

def create_reality_check_graph() -> StateGraph:
    """Create and configure the LangGraph workflow."""
    
    # Initialize the graph
    workflow = StateGraph(RealityCheckState)
    
    # Add nodes
    workflow.add_node("reddit_search", reddit_search_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("academic_search", academic_search_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry point
    workflow.set_entry_point("reddit_search")
    
    # Add edges
    workflow.add_edge("reddit_search", "web_search")
    workflow.add_edge("web_search", "academic_search")
    workflow.add_edge("academic_search", "synthesis") 
    workflow.add_edge("synthesis", END)
    
    # Compile the graph
    return workflow.compile() 