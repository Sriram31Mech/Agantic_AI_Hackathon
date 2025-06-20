# agents/okr_parser.py

import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is missing from .env file. Please add it to run the backend.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini Model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Load RAG context from past OKRs (just load JSON, no vector store)
def load_context():
    try:
        with open("data/okr_examples.json", "r", encoding="utf-8") as f:
            okrs = json.load(f)
        context_list = [okr["okr"] for okr in okrs if "okr" in okr]
        if not context_list:
            return None, "Warning: okr_examples.json is empty or contains no valid OKRs."
        return context_list, None
    except FileNotFoundError:
        return None, "Error: data/okr_examples.json file is missing. Please add example OKRs."
    except Exception as e:
        return None, f"Error loading okr_examples.json: {str(e)}"

def format_context(context_list):
    return "\n\n".join(context_list) if context_list else ""

def try_parse_json(text):
    """
    Try to parse text as JSON. If it fails, attempt to fix common issues (single quotes, trailing commas).
    """
    try:
        return json.loads(text), None
    except Exception as e1:
        # Try to fix single quotes
        fixed = text.replace("'", '"')
        # Remove trailing commas before closing braces/brackets
        fixed = re.sub(r',([\s\n]*[}\]])', r'\1', fixed)
        try:
            return json.loads(fixed), None
        except Exception as e2:
            return None, f"Malformed JSON from Gemini. Error: {str(e2)}. Raw response: {text}"

# OKR Parser Agent using Gemini
def parse_okr(okr_input: str) -> dict:
    context_list, context_error = load_context()
    context = format_context(context_list)

    prompt = f"""
You are an OKR parsing agent. Your job is to convert a user-submitted OKR into structured JSON format.

Use this format:
{{
  "objective": "...",
  "deliverables": ["...", "..."],
  "timeline": "..."
}}

Use the following context (past OKRs) to help you understand ambiguous inputs:

{context}

Input OKR: {okr_input}

Return only the structured JSON.
"""

    response = gemini_model.generate_content(prompt)
    result, parse_error = try_parse_json(response.text)
    if not result:
        result = {"error": "Could not parse response as JSON", "raw": response.text, "details": parse_error}
    if context_error:
        result["context_warning"] = context_error
    return result

# Example Usage
if __name__ == "__main__":
    okr_text = "Submit a research paper on climate tech innovations by end of Q3"
    parsed = parse_okr(okr_text)
    print(json.dumps(parsed, indent=2))