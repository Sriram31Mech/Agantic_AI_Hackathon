"""
Test script for the Agent with Search Capabilities
This script demonstrates the agent's functionality with various example queries.
"""

import os
from dotenv import load_dotenv
from agent import create_agent, run_single_query

def test_agent_functionality():
    """Test the agent with various example queries"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if required API keys are available
    required_keys = ["GOOGLE_API_KEY", "TAVILY_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
        print("Please set them in your .env file or environment variables.")
        return
    
    print("🚀 Creating agent...")
    agent_executor = create_agent()
    print("✅ Agent created successfully!\n")
    
    # Test queries
    test_queries = [
        "Hi, I'm Alice and I live in New York.",
        "What's the current weather in New York?",
        "Tell me about the latest AI developments",
        "What are the top restaurants in San Francisco?",
        "How does machine learning work?"
    ]
    
    print("🧪 Running test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 50)
        
        try:
            run_single_query(agent_executor, query)
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
        
        print("\n" + "="*60 + "\n")

def test_tool_calling():
    """Test specific tool calling functionality"""
    
    print("🔧 Testing tool calling functionality...\n")
    
    # Create agent
    agent_executor = create_agent()
    
    # Test queries that should trigger tool calls
    tool_test_queries = [
        "Search for the latest news about artificial intelligence",
        "Find information about the weather in London",
        "Look up the current stock price of Apple"
    ]
    
    for query in tool_test_queries:
        print(f"Query: {query}")
        print("Expected: Should trigger Tavily search tool")
        print("-" * 40)
        
        try:
            run_single_query(agent_executor, query)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")

def test_conversational_memory():
    """Test conversational memory functionality"""
    
    print("🧠 Testing conversational memory...\n")
    
    # Create agent
    agent_executor = create_agent()
    
    # Simulate a conversation
    conversation = [
        "Hi, I'm Bob and I live in San Francisco.",
        "What's the weather like where I live?",
        "Is it going to rain tomorrow?",
        "What should I wear for the weather?"
    ]
    
    config = {"configurable": {"thread_id": "memory_test"}}
    
    for i, message in enumerate(conversation, 1):
        print(f"Message {i}: {message}")
        print("-" * 40)
        
        input_message = {"role": "user", "content": message}
        
        try:
            for step in agent_executor.stream(
                {"messages": [input_message]}, config, stream_mode="values"
            ):
                last_message = step["messages"][-1]
                if hasattr(last_message, 'pretty_print'):
                    last_message.pretty_print()
                else:
                    print(f"Assistant: {last_message.content}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("🧪 Agent Testing Suite")
    print("=" * 50)
    
    # Run different tests
    try:
        test_agent_functionality()
        test_tool_calling()
        test_conversational_memory()
        
        print("✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user.")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}") 