import os
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from langchain.agents import Tool, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage
from langchain.tools import tool
from mongo_clients import db, okr_collection
from datetime import datetime
import json
# from typing import Optional # Removed Optional as hint is removed

import base64
import io
from pypdf import PdfReader
from yarl import URL
import uuid # Added import for uuid
from bson import ObjectId # Ensure ObjectId is imported

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from storage import IStorage, MemStorage
from shared.schemas import TaskStatus

# -------------------------------
# Load env variables
# -------------------------------
# Get the directory where okr_validator.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file, which is two levels up from agents/
dotenv_path = os.path.join(current_dir, '..', '..', '.env') # Corrected path to go from agents/ to Hackathon/AI/

load_dotenv(dotenv_path=dotenv_path)

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
API_URL = os.getenv("API_URL")

print(f"DEBUG: API_URL in okr_validator.py: {API_URL}")

# New environment setup from reference code
def setup_environment():
    os.environ["LANGSMITH_TRACING"] = "true"
    
    required_keys = ["LANGSMITH_API_KEY", "TAVILY_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]

    if missing_keys:
        raise EnvironmentError(f"Missing the following keys in .env file: {', '.join(missing_keys)}")

def init_model():
    return init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Initialize environment and model
try:
    setup_environment()
except EnvironmentError as e:
    print(e)
    # Handle error appropriately, e.g., exit or use fallback

# Replace the previous llm initialization
llm = init_model()

# -------------------------------
# Tool 4: Save validation report to MongoDB
# -------------------------------
def save_validation_report_func(report_details: dict) -> dict:
    """Saves the validation report to a new collection in MongoDB. Input should be a dictionary with 'submission_id', 'okr_id', 'overall_result', and individual agent results."""
    try:
        submission_id = report_details['submission_id']
        okr_id = report_details['okr_id']
        overall_result = report_details['overall_result']
        five_pillars_result = report_details.get('five_pillars_result', '')
        semantic_drift_result = report_details.get('semantic_drift_result', '')
        measurability_result = report_details.get('measurability_result', '')
        suggestions_result = report_details.get('suggestions_result', '')
        comparison_result = report_details.get('comparison_result', '')

    except KeyError as e:
        return {"error": f"Missing key in report_details for save_validation_report: {e}"}

    reports_collection = db["validation_reports"]
    report_data = {
        "submission_id": submission_id,
        "okr_id": okr_id,
        "overall_validation_result": overall_result,
        "five_pillars_check": five_pillars_result,
        "semantic_drift_check": semantic_drift_result,
        "measurability_check": measurability_result,
        "suggestions": suggestions_result,
        "task_evidence_comparison": comparison_result,
        "timestamp": datetime.now().isoformat()
    }
    try:
        reports_collection.insert_one(report_data)
        return {"status": "Report saved successfully"}
    except Exception as e:
        return {"error": f"Failed to save report: {e}"}

# -------------------------------
# Tool 5: Update OKR status in MongoDB
# -------------------------------
@tool
def update_okr_status(okr_id: str) -> dict:
    """Updates all micro_tasks' micro_status to 'completed'."""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DB_NAME")
        collection_name = os.getenv("MONGO_COLLECTION_NAME")

        print(f"[INFO] Connecting to MongoDB at {mongo_uri}")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]  # should be 'micro_tasks'

        try:
            obj_id = ObjectId(okr_id)
        except Exception as e:
            print(f"[ERROR] Invalid ObjectId format: {okr_id}")
            return {"error": "Invalid ObjectId format"}

        print(f"[INFO] Fetching document with _id: {okr_id}")
        okr_doc = collection.find_one({"_id": obj_id})
        if not okr_doc:
            return {"error": "Document not found"}

        micro_tasks = okr_doc.get("micro_tasks", [])
        for task in micro_tasks:
            task["micro_status"] = "completed"

        print(f"[INFO] Updating document with modified micro_tasks...")

        result = collection.update_one(
            {"_id": obj_id},
            {"$set": {"micro_tasks": micro_tasks}}
        )

        print(f"[INFO] Matched: {result.matched_count}, Modified: {result.modified_count}")
        return {"status": "All micro_tasks marked as completed"}

    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return {"error": str(e)}

