from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict

SYNTHESIS_TEMPLATE = """
You're an analysis assistant. The user is exploring the topic: "{topic}".

Below are relevant Reddit discussions:
---
{reddit_results}

Here are broader web discussions and current information:
---
{web_results}

And here is relevant academic research:
---
{academic_results}

Please provide a thoughtful, structured summary:
1. What are people saying about this issue on Reddit?
2. What broader context exists from web sources?
3. What does academic research reveal about this topic?
4. What gaps, needs, or opportunities remain?

Output format:
---
🧠 What people are saying on Reddit:
...

🌐 Broader web context:
...

📚 Academic research insights:
...

🚀 Gaps or opportunities:
...
"""

prompt = PromptTemplate.from_template(SYNTHESIS_TEMPLATE)

def llm_reasoner_tool(inputs: Dict[str, str]) -> str:
    """
    Synthesize insights from Reddit and product search results using GPT-4.
    """
    try:
        # Initialize LLM when function is called (after env vars are loaded)
        llm = ChatOpenAI(temperature=0.4, model="gpt-4o")
        
        topic = inputs.get("topic", "")
        reddit_results = inputs.get("reddit_results", "No Reddit data available")
        web_results = inputs.get("web_results", "No web data available")
        academic_results = inputs.get("academic_results", "No academic data available")
        
        formatted_prompt = prompt.format(
            topic=topic,
            reddit_results=reddit_results,
            web_results=web_results,
            academic_results=academic_results
        )
        
        response = llm.invoke(formatted_prompt)
        return response.content
    
    except Exception as e:
        return f"LLM synthesis error: {str(e)}" 