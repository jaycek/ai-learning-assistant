import io
from functools import lru_cache

import config


def is_available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


@lru_cache(maxsize=1)
def _model():
    from faster_whisper import WhisperModel
    return WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")


def transcribe(audio_bytes: bytes) -> str:
    segments, _ = _model().transcribe(
        io.BytesIO(audio_bytes), language=config.WHISPER_LANGUAGE, vad_filter=True
    )
    return " ".join(s.text.strip() for s in segments).strip()