# -------------------------------
# New Tool 6: Extract text from PDF (base64 encoded)
# -------------------------------
@tool
def extract_text_from_pdf(base64_pdf: str) -> str:
    """Extracts text content from a base64 encoded PDF."""
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# -------------------------------
# New Tool 7: Check URL trustworthiness
# -------------------------------
@tool
def check_url_trustworthiness(url: str, expected_domain: str) -> str:
    """Checks if a URL contains a specific trusted domain."""
    try:
        parsed_url = URL(url)
        if expected_domain.lower() in parsed_url.host.lower():
            return f"URL is from a trusted domain: {expected_domain}"
        else:
            return f"URL is NOT from the expected domain: {expected_domain}"
    except Exception as e:
        return f"Error parsing URL: {e}"

# -------------------------------
# Internal Agents (from reference code)
# -------------------------------
def create_agent1():
    memory = MemorySaver()
    model = init_model()
    tools = []  # Add specific tools for this agent if needed
    prompt = (
        "You are an expert in resume validation. Given an OKR task and a resume summary, "
        "check if the submission includes all 5 required pillars: "
        "1. Personal Background, 2. Academic Background, 3. Projects, 4. Career Goals, 5. Co-curricular Activities."
    )
    return create_react_agent(model, tools, prompt=prompt, checkpointer=memory)

def create_agent2():
    memory = MemorySaver()
    model = init_model()
    tools = [] # Add specific tools for this agent if needed
    prompt = (
        "You are a semantic validator. Compare the student's OKR intent with the submission. "
        "Detect if the student misunderstood the format or type (e.g., submitted a project report instead of a resume). "
        "Flag any drift in modality or purpose."
    )
    return create_react_agent(model, tools, prompt=prompt, checkpointer=memory)

def create_agent3():
    memory = MemorySaver()
    model = init_model()
    tools = [] # Add specific tools for this agent if needed
    prompt = (
        "You are a clarity and specificity checker. Read a resume section and determine whether the statements "
        "are measurable, outcome-driven, and specific. Identify vague or generic lines."
    )
    return create_react_agent(model, tools, prompt=prompt, checkpointer=memory)

def create_agent4():
    memory = MemorySaver()
    model = init_model()
    # Assume get_5pillar_search_tools provides tools relevant for RAG
    # For now, let's keep it simple, if it's not defined, it will cause an error.
    # You might need to define dummy tools or import real ones if they exist elsewhere.
    # resume_tool, okr_tool = get_5pillar_search_tools()
    tools = [] # [resume_tool, okr_tool] # Add specific tools for this agent if needed
    prompt = (
        "You are a suggestion generator. Given a problematic resume section, search for better examples using Tavily "
        "and suggest 2-3 improvements. Use concrete, structured and relevant formats."
    )
    return create_react_agent(model, tools, prompt=prompt, checkpointer=memory)

# -------------------------------
# Setup LangChain Agent (Main Orchestrator Agent)
# -------------------------------
tools = [
    Tool(
        name="save_validation_report_func",
        func=save_validation_report_func,
        description="Saves the validation report to a new collection in MongoDB. Input should be a dictionary with 'submission_id', 'okr_id', 'overall_result', and individual agent results."
    ),
    Tool(
        name="update_okr_status",
        func=update_okr_status,
        description="Updates the status of an OKR to 'completed' in MongoDB."
    ),
    Tool(
        name="extract_text_from_pdf",
        func=extract_text_from_pdf,
        description="Extracts text content from a base64 encoded PDF."
    ),
    Tool(
        name="check_url_trustworthiness",
        func=check_url_trustworthiness,
        description="Checks if a URL contains a specific trusted domain."
    )
]

