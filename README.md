# AI-Based Personal Learning Assistant

Local, private study helper: upload PDF notes, get flashcards / quizzes / Q&A grounded in them,
or study any topic from the model's general knowledge. Voice or text input.

## Setup
1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.1:8b`
2. Python 3.11 or 3.12:
   ```
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```
First run downloads the embedding model (all-MiniLM-L6-v2) and, on first voice use, the Whisper model.

## Notes
- No database: indexed notes live in memory, progress lives in the session. Use
  **Progress → Save progress** to export/import a JSON file.
- To keep the vector index between restarts, set `PERSIST_DIR` in `config.py`.
- Change models, chunk sizes, Whisper size, etc. in `config.py`.
