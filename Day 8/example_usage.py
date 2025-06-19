"""
Example Usage: Building an Agent with Search Capabilities
This script demonstrates the exact methodology described in the task.
"""

import os
import getpass
from dotenv import load_dotenv

# Import relevant functionality
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

def setup_environment():
    """Setup environment variables as shown in the methodology"""
    load_dotenv()
    
    # LangSmith setup
    os.environ["LANGSMITH_TRACING"] = "true"
    if not os.environ.get("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter LangSmith API key: ")
    
    # Tavily setup
    if not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter Tavily API key: ")
    
    # Google Gemini setup
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google Gemini API key: ")

def demonstrate_methodology():
    """Demonstrate the exact methodology from the task"""
    
    print("🚀 Building Agent with Search Capabilities")
    print("=" * 50)
    
    # Step 1: Setup environment
    print("\n1️⃣ Setting up environment...")
    setup_environment()
    
    # Step 2: Create the agent (following the methodology exactly)
    print("\n2️⃣ Creating the agent...")
    
    # Create memory
    memory = MemorySaver()
    
    # Initialize model
    model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    
    # Create search tool
    search = TavilySearch(max_results=2)
    tools = [search]
    
    # Create the agent
    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    
    print("✅ Agent created successfully!")
    
    # Step 3: Use the agent
    print("\n3️⃣ Using the agent...")
    config = {"configurable": {"thread_id": "example_123"}}
    
    # Example 1: Basic conversation (no tool needed)
    print("\n📝 Example 1: Basic conversation")
    print("-" * 30)
    
    input_message = {
        "role": "user",
        "content": "Hi, I'm Bob and I live in SF.",
    }
    
    print("User:", input_message["content"])
    print("\nAgent response:")
    
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
    
    # Example 2: Query requiring search
    print("\n📝 Example 2: Query requiring search")
    print("-" * 30)
    
    input_message = {
        "role": "user",
        "content": "What's the weather where I live?",
    }
    
    print("User:", input_message["content"])
    print("\nAgent response:")
    
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

def demonstrate_tool_definition():
    """Demonstrate tool definition as shown in the methodology"""
    
    print("\n🔧 Demonstrating Tool Definition")
    print("=" * 40)
    
    # Define tools
    search = TavilySearch(max_results=2)
    search_results = search.invoke("What is the weather in SF")
    print("Search results preview:")
    print(f"Query: {search_results['query']}")
    print(f"Results count: {len(search_results['results'])}")
    print(f"Response time: {search_results['response_time']}s")
    
    # Create tools list
    tools = [search]
    print(f"✅ Created {len(tools)} tool(s)")

def demonstrate_model_with_tools():
    """Demonstrate model with tool binding"""
    
    print("\n🤖 Demonstrating Model with Tools")
    print("=" * 40)
    
    # Initialize model
    model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    
    # Create search tool
    search = TavilySearch(max_results=2)
    tools = [search]
    
    # Bind tools to model
    model_with_tools = model.bind_tools(tools)
    
    # Test normal message
    print("\n📝 Test 1: Normal message (no tool needed)")
    query = "Hi!"
    response = model_with_tools.invoke([{"role": "user", "content": query}])
    
    print(f"Query: {query}")
    print(f"Message content: {response.text()}")
    print(f"Tool calls: {response.tool_calls}")
    
    # Test message requiring tool
    print("\n📝 Test 2: Message requiring tool")
    query = "Search for the weather in SF"
    response = model_with_tools.invoke([{"role": "user", "content": query}])
    
    print(f"Query: {query}")
    print(f"Message content: {response.text()}")
    print(f"Tool calls: {response.tool_calls}")

def main():
    """Main function to run all demonstrations"""
    
    print("🎯 Agent Methodology Demonstration")
    print("This script demonstrates the exact methodology from the task.")
    print("=" * 60)
    
    try:
        # Demonstrate each part of the methodology
        demonstrate_tool_definition()
        demonstrate_model_with_tools()
        demonstrate_methodology()
        
        print("\n✅ All demonstrations completed successfully!")
        print("\n🎉 You now have a fully functional agent with search capabilities!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Please check your API keys and internet connection.")

if __name__ == "__main__":
    main() 