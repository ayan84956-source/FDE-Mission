from datetime import datetime
from pathlib import Path

import streamlit as st

from agent import database
from agent.check_rules import load_checklist
from agent.pipeline import process_resume
from config import settings

JOB_NAME = "backend_python_developer"

st.title("Add a resume")
st.write("Upload one resume (PDF, Word or text) to screen it for this opening.")

uploaded = st.file_uploader("Choose a resume", type=["pdf", "docx", "txt"])

if uploaded is not None and st.button("Screen this resume"):
    settings.INBOX_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = settings.INBOX_DIR / f"{stamp}_{Path(uploaded.name).name}"
    path.write_bytes(uploaded.getvalue())

    checklist = load_checklist(JOB_NAME)
    database.init_db()

    try:
        with st.spinner("Reading the resume. This takes about 30 to 40 seconds..."):
            status, score, seconds = process_resume(path, checklist)
    except Exception as error:
        st.error(f"Something went wrong: {error}")
    else:
        rows = [
            row
            for row in database.list_candidates(checklist["job_id"])
            if row["source_file"] == path.name
        ]
        if status == "ok" and rows:
            st.success(f"Done in {seconds:.0f} seconds. Result: {rows[0]['label']}")
            st.write(rows[0]["summary"])
            st.write("Open the dashboard page in the sidebar to see all the reasons.")
        else:
            st.warning(
                f"The file was saved but could not be read automatically ({status}). "
                "It is on the dashboard for a manual check."
            )