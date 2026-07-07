## Demo

Live demo: https://finguard-ai-kappa.vercel.app

FinGuard AI is deployed as a full-stack demo showcasing real-time compliance monitoring, AI-powered semantic search, and alert investigation workflows.
---
# FinGuard AI — Real-Time Compliance Intelligence Platform

FinGuard AI is a full-stack AI-powered compliance monitoring platform that simulates financial transactions, scores transaction risk, creates alerts, supports investigation workflows, and enables semantic search across compliance evidence using OpenAI embeddings and ChromaDB.

The project is designed like an internal compliance operations tool for finance, fraud review, audit, and risk teams.


## Features

- Real-time simulated financial transaction ingestion
- Rule-based transaction risk scoring
- Automatic alert creation for high-risk transactions
- OpenAI-powered alert investigation explanations
- ChromaDB semantic search over transaction evidence
- PostgreSQL-backed structured transaction records
- Redis-backed service layer
- WebSocket live transaction feed
- Advanced React dashboard with analytics and investigation pages
- Dockerized local development setup

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, TypeScript, Vite |
| UI | Custom CSS, Recharts, Lucide Icons |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Cache / Real-Time | Redis, WebSockets |
| AI | OpenAI API |
| Vector Search | ChromaDB |
| ORM | SQLAlchemy |
| DevOps | Docker, Docker Compose |

---

## Architecture

```mermaid
flowchart TD
    A[React Dashboard] --> B[FastAPI Backend]

    B --> C[PostgreSQL]
    B --> D[Redis]
    B --> E[ChromaDB]
    B --> F[OpenAI API]

    G[Transaction Simulator] --> B
    B --> H[Risk Scoring Engine]
    H --> I[Risk Alerts]

    C --> J[Structured Transactions, Vendors, Alerts]
    E --> K[Vector Embeddings]
    F --> L[Embeddings and AI Explanations]

    B --> M[WebSocket Live Feed]
    M --> A

    A --> N[Command Center]
    A --> O[Live Monitor]
    A --> P[Semantic Search]
    A --> Q[Alert Investigation]
    A --> R[Vendor Risk]
    A --> S[Analytics]
```

---

## System Workflow

```mermaid
sequenceDiagram
    participant UI as React Dashboard
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant AI as OpenAI API
    participant VDB as ChromaDB

    UI->>API: Start transaction simulation
    API->>DB: Store generated transaction
    API->>API: Run risk scoring engine
    API->>DB: Create alert if risk score is high
    API->>AI: Generate transaction embedding
    API->>VDB: Store vector with metadata

    UI->>API: Submit semantic search query
    API->>AI: Generate query embedding
    API->>VDB: Retrieve similar transaction vectors
    API->>DB: Fetch full transaction records
    API->>UI: Return evidence, risk flags, and similarity scores
```

---

## Main Modules

### 1. Transaction Simulator

The simulator creates realistic financial transactions such as:

- Vendor payments
- Wire transfers
- Consulting fees
- Office supply purchases
- International transfers
- Employee reimbursements
- Duplicate invoice patterns
- Weekend or after-hours approvals

This makes the project feel dynamic instead of using static sample data only.

---

### 2. Risk Scoring Engine

Each transaction is evaluated using compliance-style risk rules.

Risk indicators include:

- Large transaction amount
- Enhanced review threshold
- Wire transfer
- Elevated-review country
- High-risk vendor profile
- Missing approval metadata
- Weekend or after-hours approval
- Duplicate invoice pattern
- Repeated vendor payment
- Round-number transfer
- Department baseline anomaly

Risk levels:

| Score | Risk Level |
|---|---|
| 0-30 | Low |
| 31-60 | Medium |
| 61-80 | High |
| 81-100 | Critical |

---

### 3. Alert Investigation Workflow

High-risk transactions automatically create alerts.

Investigation features:

- Alert detail view
- AI-generated explanation
- Evidence text
- Related transactions
- Timeline
- Investigation notes
- Status updates
- Analyst assignment

Alert statuses:

- Open
- In Review
- Escalated
- Resolved
- False Positive

---

### 4. AI Semantic Search

Users can search compliance records using natural language.

Example queries:

```text
suspicious wire transfers with missing approvals
```

```text
large vendor payments that need compliance review
```

```text
international payments to high-risk vendors
```

The search API returns:

