# RakGPT

An agentic, ChatGPT-style assistant built with FastAPI and LangGraph. It streams answers in real time, searches the web, answers questions about your uploaded documents (RAG), and keeps long-term memory across conversations.

## Features

- **Agent with tools.** A LangGraph agent decides when to call a tool: web search, document search, memory, or a calculator.
- **Web search.** Up-to-date answers through [Tavily](https://tavily.com).
- **Document Q&A (RAG).** Upload PDF, DOCX, TXT, MD, PY or CSV files and ask questions about them. Chunks are embedded and stored in ChromaDB, scoped per conversation.
- **Long-term memory.** The agent can save and recall facts about the user.
- **Multiple models.** Switch between Google Gemini and Groq-hosted models from the UI.
- **Persistent conversations.** Chat history and agent checkpoints are stored in SQLite.
- **Streaming responses** over Server-Sent Events.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI, Uvicorn |
| Agent | LangChain, LangGraph |
| LLM providers | Google Gemini, Groq |
| Vector store | ChromaDB, Gemini embeddings |
| Database | SQLite, SQLAlchemy |
| Web search | Tavily |
| Frontend | Vanilla HTML, CSS and JavaScript |

## Project structure

```
RakGPT/
├── app/
│   ├── main.py              # App entry point, registers routers
│   ├── config.py            # Paths, models, environment settings
│   ├── api/
│   │   ├── chat.py          # POST /chat/stream (SSE)
│   │   ├── conversations.py # GET /conversations, /history/{thread_id}
│   │   └── documents.py     # POST /upload
│   ├── agent/
│   │   ├── graph.py         # LLM factory and LangGraph agent
│   │   ├── tools.py         # Agent tools
│   │   └── prompts.py       # System prompt
│   ├── services/
│   │   ├── rag.py           # Document ingestion and retrieval
│   │   └── streaming.py     # SSE helpers and chunk filtering
│   └── db/
│       ├── session.py       # Engine and session factory
│       ├── models.py        # SQLAlchemy models
│       └── repository.py    # Data access functions
├── static/                  # CSS and JavaScript
├── templates/index.html     # Chat UI
├── data/                    # SQLite databases (created at runtime)
├── chroma_db/               # Vector store (created at runtime)
├── uploads/                 # Uploaded files (created at runtime)
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.11
- [Conda](https://docs.conda.io) (or any virtual environment manager)
- API keys, see [Configuration](#configuration)

### Installation

```bash
git clone https://github.com/MamitianaRak/RakGPT.git
cd RakGPT

conda create -n rakgpt python=3.11 -y
conda activate rakgpt

pip install -r requirements.txt
```

### Configuration

Create a `.env` file at the project root:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional, defaults to openai/gpt-oss-120b
# DEFAULT_MODEL=openai/gpt-oss-120b
```

| Variable | Required | Used for |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Yes | Gemini models and document embeddings |
| `GROQ_API_KEY` | For Groq models | Groq-hosted models |
| `TAVILY_API_KEY` | For web search | The web search tool |
| `DEFAULT_MODEL` | No | Model used when none is selected |

The `.env` file is ignored by git. Never commit your keys.

### Run

```bash
python -m app.main
```

Or with Uvicorn directly:

```bash
uvicorn app.main:app --reload --port 8080
```

Then open <http://localhost:8080>.

## Available models

| Provider | Models |
| --- | --- |
| Groq | `openai/gpt-oss-120b` (default), `openai/gpt-oss-20b`, `qwen/qwen3.8-27b` |
| Google | `gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.1-pro-preview`, `gemini-2.5-pro` |

Model availability and free-tier quotas depend on your provider account. To add or remove a model, edit `MODEL_PROVIDERS` in [app/config.py](app/config.py) and the model selector in [templates/index.html](templates/index.html).

## Agent tools

| Tool | Purpose |
| --- | --- |
| `web_search` | Search the web with Tavily for current information |
| `search_uploaded_documents` | Retrieve relevant chunks from documents uploaded in the current conversation |
| `remember_this` | Save a fact or preference to long-term memory |
| `recall_memory` | Read saved memories |
| `calculator` | Evaluate math expressions |

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Chat UI |
| `POST` | `/chat/stream` | Send a message, receive the answer as an SSE stream |
| `GET` | `/conversations` | List conversations |
| `GET` | `/history/{thread_id}` | Get the messages of a conversation |
| `POST` | `/upload` | Upload a document (multipart form: `file`, `thread_id`) |

Example request body for `/chat/stream`:

```json
{
  "message": "Summarize the document I uploaded",
  "thread_id": "my-conversation-id",
  "model": "openai/gpt-oss-120b"
}
```

The stream sends `data: {"token": "..."}` events, then `data: {"done": true}`. On failure it sends `data: {"error": "..."}`.

## Known limitations

This project is a solid base for development, but it is not production-ready yet:

- The current `thread_id` used by the tools is a module-level global, so simultaneous requests from different users can interfere with each other.
- There is no authentication. Conversations are identified only by the `thread_id` sent by the client.
- SQLite, the local ChromaDB store and local file uploads suit a single instance, not a multi-worker or multi-server deployment.
- Switching models in the middle of a conversation that already used tools may fail with some providers. Start a new chat if that happens.

## License

Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
