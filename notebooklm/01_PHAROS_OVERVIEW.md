# Pharos — Project Overview

> This is file 1 of 5 providing complete context on the Pharos project for Gemini / NotebookLM. It covers *what* Pharos is, *who* it is for, and *why* it exists. Files 2–5 cover architecture, data model, ingestion/search, and API/deployment respectively.

---

## One-Sentence Definition

**Pharos is a single-tenant, production code-intelligence backend (FastAPI + PostgreSQL + pgvector) that serves structured retrieval context to a local LLM coding assistant called Ronin.**

It is sometimes referred to internally by its original codename **Neo Alexandria 2.0**. The two names refer to the same system.

---

## Who It Is For

- **Developer**: Ram Tewari (solo developer, backend-focused).
- **Primary consumer of the API**: **Ronin** — a local (desktop) LLM coding assistant that Ram is also building.
- **End-user count**: 1 (single-tenant by design). Pharos is *not* a SaaS product.

Because the consumer is a deterministic program (Ronin) rather than a human, API contracts prioritize:
- Clean JSON responses with stable keys
- Sub-second latency on retrieval endpoints
- Rich, structured metadata over prose

---

## What Pharos Does (The Two Core Use Cases)

### Use Case 1: Context Retrieval (Understanding Old Code)
Ronin receives a user query like *"How does the authentication system work in myapp-backend?"* and forwards it to Pharos at `POST /api/context/retrieve` (or `POST /api/search/advanced`). Pharos returns:
1. Semantically-ranked code chunks (retrieved via pgvector HNSW cosine similarity over `nomic-embed-text-v1` 768-dim embeddings).
2. Related entities from the knowledge graph (GraphRAG multi-hop traversal).
3. Similar implementations pattern-matched from other indexed codebases.
4. Dependency sub-graphs (IMPORTS / DEFINES / CALLS relationships).

Target latency: ~800 ms total.

### Use Case 2: Pattern Learning (Generating New Code)
When Ronin needs to generate code in the user's style, it queries Pharos for:
- Historical coding patterns extracted deterministically from the user's indexed repos.
- Prior mistakes / antipatterns.
- Canonical examples with matching AST structure, imports, and function signatures.

---

## What Pharos Is NOT

- Not a hosted SaaS. Single-tenant by design.
- Not a generic RAG / note-taking tool. The code-intelligence path is first-class; everything else (annotations, scholarly papers) is secondary.
- Not a frontend-centric project. The React frontend in `frontend/` exists but is **not a priority**. All effort goes to the backend.
- Not a place that stores raw source code. Code stays on GitHub (hybrid storage); Pharos stores metadata + AST-derived semantic summaries + embeddings.

---

## Repository Layout (Top Level)

```
pharos/
├── backend/              # Python 3.13 FastAPI backend — the primary codebase
│   ├── app/
│   │   ├── main.py           # Uvicorn/Gunicorn entrypoint (factory pattern)
│   │   ├── __init__.py       # create_app() — registers modules dynamically
│   │   ├── modules/          # 13+ vertical-slice domain modules
│   │   ├── shared/           # Cross-cutting: DB, cache, event bus, embeddings, security
│   │   ├── database/
│   │   │   └── models.py     # SINGLE SOURCE OF TRUTH for all SQLAlchemy models (~1864 lines)
│   │   ├── routers/          # Top-level routers (ingestion.py lives here)
│   │   ├── workers/          # edge.py, repo.py, combined.py — background workers
│   │   ├── services/         # Cross-module services (e.g. AdvancedSearchService)
│   │   └── config/           # settings.py
│   ├── alembic/          # DB migrations
│   ├── embed_server.py   # Standalone WSL-hosted embedding HTTP server (zero app.* imports)
│   ├── worker.py         # Entrypoint script that dispatches to app/workers/*
│   ├── render.yaml       # Render.com deployment blueprint
│   └── docs/             # Markdown documentation
├── frontend/             # React/TypeScript UI (low priority)
├── pharos-cli/           # CLI tool
├── .kiro/                # Project-config / spec directory
└── docs/                 # User-facing documentation + vision
```

