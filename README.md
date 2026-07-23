# ai-learning-lab

Personal lab for becoming an AI engineer (GenAI apps & agents).

**Path:** `/Users/adeljerbi/Projects/ai-learning-lab`  
**Stack:** Python 3.11 · Ollama (local LLM) · OpenAI API · Postgres + pgvector  

**Goal:**  design, build, evaluate, and ship an agentic app with tools + RAG.

---

## Prerequisites

- Python **3.11**
- [Ollama](https://ollama.com)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Postgres + pgvector)
- An [OpenAI API key](https://platform.openai.com/api-keys) (for cloud smoke tests and most course notebooks)
- Cursor (or any editor)

---

## Quick start

```bash
cd /Users/adeljerbi/Projects/ai-learning-lab
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

Never commit `.env`. It is listed in `.gitignore`.

---

## Environment variables

Copy from `.env.example`:

| Variable | Purpose |
|----------|---------|
| `OLLAMA_BASE_URL` | OpenAI-compatible Ollama endpoint (default `http://localhost:11434/v1`) |
| `OLLAMA_MODEL` | Local model name (default `llama3.2`) |
| `OPENAI_API_KEY` | Cloud OpenAI key (required for `smoke_openai.py`) |
| `ANTHROPIC_API_KEY` | Optional; for later multi-provider practice |
| `DATABASE_URL` | Postgres connection string |

---

## 1. Ollama (local LLM)

```bash
# Install Ollama, then:
ollama pull llama3.2
ollama run llama3.2 "Say hello in one word"
```

Python check (OpenAI-compatible client):

```bash
python smoke_ollama.py
```

Expected: a short reply (e.g. `Hello`).

---

## 2. OpenAI (cloud LLM)

1. Create a key at https://platform.openai.com/api-keys
2. Put it in `.env`: `OPENAI_API_KEY=sk-...`
3. Run:

```bash
python smoke_openai.py
```

Uses `gpt-4o-mini` for a cheap one-word smoke test.

---

## 3. Docker (Postgres + pgvector)

This repo uses Docker Compose for the vector database only (not the Python app yet).

```bash
docker compose up -d
python smoke_pgvector.py
```

On first start, `docker/init-vector.sql` enables the `vector` extension automatically.

Connection string (same as `.env.example`):

`postgresql://ai:ai@localhost:5432/ai_learning`

Useful commands:

```bash
docker compose ps
docker compose stop          # keeps data
docker compose start
docker compose down -v       # wipe DB data (careful)
```

If you previously created a container with `docker run --name ai-pgvector`, remove it first:

```bash
docker rm -f ai-pgvector
```

---

## Smoke tests

| Script | Checks |
|--------|--------|
| `smoke_ollama.py` | Local LLM via OpenAI-compatible API |
| `smoke_openai.py` | Cloud OpenAI chat completion |
| `smoke_pgvector.py` | Postgres connection + `vector` extension |

---

## Security

- Do **not** commit API keys or `.env`
- Prefer cheap models (`gpt-4o-mini`, small Ollama models) for experiments
- Rotate keys if they ever leak into Git history
