import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# Configure Gemini model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# HealthSecure Insurance Plan Data
policies = [
    {
        "name": "Basic Health Plan",
        "eligibility": "18-55",
        "type": "individual",
        "coverage": "Essential care, in-patient, emergency only",
        "features": ["emergency", "in-patient"],
        "premium": 150,
        "limit": 100000
    },
    {
        "name": "Family Health Plus Plan",
        "eligibility": "Families (21+), dependents ≤ 25",
        "type": "family",
        "coverage": "In-patient + out-patient, specialists, diagnostics, ambulance",
        "features": ["in-patient", "out-patient", "specialist", "ambulance", "prescriptions", "diagnostics"],
        "premium": 350,
        "limit": 500000
    },
    {
        "name": "Comprehensive Health & Wellness Plan",
        "eligibility": "No age restrictions",
        "type": "individual/family",
        "coverage": "Full care + wellness + mental health + specialists",
        "features": ["in-patient", "out-patient", "wellness", "mental health", "nutrition", "specialist", "prescriptions", "diagnostics"],
        "premium": 500,
        "limit": 1000000
    },
    {
        "name": "Senior Health Security Plan",
        "eligibility": "55+",
        "type": "individual",
        "coverage": "Senior-focused care, private rooms, vision, dental, long-term support",
        "features": ["senior", "dental", "vision", "prescriptions", "specialist", "mobility", "in-patient"],
        "premium": 600,
        "limit": 750000
    }
]

# Health needs for selection
health_needs_options = [
    "maternity", "vision", "dental", "wellness", "mental health", "emergency",
    "in-patient", "out-patient", "ambulance", "specialist", "prescriptions", "diagnostics", "nutrition", "mobility", "senior"
]

# Generate prompt and recommendation
def generate_recommendation(user_data):
    policy_text = "\n".join(
        f"""Policy Name: {p['name']}
Eligibility: {p['eligibility']}
Type: {p['type']}
Coverage: {p['coverage']}
Features: {", ".join(p['features'])}
Premium: ${p['premium']}/month
Coverage Limit: ${p['limit']:,}
""" for p in policies
    )

    prompt = f"""
You are a smart healthcare insurance agent for HealthSecure Insurance Ltd.

Suggest the most suitable policy for the client based on their age, family type, and specific healthcare needs.

### Client Profile:
Age: {user_data['age']}
Plan Type: {user_data['plan_type']}
Health Needs: {", ".join(user_data['needs'])}

### Policies Available:
{policy_text}

### Respond in this format:
**Recommended Plan**: [Plan Name]  
**Why**: [Why it's best suited based on user's profile]  
**Other Suggestions**: [If applicable]
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error from model: {str(e)}"

# UI
st.set_page_config(page_title="🛡️ Health Policy Sales Agent")
st.title("🛡️ Smart Healthcare Policy Recommender")
st.markdown("Get the most suitable plan for your client's needs.")

with st.form("policy_form"):
    age = st.number_input("Client Age", min_value=0, max_value=120, value=35)
    plan_type = st.selectbox("Coverage Type", ["individual", "family"])
    needs = st.multiselect("Select Client Health Needs", options=health_needs_options)

    submitted = st.form_submit_button("🔍 Recommend Policy")

    if submitted:
        user_data = {"age": age, "plan_type": plan_type, "needs": needs}

        with st.spinner("Analyzing best plan for the client..."):
            recommendation = generate_recommendation(user_data)

        st.success("✅ Recommendation Ready:")
        st.markdown(recommendation)
