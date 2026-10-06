import config
from core import llm, vector_store
from core.batching import format_chunks

NOTES_SYSTEM = (
    "You are a study assistant answering questions about the student's own notes. Use ONLY the "
    "notes excerpts in the latest message. If the answer is not in them, reply exactly: "
    "\"I couldn't find that in your notes.\" Cite pages like (p. 3). Keep answers concise."
)

TOPIC_SYSTEM = (
    "You are a patient, knowledgeable tutor. Use your general knowledge. Start simple, then add "
    "depth; use concrete examples and analogies; use short sections. If you are unsure about a "
    "fact, say so rather than guessing."
)


def notes_answer_stream(question: str, doc_id: str, history: list[dict], model: str):
    """RAG answer grounded in one document. Returns (token_stream, source_pages)."""
    hits = vector_store.query(doc_id, question, config.TOP_K)
    pages = sorted({h["page"] for h in hits})
    messages = [
        {"role": "system", "content": NOTES_SYSTEM},
        *history[-6:],
        {"role": "user", "content": f"NOTES EXCERPTS:\n{format_chunks(hits)}\n\nQUESTION: {question}"},
    ]
    return llm.stream_chat(messages, model, temperature=0.2), pages


def topic_stream(history: list[dict], model: str, topic: str = ""):
    system = TOPIC_SYSTEM + (f" The student is currently studying: {topic}." if topic else "")
    messages = [{"role": "system", "content": system}, *history[-10:]]
    return llm.stream_chat(messages, model, temperature=0.5)
