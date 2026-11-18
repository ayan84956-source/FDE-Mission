import streamlit as st

from agent import database

JOB_ID = "backend_python_developer"

ICONS = {"met": "✅", "not_met": "❌", "unknown": "❓"}

st.title("Resume Screening")

candidates = database.list_candidates(JOB_ID)

if not candidates:
    st.info("No resumes yet. Run the pipeline first.")
else:
    for row in candidates:
        title = f"{row['source_file']}  |  {row['label']}  |  {row['decision']}"
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