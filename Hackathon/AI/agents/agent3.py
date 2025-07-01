# import google.generativeai as genai
# from typing import Dict

# # --------------------
# # CONFIGURE GEMINI API
# # --------------------
# genai.configure(api_key="YOUR_GEMINI_API_KEY")

# # Initialize the model
# model = genai.GenerativeModel("gemini-pro")

# # --------------------
# # VALIDATION FUNCTION
# # --------------------
# def validate_micro_okr(task: str, evidence_hint: str, student_submission: str) -> Dict:
#     prompt = f"""
# You are an AI agent that validates whether a student's submitted evidence matches the required expectations.

# Task: {task}
# Expected Evidence Hint: {evidence_hint}

# Student's Submitted Evidence:
# \"\"\"
# {student_submission}
# \"\"\"

# Evaluate the submission strictly.

# Respond ONLY in the following JSON format:

# {{
#   "status": "Valid" | "Invalid" | "Needs Revision",
#   "reason": "Short explanation here"
# }}
#     """

#     try:
#         response = model.generate_content(prompt)
#         raw_output = response.text.strip()
#         print("🔍 Raw Gemini Output:")
#         print(raw_output)

#         # Use eval if output is safe, or you can use json.loads with sanitization
#         return eval(raw_output)

#     except Exception as e:
#         return {
#             "status": "Error",
#             "reason": str(e)
#         }

# # --------------------
# # TESTING EXAMPLE
# # --------------------
# if __name__ == "__main__":
#     task = "Brainstorm 10 potential AI article topics."
#     evidence_hint = "List of brainstormed topics"
#     student_submission = """
# 1. AI in Healthcare
# 2. AI in Education
# 3. Ethical AI
# 4. AI in Finance
# 5. AI in Agriculture
# 6. AI and Creativity
# 7. Natural Language Processing
# 8. Computer Vision
# 9. Robotics
# 10. AI for Climate Change
#     """

#     result = validate_micro_okr(task, evidence_hint, student_submission)
#     print("\n✅ Validation Result:")
#     print(result)
