import json
import streamlit as st
from agent.pipeline import rescore
from agent import database
from agent.check_rules import load_checklist
from config import settings

JOB_NAME = "backend_python_developer"


def split_list(text):
    """Turn 'Python, SQL' into ['Python', 'SQL']."""
    return [part.strip() for part in text.split(", ") if part.strip()]


st.title("Checklist")

checklist = load_checklist(JOB_NAME)
must = checklist["must_have"]
nice = checklist["nice_to_have"]

st.subheader("Must-haves")
years = st.number_input(
    "Minimum years of experience",
    min_value=0.0,
    value=float(must["min_years_experience"]),
    step=0.5,
)
required = st.text_input(
    "Required skills (separated by commas)",
    value=", ".join(must["required_skills"]),
)
locations = st.text_input(
    "Accepted locations (separated by commas)",
    value=", ".join(must["locations"]),
)

st.subheader("Nice-to-haves")
nice_skills = st.text_input(
    "Nice-to-have skills (separated by commas)",
    value=", ".join(nice["skills"]),
)

if st.button("Save checklist"):
    if not split_list(required) or not split_list(locations):
        st.error("Required skills and locations cannot be empty. Nothing was saved.")
    else:
        checklist["must_have"]["min_years_experience"] = years
        checklist["must_have"]["required_skills"] = split_list(required)
        checklist["must_have"]["locations"] = split_list(locations)
        checklist["nice_to_have"]["skills"] = split_list(nice_skills)

        path = settings.CHECKLIST_DIR / f"{JOB_NAME}.json"
        path.write_text(json.dumps(checklist, indent=2), encoding="utf-8")
        st.success("Checklist saved. Results already on the dashboard are not updated yet.")

st.divider()
st.write("After saving, apply the checklist to the resumes already on the dashboard.")
reset_decisions = st.checkbox("Also reset all Approve / Reject decisions to pending")
if st.button("Re-score saved resumes"):
    count = rescore(JOB_NAME)
    message = f"Re-scored {count} resumes."
    if reset_decisions:
        for row in database.list_candidates(checklist["job_id"]):
            database.set_decision(row["id"], "pending")
        message += " All decisions were reset to pending."
    st.success(message + " Open the dashboard to see the new results.")