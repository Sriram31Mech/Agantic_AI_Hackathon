import streamlit as st
import PyPDF2
import io
from rag_validator import validate_resume_pillars
from outcome_analyzer import OutcomeAnalyzer

# Set page config
st.set_page_config(
    page_title="OKR Task Validator - 5 Pillar Resume",
    page_icon="📄",
    layout="centered"
)

# Initialize the OutcomeAnalyzer
analyzer = OutcomeAnalyzer()

# Title and description
st.title("Submit the 5 Pillar Based Resume")

task_name = st.text_input("Task Name", value="5 Pillar Based Resume", disabled=True)

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=['pdf'])

if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Validate the resume
    validation_result = validate_resume_pillars(text)
    
    # Display results
    if validation_result["is_valid"]:
        st.success("✅ Your document includes all required pillars!")
    else:
        st.error("❌ Missing pillar(s):")
        for pillar in validation_result["missing_pillars"]:
            with st.expander(f"📌 {pillar}"):
                st.write(validation_result['missing_pillars_descriptions'][pillar])
    
    # Display found pillars
    if validation_result["found_pillars"]:
        st.info("Found pillars:")
        for pillar in validation_result["found_pillars"]:
            st.write(f"- {pillar}")
    
    # Generate and display outcome analysis
    st.markdown("## 📊 Outcome Analysis")
    with st.spinner("Generating outcome analysis..."):
        # Create a comprehensive content string for analysis
        analysis_content = f"""
        Resume Content:
        {text}
        
        Validation Results:
        - Found Pillars: {', '.join(validation_result['found_pillars']) if validation_result['found_pillars'] else 'None'}
        - Missing Pillars: {', '.join(validation_result['missing_pillars']) if validation_result['missing_pillars'] else 'None'}
        - Is Valid: {validation_result['is_valid']}
        
        Missing Pillar Descriptions:
        {chr(10).join([f"- {pillar}: {validation_result['missing_pillars_descriptions'][pillar]}" for pillar in validation_result['missing_pillars']]) if validation_result['missing_pillars'] else 'All pillars present'}
        """
        
        analysis = analyzer.analyze_outcome(analysis_content)
        st.markdown(analysis)

st.markdown("---")
st.markdown("OKR Task Validator - 5 Pillar Resume Matching System") 