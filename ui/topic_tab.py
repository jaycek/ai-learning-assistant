import streamlit as st

from core import tutor
from ui.ask_tab import _show
from ui.voice import voice_chat_input


def render(model, tracker) -> None:
    st.caption("🌐 General-knowledge mode: answers come from the model's training, **not** your notes.")
    topic = st.text_input("Topic", key="topic_name", placeholder="e.g. React hooks, binary search trees").strip()
    msgs = st.session_state.setdefault("topic_msgs", [])

    c1, c2, c3, c4, c5 = st.columns(5)
    prompt = None
    if c1.button("Overview", disabled=not topic):
        prompt = f"Give me a clear overview of {topic}."
    if c2.button("Learning path", disabled=not topic):
        prompt = f"Create a step-by-step learning path for {topic}, from basics to advanced."
    if c3.button("Practice questions", disabled=not topic):
        prompt = (f"Give me 5 practice questions on {topic} of increasing difficulty. "
                  "Put the answers at the end under an 'Answers' heading.")
    if c4.button("✅ Mark learnt", disabled=not topic):
        tracker.mark_learnt(topic)
        st.toast(f"Marked '{topic}' as learnt")
    if c5.button("🗑 Clear chat"):
        msgs.clear()

    history = st.container()
    typed = voice_chat_input("topic", "Ask anything about this topic…")
    prompt = prompt or typed

    with history:
        for m in msgs:
            _show(m)
        if prompt:
            msgs.append({"role": "user", "content": prompt})
            _show(msgs[-1])
            tracker.log_topic(topic, "general")
            with st.chat_message("assistant"):
                try:
                    history_msgs = [{"role": m["role"], "content": m["content"]} for m in msgs]
                    answer = st.write_stream(tutor.topic_stream(history_msgs, model, topic))
                except Exception as e:
                    answer = f"⚠️ {e}"
                    st.error(str(e))
            msgs.append({"role": "assistant", "content": answer})
