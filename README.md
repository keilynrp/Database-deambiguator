<div align="center">

# UKIP

**Universal Knowledge Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://react.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-ff6b35?style=for-the-badge)](https://www.trychroma.com/)
[![Tests](https://img.shields.io/badge/Tests-470%20passing-brightgreen?style=for-the-badge)](backend/tests/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](LICENSE)

A domain-agnostic intelligence platform that ingests raw data, harmonizes it, enriches it against global knowledge bases, runs OLAP analytics and stochastic simulations, and lets you query everything through a RAG-powered AI assistant.

[Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [API](#api-overview) · [Roadmap](#roadmap) · [Strategic Vision](docs/EVOLUTION_STRATEGY.md)

</div>

---

## Why UKIP?

Most data platforms force you to choose: clean your data **or** analyze it. UKIP does both in a single pipeline. It started as a catalog deduplication tool and evolved into a full research intelligence engine across 19 development sprints.

**What it does:**

1. **Ingest** any structured data (Excel, CSV, JSON-LD, XML, BibTeX, RIS, Parquet).
2. **Harmonize** messy records with fuzzy matching, authority resolution against 5 global knowledge bases (Wikidata, VIAF, ORCID, DBpedia, OpenAlex), and bulk normalization rules.
3. **Enrich** every record against academic APIs (OpenAlex, Google Scholar, Web of Science).
4. **Analyze** with OLAP cubes (DuckDB), Monte Carlo simulations, topic modeling, and correlation analysis.
5. **Query** your entire dataset in natural language through a RAG assistant powered by any LLM provider.

### Design Philosophy

One rule: **Justified Complexity** ([details](docs/ARCHITECTURE.md)).

- Monorepo (FastAPI + Next.js). No microservices until proven necessary.
- If a dictionary solves it, we use a dictionary.
- Accessible for beginners, robust for production data tasks.

---

## Features

### Data Operations
- **Entity Catalog** — Browse, search, inline-edit, and delete records across any domain. Dynamic pagination, structured identifier fields.
- **Multi-format Import/Export** — Excel, CSV, JSON, XML. Drag-and-drop pre-analyzer for JSON-LD, RDF, Parquet, BibTeX, RIS.
- **Domain Registry** — Define custom schemas (Science, Healthcare, Business, or your own) with YAML-based configurations.

### Data Quality
- **Fuzzy Disambiguation** — `token_sort_ratio` + Levenshtein grouping of typos, casings, and synonyms.
- **Authority Resolution Layer** — Resolve entities against Wikidata, VIAF, ORCID, DBpedia, and OpenAlex. Weighted scoring engine ranks candidates by confidence. Batch resolution with review queue for bulk confirm/reject workflows.
- **Harmonization Pipeline** — Multi-step normalization with undo/redo history and change tracking.

### Analytics
- **OLAP Cube Explorer** — DuckDB-powered multi-dimensional queries with drill-down navigation and Excel pivot export.
- **Monte Carlo Projections** — Geometric Brownian Motion model simulates 5,000 citation trajectories per record. Interactive area charts.
- **Topic Modeling** — LDA-based topic extraction with co-occurrence networks and cluster analysis.
- **Correlation Analysis** — Multi-variable statistical analysis across catalog fields.

### Scientometric Enrichment
Three-phase cascading enrichment worker:

| Phase | Source | Access |
|-------|--------|--------|
| 1 | [OpenAlex](https://openalex.org/) | Free (polite `mailto:` mode) |
| 2 | Google Scholar | Scraping via rotating proxies |
| 3 | [Web of Science](https://clarivate.com/) | BYOK (institutional API key) |

### Semantic RAG Assistant
- **6 LLM providers** with BYOK support:

  | Provider | Models |
  |----------|--------|
  | OpenAI | gpt-4o, gpt-4o-mini |
  | Anthropic | claude-3.5-sonnet, claude-3-haiku |
  | DeepSeek | deepseek-chat, deepseek-reasoner |
  | xAI | grok-3, grok-3-mini |
  | Google | gemini-2.0-flash, gemini-pro |
  | Local | Any Ollama/vLLM model (free) |

- **ChromaDB** vector store with OpenAI or local `all-MiniLM-L6-v2` embeddings.
- Natural language queries return grounded, source-attributed answers with similarity scores.

### Security
- **JWT authentication** with bcrypt password hashing.
- **Role-based access control** — `super_admin`, `admin`, `editor`, `viewer`.
- **Account lockout** after failed login attempts.
- **AES encryption** for sensitive data at rest.
- **Circuit breaker** pattern for external API resilience.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **API** | Python 3.10+, FastAPI, SQLAlchemy ORM |
| **Database** | SQLite (OLTP), DuckDB (OLAP cubes), ChromaDB (vectors) |
| **Matching** | thefuzz + python-Levenshtein |
| **Enrichment** | openalex-py, scholarly, httpx |
| **Analytics** | numpy, scipy, DuckDB SQL (CUBE/ROLLUP/GROUPING SETS) |
| **NLP** | LDA topic modeling, sentence-transformers |
| **AI/RAG** | openai, anthropic, ChromaDB, sentence-transformers |
| **Frontend** | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4, Recharts |

---

## Quick Start

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)

### 1. Clone and install

```bash
git clone https://github.com/keilynrp/universal-knowledge-intelligence-platform.git
cd universal-knowledge-intelligence-platform
```

### 2. Backend

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --reload
```

API at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3004`

### 4. (Optional) Configure providers

- **AI Assistant**: Go to **Integrations > AI Language Models** and add your API key. For zero-cost: install [Ollama](https://ollama.ai) and point to `http://localhost:11434/v1`.
- **Web of Science**: Set `WOS_API_KEY` as environment variable.

### 5. Run tests

```bash
python -m pytest backend/tests/ -x -q
# 470 tests, all passing
```

---

## Architecture

```mermaid
graph TD
    A[Excel / CSV / JSON-LD] -->|Import| B[(SQLite DB)]
    B --> C{Disambiguation}
    C -->|Fuzzy Match| D[Authority Resolution]
    D -->|Wikidata, VIAF, ORCID, DBpedia, OpenAlex| E[Review Queue]
    E -->|Confirm / Reject| F[Normalization Rules]
    F -->|Apply Bulk| B

    B -->|Queued Records| H[Enrichment Worker]
    H -->|Phase 1| I[OpenAlex]
    H -->|Phase 2| J[Google Scholar]
    H -->|Phase 3| K[Web of Science]
    I & J & K --> B

    B -->|Star Schema| OLAP[(DuckDB Cubes)]
    OLAP --> AN[OLAP Explorer]
    B -->|Citation Data| MC[Monte Carlo Engine]
    MC --> AN
    B --> TM[Topic Modeling]
    TM --> AN

    B -->|Enriched Text| VDB[(ChromaDB)]
    VDB -->|Retrieval| RAG[RAG Engine]
    LLM[LLM Provider] --> RAG
    RAG --> CHAT[AI Chat]

    B -->|Export| G[Excel / CSV / JSON / XML]

    classDef db fill:#f9f,color:#000,stroke:#333,stroke-width:2px;
    class B,VDB,OLAP db;
    classDef api fill:#ffd700,color:#000,stroke:#333,stroke-width:2px;
    class I,J,K api;
    classDef ai fill:#c7d2fe,color:#1e1b4b,stroke:#818cf8,stroke-width:2px;
    class RAG,LLM,CHAT ai;
    classDef analytics fill:#bbf7d0,color:#14532d,stroke:#4ade80,stroke-width:2px;
    class MC,AN,TM analytics;
```

---

## API Overview

86 endpoints across 12 functional groups. Full interactive docs at `/docs` (Swagger) or `/redoc`.

### Authentication & Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/token` | Login (OAuth2 password flow) |
| `GET` | `/users/me` | Current user profile |
| `POST` | `/users` | Create user (admin) |
| `POST` | `/users/me/password` | Change password |

### Entity Catalog
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/entities` | List entities (search, pagination, filters) |
| `POST` | `/upload` | Import file (Excel, CSV) |
| `GET` | `/stats` | Aggregated system statistics |
| `GET` | `/export` | Export data (CSV, Excel, JSON, XML) |

### Domains & Schema Registry
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/domains` | List available domains |
| `POST` | `/domains` | Create custom domain schema |
| `GET` | `/domains/{id}` | Get domain details |

### Disambiguation & Harmonization
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/disambiguate/{field}` | Fuzzy-match groups for a field |
| `POST` | `/harmonization/apply` | Apply harmonization step |
| `POST` | `/harmonization/undo` | Undo last harmonization |
| `POST` | `/rules/apply` | Apply normalization rules |

### Authority Resolution
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/authority/resolve` | Resolve value against authority sources |
| `POST` | `/authority/resolve/batch` | Batch resolve multiple values |
| `GET` | `/authority/queue/summary` | Review queue summary (pending/confirmed/rejected) |
| `POST` | `/authority/records/bulk-confirm` | Bulk confirm authority records |
| `POST` | `/authority/records/bulk-reject` | Bulk reject authority records |

### OLAP & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/cube/dimensions/{domain}` | Available OLAP dimensions |
| `POST` | `/cube/query` | Multi-dimensional cube query |
| `POST` | `/cube/export` | Export pivot table to Excel |
| `GET` | `/analyzers/topics/{domain}` | Topic modeling analysis |
| `GET` | `/analyzers/correlation/{domain}` | Correlation analysis |

### Scientometric Enrichment
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/enrich/bulk` | Queue bulk enrichment |
| `GET` | `/enrich/stats` | Enrichment KPIs and concept cloud |
| `GET` | `/enrich/montecarlo/{id}` | Monte Carlo 5-year projection |

### Semantic RAG
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rag/index` | Vectorize catalog into ChromaDB |
| `POST` | `/rag/query` | Natural language query |
| `GET` | `/rag/stats` | Vector store statistics |

### AI Provider Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ai-integrations` | List configured LLM providers |
| `POST` | `/ai-integrations` | Add provider (BYOK) |
| `POST` | `/ai-integrations/{id}/activate` | Set active RAG provider |

---

## Project Structure

<details>
<summary>Click to expand</summary>

```
ukip/
├── backend/
│   ├── adapters/
│   │   ├── enrichment/           # OpenAlex, Scholar, WoS adapters
│   │   └── llm/                  # OpenAI, Anthropic, Local LLM adapters
│   ├── analytics/
│   │   ├── montecarlo.py         # Stochastic citation projections
│   │   ├── rag_engine.py         # RAG orchestration (index + query)
│   │   └── vector_store.py       # ChromaDB vector store
│   ├── analyzers/
│   │   ├── topic_modeling.py     # LDA topic extraction
│   │   └── correlation.py        # Multi-variable statistical analysis
│   ├── authority/
│   │   ├── resolver.py           # Parallel authority resolution engine
│   │   ├── scoring.py            # Weighted scoring & evidence
│   │   └── resolvers/            # Wikidata, VIAF, ORCID, DBpedia, OpenAlex
│   ├── domains/
│   │   ├── default.yaml          # Universal catalog schema
│   │   ├── science.yaml          # Scientific domain
│   │   └── healthcare.yaml       # Healthcare domain
│   ├── tests/                    # 470 tests across 26 files
│   ├── auth.py                   # JWT + RBAC + lockout
│   ├── circuit_breaker.py        # External API resilience
│   ├── encryption.py             # AES encryption utilities
│   ├── main.py                   # FastAPI app (86 endpoints)
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── olap.py                   # DuckDB OLAP engine
│   └── schema_registry.py        # Dynamic domain schema loader
├── frontend/
│   ├── app/
│   │   ├── analytics/            # Dashboard + OLAP Explorer + Topics
│   │   ├── authority/            # Disambiguation + Review Queue
│   │   ├── domains/              # Domain schema management
│   │   ├── harmonization/        # Data cleaning workflows
│   │   ├── integrations/         # Store + AI provider config
│   │   ├── rag/                  # Semantic RAG chat
│   │   ├── components/           # Shared UI components
│   │   └── login/                # Authentication
│   └── lib/                      # API client, utilities
├── docs/
│   ├── ARCHITECTURE.md           # Design patterns & philosophy
│   ├── EVOLUTION_STRATEGY.md     # Long-term platform vision
│   └── SCIENTOMETRICS.md         # Enrichment strategy
└── requirements.txt
```

</details>

---

## Roadmap

### Completed

| Sprint | Milestone |
|--------|-----------|
| 1-5 | Core catalog, fuzzy disambiguation, analytics dashboard |
| 6-8 | Scientometric enrichment (OpenAlex, Scholar, Web of Science) |
| 9 | Monte Carlo stochastic citation projections |
| 10 | Semantic RAG with ChromaDB + multi-LLM BYOK panel |
| 11-13 | E-commerce integrations (Shopify, WooCommerce, Bsale) |
| 14 | Security hardening: JWT auth, RBAC, account lockout, password management |
| 15-16 | Authority Resolution Layer with weighted scoring engine (Wikidata, VIAF, ORCID, DBpedia, OpenAlex) |
| 17a | Domain Registry with YAML-based schema designer |
| 17b | OLAP Cube Explorer with DuckDB (multi-dimensional queries, drill-down, Excel pivot export) |
| 18 | Topic modeling, co-occurrence networks, correlation analysis |
| 19 | ARL Phase 2: batch resolution, review queue, bulk confirm/reject |

### Up Next

| Priority | Feature |
|----------|---------|
| High | **Artifact Studio** — PDF/HTML report generation from OLAP and Monte Carlo results |
| High | **Context Engineering Layer** — Structured LLM context builder with tool registry and persistent memory |
| Medium | **Knowledge Gap Analyzer** — Bibliometric gap detection across research corpora |
| Medium | **Scopus Adapter** — Elsevier premium enrichment (BYOK) |
| Medium | **ROI Calculator** — Multi-scenario return projections for research investment decisions |
| Low | **PostgreSQL/MySQL backends** — Production-grade database support |
| Low | **Scheduled Imports** — Automated ingestion from S3 / external APIs |
| Low | **SSO Integration** — OAuth2/SAML for institutional deployments |

See [EVOLUTION_STRATEGY.md](docs/EVOLUTION_STRATEGY.md) for the full platform vision and phased roadmap.

---

## Contributing

Contributions are welcome. See [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

## License

[Apache License 2.0](LICENSE)
