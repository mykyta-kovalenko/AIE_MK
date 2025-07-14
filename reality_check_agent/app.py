#!/usr/bin/env python3

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agent_graph import create_reality_check_graph
from agent_state import RealityCheckState

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Reality Check Bot",
    description="Validate emotionally charged topics with Reddit, web, and academic research",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request/Response models
class TopicRequest(BaseModel):
    topic: str

class AnalysisResponse(BaseModel):
    topic: str
    analysis: str
    success: bool
    error: str = None

# Initialize the agent (do this once at startup)
agent = None

def get_agent():
    """Get or create the agent instance."""
    global agent
    if agent is None:
        try:
            # Verify API keys
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_API_KEY not found in environment")
            
            if not os.getenv("TAVILY_API_KEY"):
                raise RuntimeError("TAVILY_API_KEY not found in environment")
            
            # Enable LangSmith tracing if available
            if os.getenv("LANGCHAIN_API_KEY"):
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_PROJECT"] = "reality-check-bot"
            
            # Create the agent
            agent = create_reality_check_graph()
            print("✅ Reality Check Bot agent initialized")
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            raise
    return agent

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        openai_key = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
        tavily_key = "✅" if os.getenv("TAVILY_API_KEY") else "❌"
        agent_status = "✅" if agent is not None else "❌"
        
        return {
            "status": "healthy",
            "openai_key": openai_key,
            "tavily_key": tavily_key,
            "agent_ready": agent_status,
            "python_version": os.sys.version
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_topic(request: TopicRequest):
    """Analyze a topic using the Reality Check Bot."""
    
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        # Get agent instance (lazy initialization)
        current_agent = get_agent()
        # Initialize state
        initial_state: RealityCheckState = {
            "topic": request.topic.strip(),
            "reddit_results": None,
            "web_results": None,
            "academic_results": None,
            "final_analysis": None,
            "current_step": "start"
        }
        
        # Run the agent in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            final_state = await loop.run_in_executor(
                executor, 
                current_agent.invoke, 
                initial_state
            )
        
        return AnalysisResponse(
            topic=request.topic,
            analysis=final_state.get("final_analysis", "No analysis generated"),
            success=True
        )
        
    except Exception as e:
        return AnalysisResponse(
            topic=request.topic,
            analysis="",
            success=False,
            error=str(e)
        )

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging."""
    try:
        from tools.reddit_search import reddit_search_tool
        from tools.tavily_search import tavily_search_tool
        from tools.arxiv_search import arxiv_search_tool
        
        return {
            "status": "ok",
            "imports": "✅ All tools imported successfully",
            "env_vars": {
                "OPENAI_API_KEY": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
                "TAVILY_API_KEY": "✅" if os.getenv("TAVILY_API_KEY") else "❌"
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/docs")
async def get_api_docs():
    """Get API documentation."""
    return {
        "endpoints": {
            "POST /analyze": "Analyze a topic",
            "GET /health": "Health check",
            "GET /test": "Test endpoint for debugging",
            "GET /": "Frontend interface"
        },
        "example_request": {
            "topic": "impostor syndrome in software engineering"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 