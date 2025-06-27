import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2,
    google_api_key=google_api_key
)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are an expert OKR assistant.

Given the following user input:
"{okr_text}"

Extract and return a valid JSON object with:
1. "objective": A clean, clear statement of the goal.
2. "deliverables": A list (1-item final output) of measurable tasks required to complete the objective.
3. "deadline": A date (YYYY-MM-DD), quarter (Q1–Q4), or "Unspecified" if not mentioned.

Only respond with a valid JSON object.
""")

# LangChain chain
okr_chain = prompt | llm

# Function to parse OKR
def parse_okr(okr_text: str) -> dict:
    try:
        response = okr_chain.invoke({"okr_text": okr_text})
        text = response.strip().strip("```json").strip("```").strip()
        
        # Safely evaluate JSON output
        data = eval(text)  # Consider using `json.loads` after cleaning

        # Validate deadline
        if data.get("deadline"):
            if not re.match(r"\b\d{4}-\d{2}-\d{2}\b", data["deadline"]) and not re.match(r"\bQ[1-4]\b", data["deadline"].upper()):
                data["deadline"] = "Unspecified"

        return data

    except Exception as e:
        return {
            "objective": okr_text.strip(),
            "deliverables": ["Could not extract deliverables reliably."],
            "deadline": "Unspecified"
        }
