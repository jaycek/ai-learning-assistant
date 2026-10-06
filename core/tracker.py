"""In-memory progress tracking. Lives in st.session_state; export/import as JSON to keep it."""
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Tracker:
    topics: dict = field(default_factory=dict)       # name -> info
    quizzes: list = field(default_factory=list)
    flashcards: list = field(default_factory=list)

    def log_topic(self, name: str, source: str) -> None:
        name = name.strip()
        if not name:
            return
        t = self.topics.setdefault(
            name, {"source": source, "first_studied": _now(), "interactions": 0, "learnt": False})
        t["interactions"] += 1
        t["last_studied"] = _now()

    def mark_learnt(self, name: str, source: str = "general") -> None:
        self.log_topic(name, source)
        if name.strip():
            self.topics[name.strip()]["learnt"] = True

    def log_quiz(self, source: str, total: int, correct: int) -> None:
        self.log_topic(source, "notes")
        self.quizzes.append({"topic": source, "total": total, "correct": correct,
                             "pct": round(100 * correct / total) if total else 0, "at": _now()})

    def log_flashcards(self, source: str, known: int, total: int) -> None:
        self.log_topic(source, "notes")
        self.flashcards.append({"topic": source, "known": known, "total": total, "at": _now()})

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Tracker":
        data = json.loads(text)
        return cls(topics=data.get("topics", {}), quizzes=data.get("quizzes", []),
                   flashcards=data.get("flashcards", []))
