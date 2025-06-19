# Day 9: 5-Pillar Resume Validator – Multi-Agent OKR Submission Checker

## 🎯 Project Goal

Build a multi-agent AI system to validate student OKR submissions (e.g., resumes) against a 5-pillar rubric, using autonomous agents for content checking, semantic drift detection, measurability analysis, and RAG-powered suggestions.

## 🏛️ The 5 Pillars (Resume Criteria)

- **CLT**: Center for Learning and Teaching
- **CFC**: Center for Creativity
- **SCD**: Skill and Career Development
- **IIPC**: Industrial Institute Partnership Cell
- **SRI**: Social Responsive Initiative

Each resume is expected to address all 5 pillars, either as sections or content.

---

## ⚠️ Current Implementation Status

- **Implemented:**
  - Pillar validation logic (`rag_validator.py`) is functional and used in the Streamlit app (`app.py`).
  - Users can upload a PDF resume, and the app checks for the presence of all 5 pillars.
- **NOT Implemented:**
  - The 4-agent system (Pillar Alignment Checker, Semantic Drift Detector, Measurability Checker, RAG-powered Suggester) is **not yet implemented**.
  - The `agents/` directory and agent files are placeholders and do not contain working agent logic.
  - Outcome analysis and advanced suggestions described in the architecture are not available in the current codebase.

**Potential Error:** Users may expect features that are not yet implemented. Please refer to this section for the current capabilities.

---

## 🤖 Intended Agent Architecture (Planned)

### 1. **Agent 1: Pillar Alignment Checker**
- Checks if the submission contains all 5 pillars (using fuzzy matching or LLM).
- Returns: "All pillars present / Missing pillars: [x, y]"

### 2. **Agent 2: Semantic Drift Detector**
- Checks if the document is actually a resume or something unrelated (e.g., a project report).
- Returns: "Looks like a resume / Doesn't match expected format"

### 3. **Agent 3: Measurability & Completeness Checker**
- Checks if pillar sections are descriptive and outcome-based (not vague).
- Returns: Score or verdict on whether content is shallow vs. rich.

### 4. **Agent 4: RAG-powered Suggestion Generator**
- If mismatched or vague, retrieves example OKRs or resume excerpts from a local knowledge base.
- Returns: "Here's how others structured the section 'Career Goals' better..."

---

## 🗂️ File Structure
```
Day 9/
├── agents/
│   ├── content_checker.py           # (Placeholder) Agent 1: Pillar Alignment Checker
│   ├── semantic_Drift.py           # (Placeholder) Agent 2: Semantic Drift Detector
│   ├── measurability_checker.py    # (Placeholder) Agent 3: Measurability Checker
│   └── suggestion_generator.py     # (Placeholder) Agent 4: RAG-powered Suggester
├── app.py                          # Streamlit frontend
├── rag_validator.py                # Pillar validation logic
├── pillars.py                      # Pillar definitions
├── requirements.txt                # Python dependencies
├── README.md                       # This documentation
├── test_analyzer.py                # (Optional) Test script
└── venv/                           # Virtual environment (not tracked)
```

---

## 🔄 Workflow Process (Current)

1. **Document Upload & Text Extraction**
   - User uploads a PDF resume via Streamlit UI (`app.py`).
   - Text is extracted using PyPDF2.

2. **Pillar Validation**
   - The app checks for all 5 pillars using `rag_validator.py`.
   - Results are displayed: found pillars, missing pillars, and descriptions.

3. **(Planned) Agent Orchestration**
   - The system will eventually run all 4 agents on the extracted text (not yet implemented).

---

## 🧩 Pillar Definitions (from `pillars.py`)

```
PILLARS = {
    "CLT": ["Center for Learning and Teaching", "CLT"],
    "CFC": ["Center for Creativity", "CFC"],
    "SCD": ["Skill and Career Development", "SCD"],
    "IIPC": ["Industrial Institute Partnership Cell", "IIPC"],
    "SRI": ["Social Responsive Initiative", "SRI"]
}
```

---

## 🛠️ Setup Instructions

1. **Environment Setup**
```bash
cd "Day 9"
pip install -r requirements.txt
```

2. **Run the Application**
```bash
streamlit run app.py
```

---

## 📊 Example Output (Streamlit UI)

```
✅ Your document includes all required pillars!
❌ Missing pillar(s):
- CLT: The Center for Learning and Teaching focuses on enhancing teaching methodologies and learning outcomes through innovative educational practices and faculty development programs.
...
```

---

## 🔍 Troubleshooting
- Ensure all dependencies are installed from `requirements.txt`.
- Only PDF uploads are supported in the current UI.
- The 4-agent system is not yet available; only pillar validation is functional.

---
This project is part of the Agantic AI Hackathon (Day 9 challenge).

