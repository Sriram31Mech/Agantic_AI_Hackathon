import os
import sys
from datetime import datetime
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'okr_agentic_app')))

# --- LLM Setup ---
google_api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2,
    google_api_key=google_api_key
)
parser = JsonOutputParser()

# --- Prompt Template ---
prompt = PromptTemplate(
    template="""
You are an AI productivity assistant. Break down the following OKR into no more than 10 micro-level tasks.

Each task must:
- Be small, specific, and actionable
- Be approximately equal in size and effort
- Be realistically scheduled:
  • Easy tasks (brainstorm, outline): 1–2 days  
  • Medium tasks (draft): 2–3 days  
  • Hard tasks (edit, coordinate): 3–4 days  
- Not compress a large workload into one task
- Have a due date ≤ the overall OKR deadline: {okr_deadline}
- Use YYYY-MM-DD for due dates
- Include a short `evidence_hint` string
- Include a `level` ("easy", "medium", "hard")

Objective:
{objective}

Key Results:
{key_results}

Return EXACT JSON:
[
  {{
    "task": "string",
    "due": "YYYY-MM-DD",
    "evidence_hint": "string",
    "level": "easy|medium|hard"
  }}
]
""",
    input_variables=["objective", "key_results", "okr_deadline"]
)

# --- Helpers ---
def validate_task_schedule(tasks, deadline):
    """Ensure tasks are in ascending order and none exceed the OKR deadline."""
    try:
        dl = datetime.strptime(deadline, "%Y-%m-%d")
        prev = None
        for idx, t in enumerate(tasks, start=1):
            due = datetime.strptime(t["due"], "%Y-%m-%d")
            if due > dl:
                print(f"❌ Task {idx} exceeds overall deadline.")
                return False
            if prev and due < prev:
                print(f"❌ Task {idx} is before Task {idx-1}.")
                return False
            prev = due
        return True
    except Exception as e:
        print("⚠️ Schedule validation error:", e)
        return False

# def save_to_mongo(tasks, objective):
#     """Insert tasks into MongoDB, tagging each with the parent objective."""
#     try:
#         client = MongoClient("MONGODB_URL")
#         db = client["okr_db"]
#         col = db["micro_tasks"]
#         for t in tasks:
#             t["objective"] = objective
#         col.insert_many(tasks)
#         print("✅ Saved microtasks to MongoDB")
#     except Exception as e:
#         print("❌ MongoDB insert failed:", e)

# --- Main Function ---
def create_micro_tasks(parsed_okr, deadline=None):
    print("📥 create_micro_tasks() called")
    key_results = parsed_okr.get("key_results") or parsed_okr.get("deliverables") or []
    if not key_results:
        print("⚠️ No key_results/deliverables found.")
        return []

    # Prepare inputs
    kr_str      = "\n".join(key_results) if isinstance(key_results, list) else str(key_results)
    deadline_str = deadline or "in 2 weeks"

    # Invoke LLM chain
    try:
        formatted = prompt.format(
            objective=parsed_okr["objective"],
            key_results=kr_str,
            okr_deadline=deadline_str
        )
        print("📝 Prompt ready")
        chain = prompt | llm | parser
        result = chain.invoke({
            "objective": parsed_okr["objective"],
            "key_results": kr_str,
            "okr_deadline": deadline_str
        })
        print("✅ LLM chain returned tasks")

        # Validate & persist
        if not validate_task_schedule(result, deadline_str):
            print("⚠️ Invalid schedule detected.")
        # save_to_mongo(result, parsed_okr["objective"])
        return result

    except Exception as e:
        print("❌ Error generating microtasks:", e)
        return []