- Matching transaction
- Similarity score
- Risk score
- Risk level
- Evidence text
- Metadata
- Matched reason

---

### 5. Real-Time Dashboard

The React dashboard includes:

- Command Center
- Live Transaction Monitor
- Semantic Search
- Alert Investigation
- Vendor Risk Profiles
- Analytics Page

The Live Monitor uses WebSockets to update transaction and alert data in real time.

---

## Project Structure

```text
finguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── ai.py
│   │   │   ├── alerts.py
│   │   │   ├── analytics.py
│   │   │   ├── health.py
│   │   │   ├── indexing.py
│   │   │   ├── risk.py
│   │   │   ├── search.py
│   │   │   ├── seed.py
│   │   │   ├── simulate.py
│   │   │   ├── system.py
│   │   │   ├── transactions.py
│   │   │   ├── vendors.py
│   │   │   └── websocket_feed.py
│   │   └── services/
│   │       ├── investigation_service.py
│   │       ├── openai_service.py
│   │       ├── risk_engine.py
│   │       ├── transaction_generator.py
│   │       └── vector_store.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── lib/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── Dockerfile
│   └── package.json
│
├── scripts/
│   └── smoke_test.sh
│
│
├── docker-compose.yml
├── Makefile
├── README.md
└── .gitignore
```

---

## Environment Setup

Create the backend environment file:

```bash
cp backend/.env.example backend/.env
```

Update your OpenAI key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Example backend `.env`:

```env
APP_NAME=FinGuard AI
ENVIRONMENT=development

DATABASE_URL=postgresql://finguard:finguard@postgres:5432/finguard_db
REDIS_URL=redis://redis:6379/0

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

CHROMA_COLLECTION_NAME=finguard_transactions
CHROMA_PERSIST_PATH=./chroma_data
```

Frontend `.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

## Run Locally

Start the full project:

```bash
docker compose up --build
```

Or use:

```bash
make build
```

Open:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## Seed and Generate Data

Seed sample compliance records:

```bash
curl -X POST "http://localhost:8000/seed/sample-data?force=true"
```

Generate simulated transactions:

```bash
curl -X POST "http://localhost:8000/simulate/batch?count=50"
```

Index transactions into ChromaDB:

```bash
curl -X POST "http://localhost:8000/index/transactions?limit=500"
```

Or use:

```bash
make seed
make simulate
make index
```

---

## Smoke Test

Run:

```bash
./scripts/smoke_test.sh
```

Or:

```bash
make smoke
```

The smoke test checks:

- Backend health
- PostgreSQL health
- Redis health
- System status
- Seed data
- Transaction simulation
- Vector indexing
- Semantic search
- Analytics summary

---

## Important API Endpoints

### Health and System

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/health/database` | PostgreSQL connection check |
| GET | `/health/redis` | Redis connection check |
| GET | `/system/status` | Full system status |
| GET | `/system/version` | Project version and stack |

### Transactions

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/transactions` | List transactions |
| POST | `/transactions` | Create transaction |
| GET | `/transactions/recent/feed` | Recent transaction feed |
| GET | `/transactions/{transaction_id}` | Transaction detail |

### Simulation

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/simulate/patterns` | View transaction simulation patterns |
| POST | `/simulate/transaction` | Generate one fake transaction |
| POST | `/simulate/batch?count=50` | Generate batch transactions |
| POST | `/simulate/live` | Start background live simulation |

### Risk Engine

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/risk/rules/seed` | Seed default risk rules |
| GET | `/risk/rules` | List risk rules |
| POST | `/risk/evaluate` | Evaluate transaction risk without saving |

### Alerts

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/alerts` | List alerts |
| GET | `/alerts/recent/feed` | Recent alert feed |
| GET | `/alerts/{alert_id}` | Alert detail |
| PATCH | `/alerts/{alert_id}/status` | Update alert status |
| GET | `/alerts/{alert_id}/investigation` | Full investigation view |
| POST | `/alerts/{alert_id}/notes` | Add investigation note |
| GET | `/alerts/{alert_id}/notes` | List investigation notes |
| POST | `/alerts/{alert_id}/ai-explanation` | Generate AI explanation |
| GET | `/alerts/{alert_id}/related-transactions` | Related transactions |

