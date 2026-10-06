import streamlit as st


def scope_controls(doc: dict, key: str):
    """Let the user limit generation to a page range or a topic within the notes."""
    mode = st.radio("Scope", ["Whole document", "Page range", "Focus on a topic"],
                    horizontal=True, key=f"{key}_scope")
    page_range, focus = None, None
    if mode == "Page range":
        c1, c2 = st.columns(2)
        lo = c1.number_input("From page", 1, doc["pages"], 1, key=f"{key}_lo")
        hi = c2.number_input("To page", 1, doc["pages"], doc["pages"], key=f"{key}_hi")
        page_range = (int(min(lo, hi)), int(max(lo, hi)))
    elif mode == "Focus on a topic":
        focus = st.text_input("Topic or keywords from your notes", key=f"{key}_focus")
    return page_range, focus
