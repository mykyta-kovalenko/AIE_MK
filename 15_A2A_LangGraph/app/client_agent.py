"""A2A Client Agent using LangGraph to interact with the A2A server."""

import asyncio
import logging
from typing import Annotated, Any, Dict, List
from uuid import uuid4

import httpx
from langgraph.graph import StateGraph, add_messages
from langgraph.graph.message import AnyMessage
from langchain_core.messages import HumanMessage, AIMessage
from typing_extensions import TypedDict

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class ClientAgentState(TypedDict):
    """State schema for client agent graphs, storing conversation and A2A communication."""
    messages: Annotated[List[AnyMessage], add_messages]
    a2a_client: A2AClient | None
    server_base_url: str
    last_response: str | None
    server_response: Any
    agent_card: Any
    workflow_info: Any


class A2AClientAgent:
    """A LangGraph agent that acts as a client to the A2A server."""

    def __init__(self, server_base_url: str = "http://localhost:10000"):
        self.server_base_url = server_base_url
        self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph client agent graph."""
        graph = StateGraph(ClientAgentState)

        graph.add_node("initialize_client", self._initialize_a2a_client)
        graph.add_node("send_to_server", self._send_message_to_server)
        graph.add_node("process_response", self._process_server_response)

        graph.add_edge("initialize_client", "send_to_server")
        graph.add_edge("send_to_server", "process_response")
        graph.add_edge("process_response", "__end__")

        graph.set_entry_point("initialize_client")

        return graph.compile()

    async def _initialize_a2a_client(self, state: ClientAgentState) -> Dict[str, Any]:
        """Initialize the A2A client and fetch agent card."""
        try:
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=state["server_base_url"],
            )

            agent_card = await resolver.get_agent_card()
            
            a2a_client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=agent_card
            )

            return {"a2a_client": a2a_client, "agent_card": agent_card}

        except Exception as e:
            logger.error(f"Failed to initialize A2A client: {e}")
            return {"last_response": f"Error: Failed to connect to A2A server: {e}"}

    async def _send_message_to_server(self, state: ClientAgentState) -> Dict[str, Any]:
        """Send the user message to the A2A server."""
        a2a_client = state.get("a2a_client")
        if not a2a_client:
            return {"last_response": "Error: A2A client not initialized"}

        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            return {"last_response": "Error: No user message found"}

        latest_message = user_messages[-1]

        try:
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': latest_message.content}
                    ],
                    'message_id': uuid4().hex,
                },
            }

            request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**send_message_payload)
            )

            response = await a2a_client.send_message(request)

            return {"server_response": response}

        except Exception as e:
            logger.error(f"Failed to send message to A2A server: {e}")
            return {"last_response": f"Error: Failed to communicate with server: {e}"}

    async def _process_server_response(self, state: ClientAgentState) -> Dict[str, Any]:
        """Process the response from the A2A server."""
        server_response = state.get("server_response")
        if not server_response:
            return {"last_response": "Error: No server response received"}

        try:
            result = server_response.root.result
            
            # Try to extract content from different response formats
            response_content = (
                self._extract_from_artifacts(result) or 
                self._extract_from_status_message(result) or 
                self._extract_from_history(result) or
                f"No content found. Status: {getattr(result.status, 'state', 'unknown') if hasattr(result, 'status') else 'unknown'}"
            )

            # Extract workflow info from history
            workflow_info = self._extract_workflow_info(result)

            ai_message = AIMessage(content=response_content)
            return {
                "messages": [ai_message],
                "last_response": response_content,
                "workflow_info": workflow_info
            }

        except Exception as e:
            logger.error(f"Failed to process server response: {e}")
            error_msg = f"Error: Failed to process server response: {e}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "last_response": error_msg
            }
    
    def _extract_from_artifacts(self, result) -> str:
        """Extract content from completed task artifacts."""
        if not (hasattr(result, 'artifacts') and result.artifacts):
            return ""
        
        content = ""
        for artifact in result.artifacts:
            for part in artifact.parts:
                if hasattr(part.root, 'text'):
                    content += part.root.text
        return content
    
    def _extract_from_status_message(self, result) -> str:
        """Extract content from status messages (input_required, etc.)."""
        if not (hasattr(result, 'status') and result.status and hasattr(result.status, 'message')):
            return ""
        
        status_message = result.status.message
        if not hasattr(status_message, 'parts'):
            return ""
        
        content = ""
        for part in status_message.parts:
            text = getattr(part.root, 'text', None) or getattr(part, 'text', None)
            if text:
                content += text
        return content
    
    def _extract_from_history(self, result) -> str:
        """Extract content from conversation history as fallback."""
        if not (hasattr(result, 'history') and result.history):
            return ""
        
        # Get the last agent message from history
        for message in reversed(result.history):
            if hasattr(message, 'role') and message.role == 'agent' and hasattr(message, 'parts'):
                for part in message.parts:
                    if hasattr(part, 'text'):
                        return part.text
        return ""
    
    def _extract_workflow_info(self, result) -> Dict[str, Any]:
        """Extract simple workflow information from the response."""
        info = {
            "agent_interactions": 0,
            "status": "unknown"
        }
        
        # Get status
        if hasattr(result, 'status') and result.status:
            status_state = str(result.status.state) if hasattr(result.status, 'state') else "unknown"
            info["status"] = status_state.replace("TaskState.", "")  # Clean up the status
        
        # Count workflow steps from history 
        if hasattr(result, 'history') and result.history:
            search_count = 0
            process_count = 0
            
            for msg in result.history:
                if hasattr(msg, 'role') and hasattr(msg, 'parts'):
                    role_str = str(msg.role)
                    if 'agent' in role_str.lower():
                        for part in msg.parts:
                            # Access text through the root object
                            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                text = part.root.text
                                if text == 'Searching for information...':
                                    search_count += 1
                                elif text == 'Processing the results...':
                                    process_count += 1
            
            if search_count > 0 or process_count > 0:
                info["agent_interactions"] = f"{search_count} searches, {process_count} processing steps"
            else:
                info["agent_interactions"] = "direct response"
        
        return info
    

    async def query(self, user_message: str) -> str:
        """Send a query to the A2A server and return the response."""
        initial_state = ClientAgentState(
            messages=[HumanMessage(content=user_message)],
            a2a_client=None,
            server_base_url=self.server_base_url,
            last_response=None,
            server_response=None,
            agent_card=None,
            workflow_info=None
        )

        try:
            final_state = await self.graph.ainvoke(initial_state)
            workflow_info = final_state.get("workflow_info")
            return final_state.get("last_response", "No response received"), workflow_info
        except Exception as e:
            logger.error(f"Error running client agent: {e}")
            return f"Error: {e}", None

    async def close(self):
        """Clean up resources."""
        await self.httpx_client.aclose()


def print_header(title: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n🔸 {title}")
    print("─" * 50)

def print_agent_card_info(agent_card):
    """Print formatted agent card information."""
    print_section("A2A Server Agent Card Discovery")
    print(f"📋 Agent Name: {agent_card.name}")
    print(f"📝 Description: {agent_card.description}")
    print(f"🌐 URL: {agent_card.url}")
    print(f"📦 Version: {agent_card.version}")
    print(f"🔄 Protocol: {getattr(agent_card, 'preferred_transport', 'JSONRPC')} v{getattr(agent_card, 'protocol_version', '0.3.0')}")
    
    print(f"\n🛠️  Available Skills ({len(agent_card.skills)}):")
    for skill in agent_card.skills:
        print(f"   • {skill.name}: {skill.description}")
        print(f"     Tags: {', '.join(skill.tags)}")
        if skill.examples:
            print(f"     Example: \"{skill.examples[0]}\"")

def format_response(response_text: str) -> str:
    """Format the response for better readability."""
    if len(response_text) > 500:
        return response_text[:500] + "..."
    return response_text

async def demo_client_agent():
    """Demonstrate the A2A client agent with detailed output."""
    print_header("🤖 A2A Protocol Client Agent Demonstration")
    
    print("\n🎯 OBJECTIVE: Demonstrate LangGraph agent communicating with A2A server")
    print("   • Client Agent: LangGraph-based A2A protocol client")
    print("   • Server Agent: Multi-tool agent with RAG, ArXiv, and Tavily search")
    print("   • Protocol: A2A (Agent-to-Agent) communication standard")
    print("   • Data Source: Design_Patterns.pdf in data/ directory")

    client_agent = A2AClientAgent()

    try:
        # First, let's get the agent card to show what we discovered
        print_section("Initializing A2A Connection")
        print("🔄 Connecting to A2A server at http://localhost:10000")
        
        # Run a simple query to get the agent card info
        initial_state = ClientAgentState(
            messages=[HumanMessage(content="test")],
            a2a_client=None,
            server_base_url=client_agent.server_base_url,
            last_response=None,
            server_response=None,
            agent_card=None
        )
        
        # Just run the initialization to get agent card
        init_result = await client_agent._initialize_a2a_client(initial_state)
        if "agent_card" in init_result:
            print("✅ Successfully connected to A2A server!")
            print_agent_card_info(init_result["agent_card"])

        # Test queries that demonstrate different capabilities
        test_scenarios = [
            {
                "title": "Design Pattern Knowledge",
                "query": "What is the Singleton design pattern and how is it implemented?",
                "expected": "Agent chooses best information source for comprehensive answer"
            },
            {
                "title": "Behavioral Pattern Explanation", 
                "query": "Explain the Observer design pattern from the documents",
                "expected": "Agent decides between local documents or academic sources"
            },
            {
                "title": "Current Technology Information",
                "query": "What is LangGraph and how is it used for building AI agents?",
                "expected": "Agent searches for current information on LangGraph"
            }
        ]

        print_header("🚀 A2A Communication Tests", "=")

        for i, scenario in enumerate(test_scenarios, 1):
            print_section(f"Test {i}: {scenario['title']}")
            print(f"📤 Query: \"{scenario['query']}\"")
            print(f"🤖 Expected: {scenario['expected']}")
            print("\n🔄 Sending A2A message...")

            start_time = asyncio.get_event_loop().time()
            response, workflow_info = await client_agent.query(scenario["query"])
            end_time = asyncio.get_event_loop().time()

            print(f"⏱️  Response Time: {end_time - start_time:.2f}s")
            
            # Show minimal workflow info  
            if workflow_info:
                status = workflow_info.get("status", "unknown")
                interactions = workflow_info.get("agent_interactions", "unknown")
                print(f"🤖 Workflow: {interactions} • Status: {status}")
            
            if response.startswith("Error:"):
                print(f"⚠️  Result: {response}")
            else:
                print("✅ Server Response:")
                print("┌" + "─" * 68 + "┐")
                lines = response.split('\n')
                for line in lines[:15]:  # Limit output
                    print(f"│ {line[:66]:<66} │")
                if len(lines) > 15:
                    print(f"│ ... (response continues for {len(lines) - 15} more lines) │")
                print("└" + "─" * 68 + "┘")

            print()
            await asyncio.sleep(1)


    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client_agent.close()
        print_section("Demo Complete")
        print("🔌 A2A client connection closed")


if __name__ == "__main__":
    asyncio.run(demo_client_agent())