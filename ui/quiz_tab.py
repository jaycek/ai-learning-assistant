import uuid

import streamlit as st

from core import quiz
from ui.common import scope_controls


def render(doc_id, doc, model, tracker) -> None:
    if not doc:
        st.info("Upload a PDF in the Notes tab first.")
        return
    st.caption(f"Questions are generated **only** from *{doc['name']}*.")
    c1, c2 = st.columns(2)
    n = c1.number_input("Number of questions", 1, 50, 5, key="quiz_n")
    difficulty = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="quiz_diff")
    page_range, focus = scope_controls(doc, "quiz")

    if st.button("Generate quiz", type="primary"):
        bar = st.progress(0.0, text="Writing questions…")
        try:
            qs = quiz.generate_quiz(
                doc_id, int(n), model, difficulty, page_range, focus,
                lambda p: bar.progress(p, text="Writing questions…"))
        except Exception as e:
            bar.empty()
            st.error(str(e))
        else:
            bar.empty()
            if not qs:
                st.error("No usable questions were produced. Try a different scope or model.")
            else:
                note = f"Generated {len(qs)} of {int(n)} requested." if len(qs) < n else ""
                st.session_state.quiz = {"id": uuid.uuid4().hex[:8], "doc_id": doc_id,
                                         "questions": qs, "submitted": False, "answers": [],
                                         "logged": False, "note": note}

    state = st.session_state.get("quiz")
    if not state or state["doc_id"] != doc_id:
        return
    st.divider()
    if state["note"]:
        st.caption(state["note"])
    if state["submitted"]:
        _results(state, doc, tracker)
        return

    qs = state["questions"]
    with st.form(f"quiz_form_{state['id']}"):
        for i, q in enumerate(qs):
            st.markdown(f"**{i + 1}. {q['question']}**")
            st.radio("Choose one", q["options"], index=None,
                     key=f"{state['id']}_q{i}", label_visibility="collapsed")
        submitted = st.form_submit_button("Submit answers", type="primary")
    if submitted:
        state["answers"] = [st.session_state.get(f"{state['id']}_q{i}") for i in range(len(qs))]
        state["submitted"] = True
        st.rerun()


def _results(state, doc, tracker) -> None:
    qs, answers = state["questions"], state["answers"]
    correct = sum(a == q["options"][q["answer_index"]] for q, a in zip(qs, answers))
    if not state["logged"]:
        tracker.log_quiz(doc["name"], len(qs), correct)
        state["logged"] = True

    st.metric("Score", f"{correct} / {len(qs)}")
    st.caption(f"{round(100 * correct / len(qs))}% correct")
    for i, (q, a) in enumerate(zip(qs, answers), start=1):
        right = q["options"][q["answer_index"]]
        ok = a == right
        with st.container(border=True):
            st.markdown(f"{'✅' if ok else '❌'} **{i}. {q['question']}**")
            st.markdown(f"Your answer: {a or '—'}")
            if not ok:
                st.markdown(f"Correct answer: **{right}**")
            st.caption(f"{q['explanation']} (page {q['page']})")
    st.button("New quiz", on_click=lambda: st.session_state.pop("quiz", None))
