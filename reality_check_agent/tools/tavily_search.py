from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Dict, List
import os

def tavily_search_tool(topic: str) -> str:
    """
    Search the web using Tavily API for current discussions and information.
    """
    try:
        # Initialize Tavily search tool
        search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            include_images=False
        )
        
        # Search for general discussions and opinions
        query = f"{topic} discussions opinions experiences problems"
        results = search.run(query)
        
        if not results:
            return f"No web results found for '{topic}'"
        
        # Format results
        formatted_results = []
        for result in results:
            if isinstance(result, dict):
                title = result.get('title', 'No title')
                content = result.get('content', '')[:300]  # Limit content
                url = result.get('url', '')
                
                formatted_results.append(f"Title: {title}\nContent: {content}...\nSource: {url}")
            else:
                formatted_results.append(str(result)[:300])
        
        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"Tavily search error: {str(e)}" 