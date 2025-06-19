"""
Streamlit App for Agent with Search Capabilities
This provides a web interface to interact with the agent.
"""

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agent import create_agent, setup_environment
from tools.tavily_tools import create_search_tool

# Page configuration
st.set_page_config(
    page_title="AI Agent with Search",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .tool-call {
        background-color: #fff3e0;
        border-left-color: #ff9800;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .status-box {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'agent_executor' not in st.session_state:
        st.session_state.agent_executor = None
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = f"streamlit_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def setup_agent():
    """Setup the agent with proper error handling"""
    try:
        with st.spinner("🔧 Setting up environment..."):
            setup_environment()
        
        with st.spinner("🤖 Creating agent..."):
            agent_executor = create_agent()
            st.session_state.agent_executor = agent_executor
            st.session_state.agent_initialized = True
            
        st.success("✅ Agent initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {str(e)}")
        return False

def display_message(message, is_user=True):
    """Display a message in the chat interface"""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_tool_call(tool_name, tool_args):
    """Display a tool call in the chat interface"""
    st.markdown(f"""
    <div class="chat-message tool-call">
        <strong>🔧 Tool Call:</strong> {tool_name}<br>
        <strong>Arguments:</strong> {json.dumps(tool_args, indent=2)}
    </div>
    """, unsafe_allow_html=True)

def process_agent_response(user_input):
    """Process user input through the agent and display results"""
    if not st.session_state.agent_initialized:
        st.error("❌ Agent not initialized. Please check your API keys.")
        return
    
    # Add user message to chat
    display_message(user_input, is_user=True)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Create input message for agent
    input_message = {"role": "user", "content": user_input}
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    full_response = ""
    
    try:
        # Stream the agent response
        for step in st.session_state.agent_executor.stream(
            {"messages": [input_message]}, config, stream_mode="values"
        ):
            last_message = step["messages"][-1]
            
            # Handle different message types
            if hasattr(last_message, 'content') and last_message.content:
                full_response += last_message.content
                response_placeholder.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {full_response}
                </div>
                """, unsafe_allow_html=True)
            
            # Handle tool calls
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    display_tool_call(tool_call['name'], tool_call['args'])
        
        # Add assistant response to session state
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        st.error(f"❌ Error processing response: {str(e)}")

def main():
    """Main Streamlit app"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Agent with Search Capabilities</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys section
        st.subheader("🔑 API Keys")
        st.info("Set your API keys in the .env file or enter them below:")
        
        # Check if agent is initialized
        if not st.session_state.agent_initialized:
            if st.button("🚀 Initialize Agent", type="primary"):
                if setup_agent():
                    st.rerun()
        else:
            st.success("✅ Agent Ready")
            if st.button("🔄 Reinitialize Agent"):
                st.session_state.agent_initialized = False
                st.session_state.agent_executor = None
                st.rerun()
        
        # Session info
        st.subheader("📊 Session Info")
        st.info(f"Thread ID: {st.session_state.thread_id}")
        st.info(f"Messages: {len(st.session_state.messages)}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Export chat
        if st.session_state.messages:
            chat_data = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="📥 Export Chat",
                data=chat_data,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Display existing messages
        for message in st.session_state.messages:
            display_message(message["content"], is_user=(message["role"] == "user"))
        
        # Input area
        st.markdown("---")
        
        # Quick action buttons
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌤️ Weather Query"):
                process_agent_response("What's the weather like today?")
        
        with col2:
            if st.button("📰 Latest News"):
                process_agent_response("What are the latest news headlines?")
        
        with col3:
            if st.button("🔍 Search Info"):
                process_agent_response("Search for information about artificial intelligence")
        
        # User input
        user_input = st.text_area(
            "💭 Ask me anything:",
            placeholder="Type your message here...",
            height=100,
            key="user_input"
        )
        
        # Send button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📤 Send", type="primary", use_container_width=True):
                if user_input.strip():
                    process_agent_response(user_input.strip())
                    # Clear input
                    st.session_state.user_input = ""
                    st.rerun()
    
    with col2:
        st.subheader("📈 Agent Status")
        
        # Status indicators
        if st.session_state.agent_initialized:
            st.markdown('<div class="status-box success">✅ Agent Active</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box error">❌ Agent Not Ready</div>', unsafe_allow_html=True)
        
        # Tool status
        st.markdown('<div class="status-box info">🔍 Tavily Search: Available</div>', unsafe_allow_html=True)
        
        # Usage tips
        st.subheader("💡 Usage Tips")
        st.markdown("""
        - Ask questions that require real-time information
        - The agent will automatically search when needed
        - Try asking about weather, news, or current events
        - Use natural language - the agent understands context
        """)
        
        # Example queries
        st.subheader("🎯 Example Queries")
        example_queries = [
            "What's the weather in San Francisco?",
            "Tell me about the latest AI developments",
            "What are the top restaurants in New York?",
            "Search for information about climate change",
            "What's happening in the tech world today?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                process_agent_response(query)

if __name__ == "__main__":
    main() 