**Backend is the center of gravity.** 90%+ of meaningful code lives under `backend/app/`.

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Web framework | FastAPI (async + sync routes, Pydantic v2) |
| ORM | SQLAlchemy 2.x (Mapped / mapped_column style) |
| Database (production) | PostgreSQL on NeonDB (free tier) + **pgvector** extension |
| Database (local/test) | SQLite (with FTS5 for full-text search) |
| Cache / Queue | Upstash Redis (REST + optional rediss://) |
| Embeddings (doc + query) | `nomic-ai/nomic-embed-text-v1` (768-dim) |
| Sparse embeddings | SPLADE (GPU, edge worker only) |
| Code parsing | Tree-Sitter AST (Python fully supported; JS/TS/Rust/Go/Java partial) |
| Cloud host | Render.com Starter ($7/mo) |
| Edge compute | Local machine with NVIDIA RTX 4070 GPU, exposed via Tailscale Funnel |
| Auth | JWT + OAuth2 (Google, GitHub); bearer M2M key for Ronin |
| Migrations | Alembic |
| Testing | pytest + pytest-asyncio + property-based (hypothesis) |
| Linter / formatter | ruff |

**Python version**: 3.13 (with a known Windows WMI hang issue — see file 5).

---

## Design Principles (Non-Negotiable)

1. **Zero circular dependencies between modules.** Modules communicate only via the event bus in `app/shared/event_bus.py`.
2. **Vertical slice architecture.** Each module under `app/modules/` owns its router, service, schema (Pydantic), handlers (event listeners), model re-exports, and tests.
3. **Single source of truth for DB models.** All SQLAlchemy models live in `app/database/models.py`. Module `model.py` files only *re-export* from there. This is enforced to prevent import cycles.
4. **Cost minimalism.** Full production cost target = **$7/mo** (Render Starter only; Neon + Upstash + Tailscale + local GPU are all $0).
5. **Cloud/Edge split.** Render never loads ML models. All GPU work (embeddings, SPLADE, LLM extraction) happens on the local RTX 4070 and is reached via Tailscale Funnel or the Upstash task queue.
6. **Hybrid storage for code.** Source files stay on GitHub; Pharos stores only metadata + chunk-level semantic summaries + embeddings. `document_chunks.content` is **nullable** for code chunks — the content lives at the `github_uri` in chunk_metadata.

---

## Production URLs and Key Constants

- **Cloud API (actual URL)**: `https://pharos-cloud-api.onrender.com`
  - Note: `render.yaml` declares `name: pharos-api` but the *deployed* service is `pharos-cloud-api`. The YAML name is stale.
- **Health check**: `GET /health`
- **OpenAPI / Swagger**: `GET /docs`
- **M2M auth header (Ronin → Pharos)**: `Authorization: Bearer <PHAROS_API_KEY>`
- **Embedding model**: `nomic-ai/nomic-embed-text-v1` → 768-dim vectors
- **Edge embed server port**: `8001` (WSL2), exposed publicly via Tailscale Funnel at a URL like `https://pc.tailf7b210.ts.net`
- **Redis queues**: `pharos:tasks` (embedding tasks, polled by edge worker), `ingest_queue` (repo ingestion — currently has no worker consuming it).

---

## Project Status Snapshot (2026-04-24)

- ✅ Backend deployed to Render, serving production traffic.
- ✅ pgvector search working end-to-end (with a recent fix: now embeds `semantic_summary` rather than the full JSON blob for code chunks).
- ✅ Windows-path-to-POSIX normalization in `github_uri` fixed.
- ✅ Non-SHA refs rewritten to `HEAD` so `raw.githubusercontent.com` resolves to default branch.
- ✅ Test-file path penalty (+0.10 distance) applied to down-rank `/tests/` hits.
- ⚠️ Repo worker (`backend/app/workers/repo.py`) exists as a file but the GitHub repo-ingestion path via `ingest_queue` is not fully wired — see file 4 for the *actual* working pipeline vs. the documented-but-broken one.
- ❌ Frontend is essentially dormant.

---

## Glossary

- **Ronin** — The local LLM desktop assistant that consumes the Pharos API. Separate project from Pharos, but co-developed by the same person.
- **Neo Alexandria** — Original codename for Pharos. Still appears in docstrings.
- **Edge worker** — Process running on Ram's local RTX 4070 that handles all GPU-bound work (embeddings, sparse embeddings, LLM extraction). Polls `pharos:tasks` from Upstash.
- **Cloud API** — The FastAPI process on Render. Serves HTTP; never loads ML models (`MODE=CLOUD` skips torch imports).
- **Hybrid storage** — Pattern where code files stay on GitHub and Pharos stores only the pointer (`github_uri`, `branch_reference`) plus derived metadata.
- **Semantic summary** — A short, human-readable string like `"[python] def authenticate_user(username, password) -> User: 'Authenticate a user.' deps: [verify_password, db.query]"`. This is what gets embedded for code chunks — **not** the raw source.
- **DocumentChunk** — A retrievable unit. For PDFs it's a page-ish slice with `content` populated. For code it's a function/class/method with `content=NULL` and a `github_uri` pointing at the source.
- **Three-way hybrid search** — Search strategy combining keyword (FTS5/tsvector) + dense vector (pgvector) + sparse (SPLADE) results via Reciprocal Rank Fusion (RRF).