### Semantic Search

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/index/transactions` | Index transactions into ChromaDB |
| GET | `/index/stats` | Vector index stats |
| DELETE | `/index/reset` | Reset vector index |
| POST | `/search/semantic` | Natural language semantic search |

### Analytics

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/analytics/summary` | Dashboard summary |
| GET | `/analytics/overview` | Full dashboard overview |
| GET | `/analytics/risk-by-department` | Risk by department |
| GET | `/analytics/risk-by-payment-method` | Risk by payment method |
| GET | `/analytics/risk-by-category` | Risk by category |
| GET | `/analytics/risk-by-country` | Risk by country |
| GET | `/analytics/alert-severity-distribution` | Alert severity distribution |
| GET | `/analytics/alert-status-distribution` | Alert status distribution |
| GET | `/analytics/top-risky-vendors` | Top risky vendors |
| GET | `/analytics/transaction-volume-trend` | Transaction trend |
| GET | `/analytics/alert-trend` | Alert trend |

### WebSocket

| Endpoint | Purpose |
|---|---|
| `ws://localhost:8000/ws/live-feed` | Live transaction and alert feed |

---

## Example Semantic Search Request

```bash
curl -X POST http://localhost:8000/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "suspicious wire transfers with missing approvals",
    "top_k": 5
  }'
```

Example response:

```json
{
  "query": "suspicious wire transfers with missing approvals",
  "top_k": 5,
  "result_count": 5,
  "results": [
    {
      "similarity_score": 0.82,
      "transaction": {
        "transaction_id": "TXN-10003",
        "vendor_name": "Apex Imports",
        "risk_level": "Critical",
        "risk_score": 96
      },
      "matched_reason": "This transaction matched the query because its embedded evidence is semantically similar..."
    }
  ]
}
```

---

## Screenshots

Add screenshots inside:

```text
docs/screenshots/
```

Recommended screenshots:

```text
docs/screenshots/command-center.png
docs/screenshots/live-monitor.png
docs/screenshots/semantic-search.png
docs/screenshots/alert-investigation.png
docs/screenshots/vendor-risk.png
docs/screenshots/analytics.png
```

Then uncomment or add these:

```markdown
![Command Center](docs/screenshots/command-center.png)

![Live Monitor](docs/screenshots/live-monitor.png)

![Semantic Search](docs/screenshots/semantic-search.png)

![Alert Investigation](docs/screenshots/alert-investigation.png)

![Vendor Risk](docs/screenshots/vendor-risk.png)

![Analytics](docs/screenshots/analytics.png)
```

---

## What I Built

This project was built as a production-style full-stack system with separate layers for transaction ingestion, risk scoring, vector search, investigation workflows, and dashboard analytics.

Key engineering work:

- Designed PostgreSQL models for vendors, transactions, alerts, risk rules, search logs, and investigation notes.
- Built a FastAPI backend with modular routes and service layers.
- Implemented a reusable risk scoring engine with multiple compliance indicators.
- Created a fake real-time transaction generator for realistic compliance scenarios.
- Integrated OpenAI embeddings and ChromaDB for semantic search.
- Built OpenAI-powered alert explanations grounded in transaction evidence.
- Added WebSocket support for live frontend updates.
- Built an advanced React dashboard with multiple operational pages.
- Added smoke testing, Docker Compose, environment examples, and Makefile commands.

---

## Resume Bullets

```text
FinGuard AI — Real-Time Compliance Intelligence Platform | Python, FastAPI, React.js, PostgreSQL, Redis, ChromaDB, OpenAI APIs, Docker

- Built a real-time compliance intelligence platform that ingests simulated financial transactions, scores risk through rule-based detection, and surfaces high-risk activity through a dynamic React dashboard.

- Integrated OpenAI embeddings and ChromaDB vector search with PostgreSQL-backed transaction metadata to support semantic investigation across vendors, payments, departments, and risk categories.

- Designed explainable alert workflows with AI-generated investigation summaries, evidence snippets, similarity scores, risk flags, WebSocket live updates, and analyst review notes.
```

---

## Local Commands

```bash
make build
make seed
make simulate
make index
make smoke
make status
make backend-logs
make frontend-logs
make down
```

---

## Project Status

It demonstrates:

- Full-stack development
- Backend architecture
- AI API integration
- Semantic search
- Vector databases
- Real-time systems
- Compliance-style workflows
- PostgreSQL data modeling
- Dockerized development
- Advanced React dashboard design
