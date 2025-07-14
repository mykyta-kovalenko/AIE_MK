from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Dict, List
import time

def reddit_search_tool(topic: str) -> str:
    """
    Search Reddit for discussions about the given topic.
    Uses multiple search strategies to find relevant content.
    """
    try:
        # Initialize Tavily search tool
        search = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_answer=False,
            include_raw_content=True,
            include_images=False
        )
        
        # Try multiple search strategies for better coverage
        search_queries = [
            f"site:reddit.com {topic} experience discussion",
            f"site:reddit.com {topic} help advice support",
            f"site:reddit.com \"{topic}\" personal story",
            f"reddit {topic} community discussion"
        ]
        
        all_results = []
        for query in search_queries:
            try:
                results = search.run(query)
                if results:
                    all_results.extend(results)
                time.sleep(0.5)  # Be respectful to API
            except Exception as e:
                continue
        
        if not all_results:
            return f"No Reddit discussions found for '{topic}'"
        
        # Remove duplicates and format results
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if isinstance(result, dict):
                url = result.get('url', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
        
        # Format results to look like Reddit posts
        formatted_results = []
        for result in unique_results[:8]:  # Limit to best 8 results
            if isinstance(result, dict):
                title = result.get('title', 'No title')
                content = result.get('content', '')[:300]  # More content
                url = result.get('url', '')
                
                # Extract subreddit from URL if possible
                subreddit = "unknown"
                if "reddit.com/r/" in url:
                    try:
                        subreddit = url.split("/r/")[1].split("/")[0]
                    except:
                        pass
                elif "reddit.com" in url:
                    subreddit = "reddit"
                
                # Clean up content for better readability
                if content:
                    # Remove common Reddit formatting issues
                    content = content.replace('\\n', ' ').replace('  ', ' ').strip()
                    formatted_results.append(f"[r/{subreddit}] {title}\n{content}...\nSource: {url}")
                else:
                    formatted_results.append(f"[r/{subreddit}] {title}\nSource: {url}")
        
        return "\n\n".join(formatted_results) if formatted_results else f"No relevant Reddit discussions found for '{topic}'"
    
    except Exception as e:
        return f"Reddit search error: {str(e)}" 