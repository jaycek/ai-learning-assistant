import hashlib

import streamlit as st

from core import speech


def _submit(key: str) -> None:
    ss = st.session_state
    ss[f"{key}_pending"] = ss.get(f"{key}_text", "").strip()
    ss[f"{key}_text"] = ""


def voice_chat_input(key: str, placeholder: str = "") -> str | None:
    """Mic + editable text box + Send button. Returns the submitted message, else None.

    Voice is transcribed locally (faster-whisper) into the text box so you can
    correct it before sending.
    """
    ss = st.session_state
    text_key = f"{key}_text"

    if speech.is_available() and hasattr(st, "audio_input"):
        audio = st.audio_input("🎤 Speak (optional)", key=f"{key}_audio")
        if audio is not None:
            data = audio.getvalue()
            digest = hashlib.md5(data).hexdigest()
            if ss.get(f"{key}_digest") != digest:  # transcribe each recording only once
                with st.spinner("Transcribing…"):
                    try:
                        ss[text_key] = speech.transcribe(data)
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")
                ss[f"{key}_digest"] = digest
    else:
        st.caption("Voice input unavailable: install faster-whisper and use Streamlit ≥ 1.40.")

    st.text_area("Your message", key=text_key, placeholder=placeholder, height=90)
    st.button("Send", key=f"{key}_send", type="primary", on_click=_submit, args=(key,))
    return ss.pop(f"{key}_pending", None) or None
