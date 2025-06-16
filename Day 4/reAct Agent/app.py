import streamlit as st
from agent import ReActAgent
from report_generator import generate_report

st.title("🔎 Web Research Agent using ReAct Pattern")
topic = st.text_input("Enter a research topic:")

if topic and st.button("Generate Report"):
    with st.spinner("🧠 Thinking..."):
        agent = ReActAgent(topic)
        questions = agent.generate_questions()
        st.subheader("📌 Generated Questions")
        for q in questions:
            st.markdown(f"- {q}")

        st.info("🌐 Fetching web answers...")
        answers = agent.search_answers()

        report = generate_report(topic, questions, answers)
        st.subheader("📄 Final Report")
        st.markdown(report)

        st.download_button("📥 Download Report", report, file_name="research_report.md")
