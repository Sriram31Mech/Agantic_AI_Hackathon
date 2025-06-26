# import streamlit as st
# from datetime import date, datetime
# import sys
# import os

# # Add backend folder to path
# sys.path.append(r'D:\Hackathon\Trial')

# # DEBUG: Import check
# print("✅ Imported sys.path and added backend")
# try:
#     from backend.okr_parser import parse_okr
#     from backend.micro_okr import create_micro_tasks
#     print("✅ Successfully imported okr_parser and micro_okr")
# except Exception as e:
#     print("❌ Error importing backend modules:", e)
#     st.error(f"Import error: {e}")

# st.set_page_config(page_title="OKR Action Tracker", layout="centered")
# st.title("🎯 OKR Action Tracker - Input Form")
# st.subheader("Step 1: Enter Your OKR Details")

# # def get_schedule_gaps(tasks):
# #     """Compute day gaps between consecutive task due dates."""
# #     gaps = []
# #     for prev, curr in zip(tasks, tasks[1:]):
# #         d1 = datetime.strptime(prev["due"], "%Y-%m-%d")
# #         d2 = datetime.strptime(curr["due"], "%Y-%m-%d")
# #         gaps.append((d2 - d1).days)
# #     return gaps

# with st.form("okr_input_form"):
#     title       = st.text_input("Objective Title", placeholder="e.g., Publish AI Articles")
#     description = st.text_area(
#         "Description (min 10 chars)",
#         placeholder="e.g., I want to publish 3 AI articles this quarter."
#     )
#     deadline    = st.date_input("Select Deadline", min_value=date.today())
#     submitted   = st.form_submit_button("Submit OKR")

# if submitted:
#     # --- Validation ---
#     if not title.strip():
#         st.error("Title cannot be empty.")
#     elif len(description.strip()) < 10:
#         st.error("Description must be at least 10 characters.")
#     else:
#         st.success("✅ OKR submitted successfully!")
#         st.write("### OKR Summary:")
#         st.write(f"**Title**: {title}")
#         st.write(f"**Description**: {description}")
#         st.write(f"**Deadline**: {deadline}")

#         # --- Parse OKR ---
#         okr_input = f"{description} by {deadline}"
#         try:
#             parsed = parse_okr(okr_input)
#             st.write("### 🧠 Parsed Output:")
#             st.json(parsed)
#         except Exception as e:
#             st.error(f"Parsing error: {e}")
#             parsed = None

#         # --- Generate Micro-Tasks ---
#         if parsed:
#             try:
#                 # Ensure deliverables → key_results
#                 parsed["key_results"] = parsed.get("deliverables", [])
#                 micro_tasks = create_micro_tasks(parsed, deadline=str(deadline))

#                 if not micro_tasks:
#                     st.warning("⚠️ No microtasks generated.")
#                 else:
#                     st.write("### 📋 Micro-Level Tasks:")
#                     for i, t in enumerate(micro_tasks, 1):
#                         st.markdown(f"**Task {i}**: {t['task']}")
#                         st.markdown(f"• Due: {t['due']}  ")
#                         st.markdown(f"• Evidence: {t['evidence_hint']}")
#                         st.markdown(f"• Level: `{t['level']}`")
#                         st.markdown("---")

#                     # # --- Schedule Diagnostics ---
#                     # gaps = get_schedule_gaps(micro_tasks)
#                     # st.write("### ⏱️ Days Between Task Due Dates")
#                     # st.write(gaps)

#             except Exception as e:
#                 st.error(f"Micro-tasks error: {e}")
