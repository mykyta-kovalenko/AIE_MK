#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from agent_graph import create_reality_check_graph
from agent_state import RealityCheckState

# Load environment variables
load_dotenv()

def main():
    """Main execution function for the Reality Check Bot."""
    
    # Verify API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ TAVILY_API_KEY not found in environment")
        print("   Required for Reddit and web search functionality")
        return
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️ LANGCHAIN_API_KEY not found - LangSmith tracing disabled")
    else:
        # Enable LangSmith tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "reality-check-bot"
        print("✅ LangSmith tracing enabled")
    
    # Create the agent graph
    agent = create_reality_check_graph()
    
    print("\n🧠 Reality Check Bot - Validate Your Topic")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            topic = input("\nEnter a topic to research (or 'quit' to exit): ").strip()
            
            if topic.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not topic:
                print("❌ Please enter a valid topic")
                continue
            
            print(f"\n🚀 Starting research on: '{topic}'")
            print("-" * 40)
            
            # Initialize state
            initial_state: RealityCheckState = {
                "topic": topic,
                "reddit_results": None,
                "web_results": None,
                "academic_results": None,
                "final_analysis": None,
                "current_step": "start"
            }
            
            # Run the agent
            final_state = agent.invoke(initial_state)
            
            # Display results
            print("\n" + "=" * 60)
            print("📊 REALITY CHECK RESULTS")
            print("=" * 60)
            print(final_state.get("final_analysis", "No analysis generated"))
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 