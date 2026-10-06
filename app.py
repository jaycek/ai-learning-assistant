import streamlit as st

import config
from core import llm
from core.tracker import Tracker
from ui import ask_tab, flashcards_tab, notes_tab, progress_tab, quiz_tab, topic_tab

st.set_page_config(page_title="Learning Assistant", page_icon="🎓", layout="wide")

ss = st.session_state
ss.setdefault("docs", {})            # doc_id -> {name, pages, chunks}
ss.setdefault("tracker", Tracker())  # in-memory progress (no database)
if "new_doc" in ss:                  # make a freshly uploaded PDF the active one
    ss["active_doc"] = ss.pop("new_doc")


@st.cache_data(ttl=10, show_spinner=False)
def available_models() -> list[str]:
    return llm.list_models()


with st.sidebar:
    st.title("🎓 Learning Assistant")
    models = available_models()
    if models:
        default = models.index(config.DEFAULT_MODEL) if config.DEFAULT_MODEL in models else 0
        model = st.selectbox("Ollama model", models, index=default)
    else:
        st.error("Can't reach Ollama or no models are installed.\n\n"
                 f"Start it, then run: `ollama pull {config.DEFAULT_MODEL}`")
        model = st.text_input("Model name", config.DEFAULT_MODEL)

    doc_id = None
    if ss.docs:
        doc_id = st.selectbox("Active notes", list(ss.docs), key="active_doc",
                              format_func=lambda d: ss.docs[d]["name"])
    st.caption("Notes mode uses only your PDF. Topic Tutor uses the model's own knowledge.")

doc = ss.docs.get(doc_id)

tabs = st.tabs(["📄 Notes", "🃏 Flashcards", "📝 Quiz", "💬 Ask my notes", "🎓 Topic Tutor", "📈 Progress"])
with tabs[0]:
    notes_tab.render()
with tabs[1]:
    flashcards_tab.render(doc_id, doc, model, ss.tracker)
with tabs[2]:
    quiz_tab.render(doc_id, doc, model, ss.tracker)
with tabs[3]:
    ask_tab.render(doc_id, doc, model)
with tabs[4]:
    topic_tab.render(model, ss.tracker)
with tabs[5]:
    progress_tab.render(ss.tracker)
