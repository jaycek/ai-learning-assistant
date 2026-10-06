"""Central settings. Edit these to tune the app."""

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
NUM_CTX = 4096                 # context window requested from Ollama

EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_WORDS = 160              # MiniLM truncates at ~256 tokens, so keep chunks small
CHUNK_OVERLAP = 30
TOP_K = 5                      # chunks retrieved for "Ask my notes"

GROUP_SIZE = 6                 # chunks sent to the LLM per generation batch
MAX_ITEMS_PER_BATCH = 5        # max flashcards/questions requested per batch

WHISPER_MODEL = "base"         # tiny | base | small | medium
WHISPER_LANGUAGE = "en"        # None = auto-detect

# None = in-memory vector store (nothing is written to disk).
# Set e.g. "data/chroma_db" if you later want indexed notes to survive restarts.
PERSIST_DIR = None
