# Not Your Therapist 🧠
[日本語](./README.ja.md)

> **An AI therapist-style chatbot that is very explicitly *not* your therapist.**

Not Your Therapist is a small full-stack experiment built with **React, FastAPI, LangChain, LangGraph, and Ollama**.

It is intended as a locally runnable conversational AI experiment, not a medical or mental-health service.

## ⚠️ Disclaimer

**Not Your Therapist is not a therapist, doctor, psychologist, counselor, or medical service.**

Do not use it for diagnosis, treatment, crisis support, or professional mental-health decisions. If you are experiencing an emergency or believe you may be in immediate danger, contact your local emergency service or a qualified professional.

## Architecture

```text
┌──────────────────────┐
│      React + Vite    │
│      Frontend        │
└──────────┬───────────┘
           │ HTTP / SSE
           ▼
┌──────────────────────┐
│       FastAPI        │
│       Backend        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ LangChain / LangGraph│
│    Agent Services    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Ollama         │
│   Local LLM runtime  │
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│ SQLite / Checkpoints │
└──────────────────────┘
```

## Technology

* **Frontend:** React 19 + Vite
* **Backend:** Python 3.11+ + FastAPI
* **AI orchestration:** LangChain + LangGraph
* **LLM runtime:** Ollama
* **Persistence:** SQLite + SQLAlchemy / aiosqlite
* **Streaming:** Server-Sent Events (SSE)
* **Testing:** pytest + pytest-asyncio

The backend project defines FastAPI, LangChain, LangGraph checkpointing, LangChain-Ollama, SQLAlchemy, SQLite-related dependencies, and Uvicorn.

## Project Structure

```text
not-your-therapist/
├── backend/
│   ├── app/
│   │   ├── agent_services/
│   │   ├── repository/
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── sse_helper.py
│   ├── tests/
│   ├── main.py
│   ├── pyproject.toml
│   └── .env.example
│
└── not-your-therapist/
    ├── src/
    ├── package.json
    └── vite.config.*
```

## Prerequisites

* Python **3.11+**
* Node.js and npm
* Ollama
* An Ollama model suitable for your machine

## Getting Started

### 1. Clone

```bash
git clone https://github.com/ashishwebt/not-your-therapist.git
cd not-your-therapist
```

### 2. Start Ollama

Install and start Ollama, then pull the model you want to use.

For example:

```bash
ollama pull llama3.2
```

Use the model configured by the application if it differs from this example.

### 3. Configure the backend

```bash
cd backend
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The supplied configuration uses:

```env
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./chat.db
ENVIRONMENT=development
```

### 4. Install dependencies

The backend includes a `uv.lock`, so `uv` is the recommended development workflow:

```bash
uv sync
```

### 5. Run the API

From `backend/`:

```bash
uv run uvicorn main:app --reload
```

The API should be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 6. Run the frontend

In another terminal:

```bash
cd not-your-therapist
npm install
npm run dev
```

Open the URL printed by Vite, normally:

```text
http://localhost:5173
```

## Testing

Run the backend tests with:

```bash
cd backend
uv run pytest
```

The repository contains tests covering repositories, routes, and schemas.

## Frontend Build

```bash
cd not-your-therapist
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Configuration

| Variable          | Description             | Default                  |
| ----------------- | ----------------------- | ------------------------ |
| `OLLAMA_BASE_URL` | Ollama server URL       | `http://localhost:11434` |
| `DATABASE_URL`    | Database connection     | `sqlite:///./chat.db`    |
| `ENVIRONMENT`     | Application environment | `development`            |

## Why the Name?

Because calling an AI chatbot **"Your Therapist"** would be a spectacularly bad product decision.

So this one tells you the truth:

**It's not your therapist.**

## Development Status

This is an experimental project. The architecture, agent behaviour, UI, and APIs may change as the project evolves.

Contributions and ideas are welcome.

## License

See [LICENSE](LICENSE) for license information.
