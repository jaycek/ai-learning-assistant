from typing import Iterator, Type, TypeVar

import ollama
from pydantic import BaseModel, ValidationError

import config

T = TypeVar("T", bound=BaseModel)


def _client() -> ollama.Client:
    return ollama.Client(host=config.OLLAMA_HOST)


def list_models() -> list[str]:
    try:
        return sorted(m.model for m in _client().list().models)
    except Exception:
        return []


def stream_chat(messages: list[dict], model: str, temperature: float = 0.4) -> Iterator[str]:
    options = {"temperature": temperature, "num_ctx": config.NUM_CTX}
    for part in _client().chat(model=model, messages=messages, stream=True, options=options):
        yield part.message.content or ""


def generate_structured(prompt: str, schema: Type[T], model: str,
                        system: str | None = None, retries: int = 2) -> T:
    """Ask Ollama for JSON matching a Pydantic schema; validate and retry on failure."""
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    last_error = None
    for _ in range(retries + 1):
        resp = _client().chat(
            model=model,
            messages=messages,
            format=schema.model_json_schema(),
            options={"temperature": 0.3, "num_ctx": config.NUM_CTX},
        )
        try:
            return schema.model_validate_json(resp.message.content)
        except ValidationError as e:
            last_error = e
    raise ValueError(f"Model returned invalid JSON after {retries + 1} attempts: {last_error}")
