# SafeX Solutions RAG Chatbot

Production-grade RAG-powered customer support chatbot for SafeX Solutions.

## Architecture

- **Backend**: FastAPI
- **RAG & Vector Store**: LangChain + PostgreSQL (pgvector) + `sentence-transformers` (local embeddings)
- **Local LLM**: Ollama (`phi3:mini` or `llama3.1:8b`)
- **Memory**: PostgreSQL (windowed, session-based)
- **Escalation Flow**: Meta WhatsApp Cloud API via n8n
- **Self-Optimizing FAQs**: K-Means clustering batch job + LLM synthesis
- **Admin Dashboard**: Streamlit
- **Frontend Widget**: React (Vite)

## Setup

1. Copy `.env.example` to `.env` and fill in the required variables (especially secrets).
2. Install Ollama on your host and pull the required model:
   ```bash
   ollama pull phi3:mini
   ```
3. Start the infrastructure (Postgres, Redis, n8n, etc.):
   ```bash
   docker-compose up -d
   ```
4. Run the backend (requires Python 3.10+):
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
5. Run the Admin Dashboard:
   ```bash
   cd admin-dashboard
   pip install streamlit requests
   streamlit run app.py
   ```
6. Run the Frontend Widget:
   ```bash
   cd frontend-widget
   npm install
   npm run dev
   ```

## Webhook Exposure

During development, you can use `ngrok` to expose your local ports (e.g., port 8000 for FastAPI to receive n8n callbacks, and port 5678 for n8n to receive Meta WhatsApp webhooks).

```bash
ngrok http 5678
```

Update your `.env` with the ngrok URLs accordingly.
