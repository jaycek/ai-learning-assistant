import streamlit as st

from core import tutor
from ui.voice import voice_chat_input


def _show(m: dict) -> None:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            st.caption("Sources: pages " + ", ".join(map(str, m["sources"])))


def render(doc_id, doc, model) -> None:
    if not doc:
        st.info("Upload a PDF in the Notes tab first.")
        return
    st.caption(f"Answers come only from *{doc['name']}*.")
    msgs = st.session_state.setdefault(f"ask_msgs_{doc_id}", [])

    history = st.container()
    question = voice_chat_input(f"ask_{doc_id}", "Ask a question about your notes…")

    with history:
        for m in msgs:
            _show(m)
        if question:
            msgs.append({"role": "user", "content": question})
            _show(msgs[-1])
            with st.chat_message("assistant"):
                prior = [{"role": m["role"], "content": m["content"]} for m in msgs[:-1]]
                try:
                    stream, pages = tutor.notes_answer_stream(question, doc_id, prior, model)
                    answer = st.write_stream(stream)
                    if pages:
                        st.caption("Sources: pages " + ", ".join(map(str, pages)))
                except Exception as e:
                    answer, pages = f"⚠️ {e}", []
                    st.error(str(e))
            msgs.append({"role": "assistant", "content": answer, "sources": pages})
