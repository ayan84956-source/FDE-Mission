import streamlit as st
from agent import database
from config import settings

JOB_ID = "backend_python_developer"

ICONS = {"met": "✅", "not_met": "❌", "unknown": "❓"}


def find_original(file_name):
    for folder in (settings.INBOX_DIR, settings.SAMPLE_DATA):
        path = folder / file_name
        if path.is_file():
            return path
    return None


st.title("Resume Screening")

candidates = database.list_candidates(JOB_ID)

if not candidates:
    st.info("No resumes yet. Run the pipeline first.")
else:
    for row in candidates:
        title = f"{row['display_name'] or 'Name not found'}  ({row['source_file']})  |  {row['label']}  |  {row['decision']}"
        with st.expander(title):
            st.write(row["summary"] or row["note"])

            rules = row["rule_rows"]
            if rules:
                st.subheader("Must-haves")
                for item in rules["must_have"]:
                    st.write(f"{ICONS[item['status']]} {item['reason']}")

                st.subheader("Nice-to-haves")
                for item in rules["nice_to_have"]:
                    st.write(f"{ICONS[item['status']]} {item['reason']}")

            original = find_original(row["source_file"])
            if original:
                st.download_button(
                    "Open original resume",
                    data=original.read_bytes(),
                    file_name=original.name,
                    key=f"original_{row['id']}",
                )
            else:
                st.caption("Original file not found")

            col1, col2, col3 = st.columns(3)
            if col1.button("Approve", key=f"approve_{row['id']}"):
                database.set_decision(row["id"], "approved")
                st.rerun()
            if col2.button("Reject", key=f"reject_{row['id']}"):
                database.set_decision(row["id"], "rejected")
                st.rerun()
            if col3.button("Reset", key=f"reset_{row['id']}"):
                database.set_decision(row["id"], "pending")
                st.rerun()