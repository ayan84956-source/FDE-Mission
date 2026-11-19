import json

import streamlit as st

from agent import database
from config import settings

JOB_ID = "backend_python_developer"

ICONS = {"met": "✅", "not_met": "❌", "unknown": "❓"}
LABEL_ICONS = {"strong_match": "🟢", "needs_review": "🟡"}
LABEL_TEXT = {"strong_match": "Strong match", "needs_review": "Needs review"}
DECISION_ICONS = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
ORIGINAL_FOLDERS = (
    settings.INBOX_DIR,
    settings.SAMPLE_DATA,
    settings.ROOT / "sample_data" / "test_set",
)


def load_email_index():
    """Sender and subject for each saved attachment. Empty if no email was fetched."""
    path = settings.INBOX_DIR / ".emails.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_original(file_name):
    """Look for the original resume file. Returns a Path, or None."""
    for folder in ORIGINAL_FOLDERS:
        path = folder / file_name
        if path.is_file():
            return path
    return None


def reason_lines(items):
    """One line per rule, with an icon, as a single tight block of text."""
    return "  \n".join(f"{ICONS[item['status']]} {item['reason']}" for item in items)


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
    for decision in ("pending", "approved", "rejected"):
        counts[decision] = sum(1 for r in candidates if r["decision"] == decision)

    view = st.radio(
        "Show",
        ["all", "pending", "approved", "rejected"],
        horizontal=True,
        key="view",
        format_func=lambda option: f"{option.capitalize()} ({counts[option]})",
    )
    shown = candidates if view == "all" else [r for r in candidates if r["decision"] == view]

    if not shown:
        st.info("No candidates in this view.")

    for row in shown:
        person = row["display_name"] or "Name not found"
        label = row["label"]
        title = (
            f"{LABEL_ICONS.get(label, '⚪')} **{person}**  ·  "
            f"{LABEL_TEXT.get(label, label)}  ·  "
            f"{DECISION_ICONS[row['decision']]} {row['decision'].capitalize()}"
        )
        with st.expander(title):
            details = [f"File: {row['source_file']}"]
            sender_info = email_index.get(row["source_file"])
            if sender_info:
                details.append(f"From: {sender_info['sender']}")
                details.append(f"Subject: {sender_info['subject']}")
            st.caption("  ·  ".join(details))

            st.write(row["summary"] or row["note"])

            rules = row["rule_rows"]
            if rules:
                left, right = st.columns(2)
                left.markdown("**Must-haves**\n\n" + reason_lines(rules["must_have"]))
                right.markdown("**Nice-to-haves**\n\n" + reason_lines(rules["nice_to_have"]))

            col1, col2, col3, col4 = st.columns(4)
            if col1.button("✅ Approve", key=f"approve_{row['id']}",
                           disabled=row["decision"] == "approved"):
                database.set_decision(row["id"], "approved")
                st.rerun()
            if col2.button("❌ Reject", key=f"reject_{row['id']}",
                           disabled=row["decision"] == "rejected"):
                database.set_decision(row["id"], "rejected")
                st.rerun()
            if col3.button("🔄 Reset", key=f"reset_{row['id']}",
                           disabled=row["decision"] == "pending"):
                database.set_decision(row["id"], "pending")
                st.rerun()

            original = find_original(row["source_file"])
            if original:
                col4.download_button(
                    "📄 Original",
                    data=original.read_bytes(),
                    file_name=original.name,
                    key=f"original_{row['id']}",
                )
            else:
                col4.caption("No original file")

    if counts["rejected"]:
        st.divider()
        with st.expander(f"Delete the {counts['rejected']} rejected candidates"):
            st.warning(
                "This permanently deletes their saved results and their original "
                "files in the inbox. It cannot be undone."
            )
            confirmed = st.checkbox("I understand, delete them", key="confirm_delete")
            st.button("Delete all rejected", disabled=not confirmed, on_click=delete_rejected)