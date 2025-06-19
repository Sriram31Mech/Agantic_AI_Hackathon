"""
Agent with Search Capabilities
This agent uses LangChain and LangGraph to create an intelligent agent that can search the web
and maintain conversational memory.
"""

import os
import getpass
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools.tavily_tools import create_search_tool, get_search_tools

# Load environment variables
load_dotenv()

# Setup environment variables
def setup_environment():
    """Setup required environment variables"""
    # LangSmith tracing
    os.environ["LANGSMITH_TRACING"] = "true"
    if not os.environ.get("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter LangSmith API key: ")
    
    # Tavily API key
    if not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter Tavily API key: ")
    
    # Google API key for Gemini
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google Gemini API key: ")

def create_agent():
    """Create and configure the agent with tools and memory"""
    # Initialize memory for conversational context
    memory = MemorySaver()
    
    # Initialize the language model
    model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    
    # Create search tools
    search_tool = create_search_tool(max_results=2)
    tools = [search_tool]
    
    # Create the agent with memory
    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    
    return agent_executor

def run_agent_interactive(agent_executor):
    """Run the agent in interactive mode"""
    config = {"configurable": {"thread_id": "session_001"}}
    
    print("🤖 Agent initialized! You can now ask questions.")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break
            
            if not user_input.strip():
                continue
            
            # Create input message
            input_message = {"role": "user", "content": user_input}
            
            print("\n🤖 Agent is thinking...\n")
            
            # Stream the agent response
            for step in agent_executor.stream(
                {"messages": [input_message]}, config, stream_mode="values"
            ):
                last_message = step["messages"][-1]
                if hasattr(last_message, 'pretty_print'):
                    last_message.pretty_print()
                else:
                    print(f"Assistant: {last_message.content}")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.\n")

def run_single_query(agent_executor, query: str):
    """Run a single query through the agent"""
    config = {"configurable": {"thread_id": "single_query"}}
    
    input_message = {"role": "user", "content": query}
    
    print(f"Query: {query}")
    print("🤖 Agent response:\n")
    
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        last_message = step["messages"][-1]
        if hasattr(last_message, 'pretty_print'):
            last_message.pretty_print()
        else:
            print(f"Assistant: {last_message.content}")

def main():
    """Main function to run the agent"""
    print("🚀 Initializing Agent with Search Capabilities...")
    
    # Setup environment
    setup_environment()
    
    # Create agent
    agent_executor = create_agent()
    
    print("✅ Agent created successfully!")
    
    # Choose mode
    print("\nChoose mode:")
    print("1. Interactive mode (chat)")
    print("2. Single query mode")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "2":
        query = input("Enter your query: ")
        run_single_query(agent_executor, query)
    else:
        run_agent_interactive(agent_executor)

if __name__ == "__main__":
    main()
