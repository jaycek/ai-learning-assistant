from pydantic import BaseModel

from core.batching import generate_items


class Card(BaseModel):
    front: str
    back: str
    page: int | None = None


class CardSet(BaseModel):
    cards: list[Card]


SYSTEM = (
    "You write study flashcards. Use ONLY the notes excerpt provided; never add facts from "
    "outside it. Each card has a short question or term on the front and a clear, "
    "self-contained answer (1-3 sentences) on the back. Cover distinct ideas, avoid duplicates, "
    "and skip anything the excerpt does not cover. Set `page` to the page number the answer "
    "comes from (pages are marked [Page N])."
)


def generate_cards(doc_id, n, model, page_range=None, focus=None, on_progress=None) -> list[dict]:
    items = generate_items(
        doc_id, n, model, CardSet, SYSTEM,
        lambda ctx, k: f"NOTES EXCERPT:\n{ctx}\n\nWrite exactly {k} flashcards from this excerpt.",
        "cards", page_range, focus, on_progress,
    )
    cards, seen = [], set()
    for c, pages in items:
        front, back = c.front.strip(), c.back.strip()
        if not front or not back or front.lower() in seen:
            continue
        seen.add(front.lower())
        cards.append({"front": front, "back": back,
                      "page": c.page if c.page in pages else pages[0]})
    return cards
