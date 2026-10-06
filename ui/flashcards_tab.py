import streamlit as st

from core import flashcards
from ui.common import scope_controls


def _new_session(doc_id, cards, review=False, note=""):
    return {"doc_id": doc_id, "cards": cards, "i": 0, "revealed": False,
            "known": [], "missed": [], "review": review, "logged": review, "note": note}


def _reveal():
    st.session_state.fc["revealed"] = True


def _mark(known: bool):
    fc = st.session_state.fc
    (fc["known"] if known else fc["missed"]).append(fc["cards"][fc["i"]])
    fc["i"] += 1
    fc["revealed"] = False


def _review_missed():
    fc = st.session_state.fc
    st.session_state.fc = _new_session(fc["doc_id"], fc["missed"], review=True)


def render(doc_id, doc, model, tracker) -> None:
    if not doc:
        st.info("Upload a PDF in the Notes tab first.")
        return
    st.caption(f"Flashcards are generated **only** from *{doc['name']}*.")
    n = st.number_input("Number of flashcards", 1, 50, 10, key="fc_n")
    page_range, focus = scope_controls(doc, "fc")

    if st.button("Generate flashcards", type="primary"):
        bar = st.progress(0.0, text="Generating flashcards…")
        try:
            cards = flashcards.generate_cards(
                doc_id, int(n), model, page_range, focus,
                lambda p: bar.progress(p, text="Generating flashcards…"))
        except Exception as e:
            bar.empty()
            st.error(str(e))
        else:
            bar.empty()
            if not cards:
                st.error("No usable cards were produced. Try a different scope or model.")
            else:
                note = f"Generated {len(cards)} of {int(n)} requested." if len(cards) < n else ""
                st.session_state.fc = _new_session(doc_id, cards, note=note)

    fc = st.session_state.get("fc")
    if fc and fc["doc_id"] == doc_id:
        _study(fc, doc, tracker)


def _study(fc, doc, tracker) -> None:
    st.divider()
    total = len(fc["cards"])
    if fc["note"]:
        st.caption(fc["note"])

    if fc["i"] >= total:
        known, missed = len(fc["known"]), len(fc["missed"])
        if not fc["logged"]:
            tracker.log_flashcards(doc["name"], known, total)
            fc["logged"] = True
        st.success(f"Deck complete: you knew {known} of {total}.")
        if missed:
            st.button(f"Review {missed} missed card(s)", on_click=_review_missed)
        return

    card = fc["cards"][fc["i"]]
    st.progress(fc["i"] / total, text=f"Card {fc['i'] + 1} of {total}")
    with st.container(border=True):
        st.markdown(f"### {card['front']}")
        if fc["revealed"]:
            st.markdown(card["back"])
            st.caption(f"Source: page {card['page']}")

    if not fc["revealed"]:
        st.button("Show answer", on_click=_reveal, type="primary")
    else:
        c1, c2 = st.columns(2)
        c1.button("✅ Knew it", on_click=_mark, args=(True,))
        c2.button("❌ Missed it", on_click=_mark, args=(False,))
