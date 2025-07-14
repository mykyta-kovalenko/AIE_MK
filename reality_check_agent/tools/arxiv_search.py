from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from typing import Dict

def arxiv_search_tool(topic: str) -> str:
    """
    Search Arxiv for academic research related to the topic.
    """
    try:
        # Initialize Arxiv search tool
        arxiv_wrapper = ArxivAPIWrapper(
            top_k_results=3,
            doc_content_chars_max=500
        )
        arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)
        
        # Try multiple search strategies
        search_queries = [
            f"{topic} psychology mental health wellbeing research",
            f"{topic} psychology research",
            f"{topic} social psychology",
            topic
        ]
        
        for query in search_queries:
            results = arxiv_tool.run(query)
            if results and "No good Arxiv Result was found" not in results:
                return results
        
        return f"No academic research found for '{topic}'"
        
        return results
    
    except Exception as e:
        return f"Arxiv search error: {str(e)}" 