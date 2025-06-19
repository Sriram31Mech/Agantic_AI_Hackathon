"""
Simple Streamlit App for Agent with Search
Streamlined version focusing on core functionality
"""

import streamlit as st
import os
from dotenv import load_dotenv
from agent import create_agent, setup_environment

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None

def initialize_agent():
    """Initialize the agent"""
    try:
        with st.spinner("Setting up agent..."):
            setup_environment()
            agent_executor = create_agent()
            st.session_state.agent_executor = agent_executor
            st.session_state.agent_initialized = True
        st.success("Agent initialized successfully!")
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return False

def chat_with_agent(user_input):
    """Chat with the agent and display streaming response"""
    if not st.session_state.agent_initialized:
        st.error("Agent not initialized. Please check your API keys.")
        return
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Create input for agent
    input_message = {"role": "user", "content": user_input}
    config = {"configurable": {"thread_id": "streamlit_chat"}}
    
    # Create placeholder for streaming response
    response_placeholder = st.empty()
    full_response = ""
    
    try:
        # Stream the response
        for step in st.session_state.agent_executor.stream(
            {"messages": [input_message]}, config, stream_mode="values"
        ):
            last_message = step["messages"][-1]
            
            if hasattr(last_message, 'content') and last_message.content:
                full_response += last_message.content
                # Update the placeholder with current response
                response_placeholder.markdown(f"**🤖 Assistant:** {full_response}")
        
        # Add assistant response to session state
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Main app
st.title("🤖 AI Agent with Search Capabilities")

# Sidebar
with st.sidebar:
    st.header("Setup")
    
    if not st.session_state.agent_initialized:
        if st.button("Initialize Agent", type="primary"):
            initialize_agent()
    else:
        st.success("✅ Agent Ready")
        if st.button("Reinitialize"):
            st.session_state.agent_initialized = False
            st.session_state.agent_executor = None
            st.rerun()
    
    st.header("Quick Actions")
    if st.button("🌤️ Weather"):
        chat_with_agent("What's the weather like today?")
    
    if st.button("📰 News"):
        chat_with_agent("What are the latest news headlines?")
    
    if st.button("🔍 Search"):
        chat_with_agent("Search for information about artificial intelligence")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.header("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**👤 You:** {message['content']}")
    else:
        st.markdown(f"**🤖 Assistant:** {message['content']}")

# Input area
st.markdown("---")
user_input = st.text_area("Ask me anything:", height=100)

if st.button("Send", type="primary"):
    if user_input.strip():
        chat_with_agent(user_input.strip())
        st.rerun()

# Status
st.markdown("---")
if st.session_state.agent_initialized:
    st.success("✅ Agent is ready to chat!")
else:
    st.warning("⚠️ Please initialize the agent first.") 