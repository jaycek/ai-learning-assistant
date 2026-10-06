import hashlib

import streamlit as st

from core.tracker import Tracker


def render(tracker: Tracker) -> None:
    quizzes = tracker.quizzes
    avg = round(sum(q["pct"] for q in quizzes) / len(quizzes)) if quizzes else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Topics studied", len(tracker.topics))
    c2.metric("Marked learnt", sum(t["learnt"] for t in tracker.topics.values()))
    c3.metric("Quizzes taken", len(quizzes))
    c4.metric("Avg quiz score", f"{avg}%")

    st.subheader("Topics")
    if tracker.topics:
        st.dataframe(
            [{"Topic": name, "Source": t["source"], "Learnt": "✅" if t["learnt"] else "",
              "Interactions": t["interactions"], "Last studied": t.get("last_studied", "")}
             for name, t in tracker.topics.items()],
            hide_index=True)
    else:
        st.caption("Nothing yet. Topics are logged when you finish flashcards, take a quiz, or study in Topic Tutor.")

    if quizzes:
        st.subheader("Quiz scores")
        st.line_chart([q["pct"] for q in quizzes], x_label="Quiz #", y_label="% correct")
        weak = {}
        for q in quizzes:
            weak.setdefault(q["topic"], []).append(q["pct"])
        st.dataframe(
            sorted(({"Topic": k, "Avg %": round(sum(v) / len(v))} for k, v in weak.items()),
                   key=lambda r: r["Avg %"]),
            hide_index=True)

    st.divider()
    st.caption("Progress is kept only for this browser session. Save it to a file to continue later.")
    st.download_button("⬇️ Save progress (JSON)", tracker.to_json(), "learning_progress.json", "application/json")
    up = st.file_uploader("Load saved progress", type="json", key="progress_upload")
    if up is not None:
        raw = up.getvalue()
        digest = hashlib.md5(raw).hexdigest()
        if st.session_state.get("progress_digest") != digest:  # load each file once
            try:
                st.session_state.tracker = Tracker.from_json(raw.decode("utf-8"))
                st.session_state.progress_digest = digest
                st.rerun()
            except Exception as e:
                st.error(f"Couldn't load that file: {e}")
