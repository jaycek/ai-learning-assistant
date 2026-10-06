import hashlib
import io

import streamlit as st

from core import chunker, pdf_loader, vector_store


def render() -> None:
    ss = st.session_state
    st.subheader("Upload your study notes")
    files = st.file_uploader("PDF files", type="pdf", accept_multiple_files=True)

    new_doc = None
    for f in files or []:
        data = f.getvalue()
        doc_id = "doc_" + hashlib.sha256(data).hexdigest()[:16]
        if doc_id in ss.docs:
            continue
        try:
            with st.spinner(f"Indexing {f.name}…"):
                pages = pdf_loader.extract_pages(io.BytesIO(data))
                if not pages:
                    st.error(f"{f.name}: no extractable text (is it a scanned PDF?).")
                    continue
                chunks = chunker.chunk_pages(pages)
                vector_store.add_document(doc_id, chunks)
        except Exception as e:
            st.error(f"Couldn't read {f.name}: {e}")
            continue
        ss.docs[doc_id] = {"name": f.name, "pages": pages[-1]["page"], "chunks": len(chunks)}
        new_doc = doc_id

    if new_doc:
        ss["new_doc"] = new_doc  # becomes the active document on the next run
        st.rerun()

    if ss.docs:
        st.dataframe(
            [{"File": d["name"], "Pages": d["pages"], "Chunks": d["chunks"]} for d in ss.docs.values()],
            hide_index=True,
        )
        st.caption("Flashcards, quizzes and *Ask my notes* use only the active PDF chosen in the sidebar.")
    else:
        st.info("Upload a PDF to get started.")