system_message_template = """
You are an AI agent designed to validate student submissions against their Objectives and Key Results (OKRs). Your primary goal is to ensure the submission meets the OKR's criteria in terms of content, semantic meaning, measurability, and format. You will leverage various specialized sub-agents to perform different aspects of this validation.

Here's the validation process:
1.  **Submission Content:** The submission content is directly provided as an argument to the validation function.
2.  **Perform 5 Pillars Check (Agent 1 - `create_agent1`):** Evaluate if the submission implicitly or explicitly covers the five required pillars for a resume (Personal Background, Academic Background, Projects, Career Goals, Co-curricular Activities). This agent will return a conclusion on the 5 pillars.
3.  **Perform Semantic Drift Check (Agent 2 - `create_agent2`):** Analyze the potential semantic drift between the implied OKR intent and the provided submission content. Flag any drift in modality or purpose. This agent will return an assessment of semantic drift.
4.  **Perform Measurability Check (Agent 3 - `create_agent3`):** Determine whether the statements in the submission are measurable, outcome-driven, and specific. Identify vague or generic lines. This agent will return an assessment of measurability.
5.  **Generate Suggestions (Agent 4 - `create_agent4`):** If any of the above checks reveal issues, generate 2-3 concrete, structured suggestions for improvement based on the identified problems. This agent should also search for better examples using Tavily.
6.  **Consolidate Results:** Combine the results from all checks and suggestions into a comprehensive validation response.
7.  **Save Report:** Use the `save_validation_report_func` tool to save the consolidated validation report to MongoDB.
8.  **Update OKR Status (if applicable):** If the overall validation is successful and indicates that the OKR should be completed, use the `update_okr_status` tool.

Your final output should be a JSON object containing `success` (boolean), `message` (string with all validation details and suggestions), and `okr_update` (string indicating if OKR status was updated).

"""

agent_executor = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)

