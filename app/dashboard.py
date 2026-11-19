import json
import streamlit as st
from agent import database
from config import settings

JOB_ID = "backend_python_developer"

ICONS = {"met": "✅", "not_met": "❌", "unknown": "❓"}

def load_email_index():
    """Sender and subject for each saved attachment. Empty if no email was fetched."""
    path = settings.INBOX_DIR / ".emails.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def find_original(file_name):
    for folder in (settings.INBOX_DIR, settings.SAMPLE_DATA):
        path = folder / file_name
        if path.is_file():
            return path
    return None

def remove_files(names):
    """Delete the original files in the inbox and their sender entries."""
    index = load_email_index()
    for name in names:
        path = settings.INBOX_DIR / name
        if path.is_file():
            path.unlink()
        index.pop(name, None)
    index_path = settings.INBOX_DIR / ".emails.json"
    if index_path.is_file():
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def delete_rejected():
    names = database.delete_decided(JOB_ID, "rejected")
    remove_files(names)
    st.session_state["confirm_delete"] = False


st.title("Resume Screening")

candidates = database.list_candidates(JOB_ID)
email_index = load_email_index()

if not candidates:
    st.info("No resumes yet. Run the pipeline first.")
else:
    counts = {"all": len(candidates)}
    for name in ("pending", "approved", "rejected"):
        counts[name] = sum(1 for r in candidates if r["decision"] == name)

    view = st.radio(
        "Show",
        ["all", "pending", "approved", "rejected"],
        horizontal=True,
        key="view",
        format_func=lambda name: f"{name.capitalize()} ({counts[name]})",
    )
    shown = candidates if view == "all" else [r for r in candidates if r["decision"] == view]

    if counts["rejected"]:
        with st.expander(f"Delete the {counts['rejected']} rejected candidates"):
            st.warning(
                "This permanently deletes their saved results and their original "
                "files in the inbox. It cannot be undone."
            )
            confirmed = st.checkbox("I understand, delete them", key="confirm_delete")
            st.button("Delete all rejected", disabled=not confirmed, on_click=delete_rejected)

    if not shown:
        st.info("No candidates in this view.")

    for row in shown:
        title = f"{row['display_name'] or 'Name not found'}  ({row['source_file']})  |  {row['label']}  |  {row['decision']}"
        with st.expander(title):
            st.write(row["summary"] or row["note"])

            sender_info = email_index.get(row["source_file"])
            if sender_info:
                st.caption(f"From: {sender_info['sender']} | Subject: {sender_info['subject']}")

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