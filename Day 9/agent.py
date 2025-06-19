import os
import getpass
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools.tavily_tools import get_5pillar_search_tools, get_resume_example_query, search_with_tavily_tool

# Load environment variables
load_dotenv()

def setup_environment():
    os.environ["LANGSMITH_TRACING"] = "true"
    
    required_keys = ["LANGSMITH_API_KEY", "TAVILY_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]

    if missing_keys:
        raise EnvironmentError(f"Missing the following keys in .env file: {', '.join(missing_keys)}")

def init_model():
    return init_chat_model("gemini-2.0-flash", model_provider="google_genai")


# Agent 1: OKR vs Submission Checker
def create_agent1():
    memory = MemorySaver()
    model = init_model()
    tools = []  # You may add utils here later
    prompt = (
        "You are an expert in resume validation. Given an OKR task and a resume summary, "
        "check if the submission includes all 5 required pillars: "
        "1. Personal Background, 2. Academic Background, 3. Projects, 4. Career Goals, 5. Co-curricular Activities."
    )
    return create_react_agent(model, tools, system_message=prompt, checkpointer=memory)


# Agent 2: Semantic Drift Detector

def create_agent2():
    memory = MemorySaver()
    model = init_model()
    tools = []
    prompt = (
        "You are a semantic validator. Compare the student's OKR intent with the submission. "
        "Detect if the student misunderstood the format or type (e.g., submitted a project report instead of a resume). "
        "Flag any drift in modality or purpose."
    )
    return create_react_agent(model, tools, system_message=prompt, checkpointer=memory)


# Agent 3: Measurability Checker

def create_agent3():
    memory = MemorySaver()
    model = init_model()
    tools = []
    prompt = (
        "You are a clarity and specificity checker. Read a resume section and determine whether the statements "
        "are measurable, outcome-driven, and specific. Identify vague or generic lines."
    )
    return create_react_agent(model, tools, system_message=prompt, checkpointer=memory)


# Agent 4: Suggestion Generator with RAG (Tavily)

def create_agent4():
    memory = MemorySaver()
    model = init_model()
    resume_tool, okr_tool = get_5pillar_search_tools()
    tools = [resume_tool, okr_tool]
    prompt = (
        "You are a suggestion generator. Given a problematic resume section, search for better examples using Tavily "
        "and suggest 2-3 improvements. Use concrete, structured and relevant formats."
    )
    return create_react_agent(model, tools, system_message=prompt, checkpointer=memory)


# Query Runner for Single Agent

def run_single_agent(agent, query: str, label=""):
    config = {"configurable": {"thread_id": f"{label}_query"}}
    input_message = {"role": "user", "content": query}
    
    print(f"\n🔍 {label} Agent:\nQuery: {query}\nResponse:")
    
    for step in agent.stream({"messages": [input_message]}, config, stream_mode="values"):
        last_message = step["messages"][-1]
        if hasattr(last_message, 'pretty_print'):
            last_message.pretty_print()
        else:
            print(last_message.content)


# Main

def main():
    print("🚀 Initializing 5 Pillar Resume Multi-Agent Validator...")
    setup_environment()
    
    agents = {
        "Agent 1: Alignment Checker": create_agent1(),
        "Agent 2: Semantic Drift": create_agent2(),
        "Agent 3: Measurability": create_agent3(),
        "Agent 4: RAG Suggester": create_agent4()
    }
    
    print("✅ All 4 agents created successfully!\n")
    
    print("Enter your resume validation prompt or paste a resume summary to test all agents.")
    user_query = input("\nPaste query (e.g., OKR + resume snippet):\n> ").strip()
    
    for label, agent in agents.items():
        run_single_agent(agent, user_query, label)

if __name__ == "__main__":
    main()
