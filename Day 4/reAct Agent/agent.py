import os
import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv


load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Tavily client for search
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class ReActAgent:
    def __init__(self, topic):
        self.topic = topic
        self.questions = []
        self.answers = {}

    def generate_questions(self):
        prompt = f"Generate 5-6 in-depth research questions about the topic: {self.topic}"
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text
        self.questions = [line.strip("-• ") for line in text.strip().split("\n") if line.strip()]
        return self.questions

    def search_answers(self):
        for question in self.questions:
            trimmed_question = question[:400] 
            try:
                result = tavily.search(query=trimmed_question, search_depth="advanced", include_answer=True)
                top_results = result.get("results", [])[:3]
                summary = "\n".join(
                    [f"🔹 {r.get('title')}: {r.get('content')[:200]}..." for r in top_results]
                )
                self.answers[question] = summary
            except Exception as e:
                self.answers[question] = f"❌ Error fetching results: {e}"
        return self.answers

