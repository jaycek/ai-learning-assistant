import random

from pydantic import BaseModel, Field

from core.batching import generate_items


class Question(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str
    page: int | None = None


class QuizSet(BaseModel):
    questions: list[Question]


def _system(difficulty: str) -> str:
    return (
        "You write multiple-choice quiz questions. Use ONLY the notes excerpt provided; never add "
        "facts from outside it. Each question has exactly 4 options with one correct answer; "
        "distractors must be plausible but wrong according to the notes. `answer_index` is the "
        "0-based index of the correct option. `explanation` is one sentence based on the notes. "
        "Set `page` to the page the answer comes from (pages are marked [Page N]). "
        f"Difficulty: {difficulty}."
    )


def generate_quiz(doc_id, n, model, difficulty="Medium", page_range=None, focus=None,
                  on_progress=None) -> list[dict]:
    items = generate_items(
        doc_id, n, model, QuizSet, _system(difficulty),
        lambda ctx, k: f"NOTES EXCERPT:\n{ctx}\n\nWrite exactly {k} multiple-choice questions.",
        "questions", page_range, focus, on_progress,
    )
    questions, seen = [], set()
    for q, pages in items:
        text = q.question.strip()
        if not text or text.lower() in seen or len(set(q.options)) < 4:
            continue
        seen.add(text.lower())
        correct = q.options[q.answer_index]
        options = q.options[:]
        random.shuffle(options)  # models tend to favour certain answer positions
        questions.append({
            "question": text,
            "options": options,
            "answer_index": options.index(correct),
            "explanation": q.explanation.strip(),
            "page": q.page if q.page in pages else pages[0],
        })
    random.shuffle(questions)
    return questions