async def validate_submission(task_id: str, okr_id: str, submission_content: str, submission_type: str, storage: IStorage) -> dict:
    try:
        print(f"DEBUG: validate_submission: Starting for task_id={task_id}, okr_id={okr_id}, submission_type={submission_type}")
        overall_validation_result = ""
        processed_content = submission_content # Initialize processed_content

        # Handle submission type: PDF or URL
        if submission_type == "pdf" or submission_type == "screenshot":
            print(f"DEBUG: validate_submission: Processing PDF/Screenshot for {task_id}")
            try:
                pdf_text = extract_text_from_pdf(submission_content)
                processed_content = pdf_text
                overall_validation_result += f"PDF Text Extraction: {pdf_text[:100]}...\n"
                print(f"DEBUG: validate_submission: Extracted PDF text sample: {pdf_text[:50]}...")
            except Exception as e:
                overall_validation_result += f"Error extracting PDF text: {e}\n"
                processed_content = "" # Clear content if extraction fails
                print(f"DEBUG: validate_submission: PDF/Screenshot extraction failed: {e}")

        elif "url" in submission_type:
            print(f"DEBUG: validate_submission: Processing URL for {task_id}")
            expected_domain = "linkedin.com" if "linkedin" in submission_type else (
                            "github.com" if "git" in submission_type else "")
            print(f"DEBUG: validate_submission: Expected domain for URL: {expected_domain}")
            
            try:
                url_check_result = check_url_trustworthiness(submission_content, expected_domain)
                overall_validation_result += f"URL Trustworthiness: {url_check_result}\n"
                # Optionally, fetch content from URL for further text analysis if needed
                processed_content = submission_content # Keep URL as content for now if it's a valid URL, otherwise clear it
                print(f"DEBUG: validate_submission: URL check result: {url_check_result}")
            except Exception as e:
                overall_validation_result += f"Error checking URL: {e}\n"
                processed_content = "" # Clear content if check fails
                print(f"DEBUG: validate_submission: URL check failed: {e}")
        
        print(f"DEBUG: validate_submission: Processed Content: {processed_content[:100]}...")

        # Step 1: Fetch OKR details from DB to get task_hint and evidence_hint
        print("DEBUG: validate_submission: Fetching OKR details from DB...")
        try:
            okr_details = db["okrs"].find_one({"_id": ObjectId(okr_id)})
            print(f"DEBUG: validate_submission: OKR details fetched: {okr_details}")
        except Exception as e:
            overall_validation_result = f"Error fetching OKR details from DB: {e}"
            print(f"DEBUG: validate_submission: {overall_validation_result}")
            return {"success": False, "message": overall_validation_result}

        task_hint = okr_details.get("description", "") if okr_details else ""
        evidence_hint = okr_details.get("evidence_hint", "") if okr_details else "" # Fetch evidence_hint from OKR details

        print(f"DEBUG: validate_submission: Task Hint: {task_hint}")
        print(f"DEBUG: validate_submission: Evidence Hint: {evidence_hint}")

        if processed_content:
            print(f"DEBUG: validate_submission: Validating content for {task_id} using multi-agents")
            
            config_agent = {
                "configurable": {
                    "thread_id": str(uuid.uuid4()),  # Use UUID for thread_id
                    "checkpoint_ns": "okr_validation",
                    "checkpoint_id": str(uuid.uuid4()) # Use UUID for checkpoint_id
                }
            }
            print(f"DEBUG: validate_submission: Agent config: {config_agent}")

            # Agent 1: OKR vs Submission Checker
            print("DEBUG: validate_submission: Running Agent 1...")
            prompt_agent1 = f"Given OKR task hint: {task_hint}, and submission content: {processed_content}, check for 5 pillars."
            print(f"DEBUG: validate_submission: Agent 1 prompt: {prompt_agent1}")
            result_agent1 = create_agent1().invoke({"messages": [{"role": "user", "content": prompt_agent1}]}, config=config_agent) # Pass config
            five_pillars_result = result_agent1['messages'][-1].content
            overall_validation_result += f"5 Pillars Check: {five_pillars_result}\n"
            print(f"DEBUG: validate_submission: Agent 1 raw result: {result_agent1}")
            print(f"DEBUG: validate_submission: Agent 1 processed result: {five_pillars_result}")

            # Agent 2: Semantic Drift Detector
            print("DEBUG: validate_submission: Running Agent 2...")
            prompt_agent2 = f"Compare OKR intent ({task_hint}) with submission content ({processed_content}) for semantic drift."
            print(f"DEBUG: validate_submission: Agent 2 prompt: {prompt_agent2}")
            result_agent2 = create_agent2().invoke({"messages": [{"role": "user", "content": prompt_agent2}]}, config=config_agent) # Pass config
            semantic_drift_result = result_agent2['messages'][-1].content
            overall_validation_result += f"Semantic Drift Check: {semantic_drift_result}\n"
            print(f"DEBUG: validate_submission: Agent 2 raw result: {result_agent2}")
            print(f"DEBUG: validate_submission: Agent 2 processed result: {semantic_drift_result}")
            
            # Agent 3: Measurability Checker
            print("DEBUG: validate_submission: Running Agent 3...")
            prompt_agent3 = f"Analyze this submission content for measurability, outcome-driven, and specificity: {processed_content}"
            print(f"DEBUG: validate_submission: Agent 3 prompt: {prompt_agent3}")
            result_agent3 = create_agent3().invoke({"messages": [{"role": "user", "content": prompt_agent3}]}, config=config_agent) # Pass config
            measurability_result = result_agent3['messages'][-1].content
            overall_validation_result += f"Measurability Check: {measurability_result}\n"
            print(f"DEBUG: Agent 3 raw result: {result_agent3}")
            print(f"DEBUG: Measurability Check (Agent 3) processed result: {measurability_result}")

            # Agent 4: Suggestion Generator (if any previous validation failed)
            suggestions_result = ""
            if "❌" in overall_validation_result:
                print("DEBUG: validate_submission: Running Agent 4 (Suggestions)...")
                prompt_agent4 = f"Provide suggestions for improving submission: {processed_content} based on OKR hint: {task_hint}."
                print(f"DEBUG: validate_submission: Agent 4 prompt: {prompt_agent4}")
                result_agent4 = create_agent4().invoke({"messages": [{"role": "user", "content": prompt_agent4}]}, config=config_agent) # Pass config
                suggestions_result = result_agent4['messages'][-1].content
                overall_validation_result += f"Suggestions: {suggestions_result}\n"
                print(f"DEBUG: validate_submission: Agent 4 raw result: {result_agent4}")
                print(f"DEBUG: validate_submission: Agent 4 processed result: {suggestions_result}")
            else:
                suggestions_result = "No specific suggestions needed. Submission appears to be in good shape."
                print(f"DEBUG: validate_submission: No suggestions generated as no issues found.")

            # Basic task hint vs evidence hint comparison (still relevant)
            print("DEBUG: validate_submission: Running Task-Evidence Hint comparison...")
            validate_task_hint_input = json.dumps({"task_hint": task_hint, "evidence_hint": evidence_hint}) # Use the fetched evidence_hint
            print(f"DEBUG: validate_submission: Task-Evidence Hint comparison input: {validate_task_hint_input}")
            # Using agent_executor for this tool call as it's part of the main agent's tools
            comparison_result_obj = await agent_executor.ainvoke({"input": f"validate_task_hint: {validate_task_hint_input}"})
            comparison_result = comparison_result_obj["output"]
            overall_validation_result += f"Task-Evidence Hint Match: {comparison_result}\n"
            print(f"DEBUG: validate_submission: Task-Evidence Hint comparison raw result: {comparison_result_obj}")
            print(f"DEBUG: validate_submission: Task-Evidence Hint comparison processed result: {comparison_result}")

        else:
            overall_validation_result = "No content to validate or extraction failed."
            # Initialize individual results to empty strings if no content to validate
            five_pillars_result = ""
            semantic_drift_result = ""
            measurability_result = ""
            suggestions_result = ""
            comparison_result = ""
            print(f"DEBUG: validate_submission: {overall_validation_result}")

        # Step 4: Save validation report
        print(f"DEBUG: validate_submission: Saving validation report for {task_id}")
        save_report_data = {
            "submission_id": task_id,
            "okr_id": okr_id,
            "overall_result": overall_validation_result,
            "five_pillars_result": five_pillars_result,
            "semantic_drift_result": semantic_drift_result,
            "measurability_result": measurability_result,
            "suggestions_result": suggestions_result,
            "comparison_result": comparison_result
        }
        print(f"DEBUG: validate_submission: Save report input: {save_report_data}")
        save_report_result = save_validation_report_func(save_report_data) # Direct call, not through agent
        print(f"DEBUG: validate_submission: Save Report Result: {save_report_result}")

        validation_successful = "❌" not in overall_validation_result
        print(f"DEBUG: validate_submission: Overall validation successful: {validation_successful}")

        # Step 5: Update OKR and Task status
        print("DEBUG: validate_submission: Updating OKR and Task status...")
        if validation_successful:
            print(f"DEBUG: validate_submission: Updating Task {task_id} status to completed.")
            await storage.update_task_status(task_id, "completed")
            # Check if all tasks for the OKR are completed
            print(f"DEBUG: validate_submission: Getting tasks for OKR {okr_id}...")
            okr_tasks = await storage.get_tasks_by_okr(okr_id)
            all_tasks_completed = all(task.status == "completed" for task in okr_tasks)
            print(f"DEBUG: validate_submission: All tasks completed for OKR {okr_id}: {all_tasks_completed}")
            if all_tasks_completed:
                await storage.update_okr_status(okr_id, "completed")
                update_okr_status_result = f"OKR {okr_id} status updated to completed."
                print(f"DEBUG: validate_submission: OKR status updated to completed: {okr_id}")
            else:
                update_okr_status_result = f"OKR {okr_id} not yet completed, {sum(1 for task in okr_tasks if task.status == 'completed')}/{len(okr_tasks)} tasks completed."
                print(f"DEBUG: validate_submission: OKR not fully completed: {okr_id}")
        else:
            print(f"DEBUG: validate_submission: Task {task_id} validation failed.")
            update_okr_status_result = f"Task {task_id} validation failed. OKR {okr_id} status not updated."

        print(f"DEBUG: validate_submission: Final Validation Result for {task_id}:\n{overall_validation_result}")
        print("DEBUG: validate_submission: Returning validation response.")

        return {"success": validation_successful, "message": overall_validation_result, "okr_update": update_okr_status_result}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"An error occurred during validation: {e}", "okr_update": f"Task {task_id} validation failed. OKR {okr_id} status not updated."}