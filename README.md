# FM Alarm Prediction — End-to-End Use Case

> **Predict 5G Cell Down using ML + Graph DB with Synthetic Data**
>
> Runs entirely on **GitHub Codespaces** — no local setup needed.
> LLM calls go outbound to the **Anthropic Claude API** from inside Codespaces.

---

## Use Case Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Alarm Trigger (PTP_SYNC_LOSS on DU001)                                 │
│       ↓                                                                 │
│  Ingestion API  →  Feature Engineering  →  ML Prediction (91% CELL_DOWN)│
│       ↓                                                                 │
│  Neo4j Graph  →  RCA: RTR001 = NODE_DOWN                               │
│       ↓                                                                 │
│  Impact: CELL001, CELL002, CELL003 affected                             │
│       ↓                                                                 │
│  LLM Agent: "Why is CELL001 failing?" → Plain English RCA explanation  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture — 8 Boxes

| Box | Component | Folder / File | Description |
|-----|-----------|---------------|-------------|
| 1 | **Network Inventory** | `data/inventory/` | Synthetic CSVs — sites, gNBs, CUs, DUs, cells, routers, links |
| 2 | **Alarm Generator** | `ingestion/alarm_generator.py` | Generates realistic alarm patterns (HIGH_CPU, PACKET_LOSS, CELL_UNAVAILABLE…) |
| 3 | **Alarm Ingestion API** | `ingestion/alarm_api.py`, `api/main.py` | POST /alarms → validate → store → update graph → trigger prediction |
| 4 | **Data Stores** | `data/alarms/`, Neo4j (Docker) | Alarm DB + Graph DB (Neo4j) + Inventory CSVs |
| 5 | **ML Model** | `ml/` | Feature engineering → Random Forest → CELL_DOWN prediction |
| 6 | **Graph RCA / Impact** | `graph/`, `rca/` | Neo4j topology queries → find root cause → calculate blast radius |
| 7 | **LLM / Agent** | `llm/` | Claude API → natural language queries, explain predictions, RCA summaries |
| 8 | **API + Dashboard** | `api/`, `dashboard/` | FastAPI REST + Streamlit UI for NOC operators |

---

## Folder Structure

```
fm-alarm-prediction/
│
├── .devcontainer/
│   └── devcontainer.json        ← Codespaces: auto-installs Python, Docker, extensions
│
├── data/
│   ├── inventory/               ← [Box 1] Network topology (input CSVs)
│   │   ├── sites.csv
│   │   ├── nodes.csv            ← gNB, CU, DU, Router
│   │   ├── cells.csv
│   │   └── links.csv
│   └── alarms/                  ← [Box 4] Generated alarm data (git-ignored)
│       └── .gitkeep
│
├── ingestion/                   ← [Box 2 + 3] Alarm generation & ingestion
│   ├── inventory_loader.py      ← Load CSVs into Neo4j
│   ├── alarm_generator.py       ← Generate synthetic alarms → data/alarms/
│   └── alarm_api.py             ← Alarm ingestion logic
│
├── graph/                       ← [Box 4 + 6] Neo4j graph operations
│   ├── neo4j_loader.py          ← Push inventory into Neo4j
│   ├── topology.py              ← Build/query topology graph
│   └── graph_queries.py         ← Cypher queries (upstream, downstream, paths)
│
├── ml/                          ← [Box 5] ML pipeline
│   ├── feature_engineering.py   ← Build feature vectors from alarm history
│   ├── train.py                 ← Train Random Forest model
│   ├── evaluate.py              ← Metrics, confusion matrix
│   ├── predict.py               ← Predict CELL_DOWN probability
│   └── model_registry/          ← Saved .pkl models (git-ignored)
│       └── .gitkeep
│
├── rca/                         ← [Box 6] Root cause & impact analysis
│   ├── dependency_analysis.py   ← Find upstream dependencies via Neo4j
│   └── impact_analysis.py       ← Calculate downstream blast radius
│
├── llm/                         ← [Box 7] LLM / Agent layer
│   ├── __init__.py
│   └── rca_explainer.py         ← Claude API: explain RCA in plain English
│
├── api/                         ← [Box 8] FastAPI REST server
│   └── main.py                  ← GET /predict, GET /rca, POST /alarms
│
├── dashboard/                   ← [Box 8] Streamlit UI
│   └── app.py                   ← Real-time alarms, predictions, topology view
│
├── notebooks/
│   └── 01_alarm_prediction.ipynb ← Exploration & experiments
│
├── tests/
│   └── test_smoke.py            ← Basic smoke tests
│
├── docs/
│   ├── HOW_TO_CREATE_AND_RUN.md ← Step-by-step setup guide
│   └── PROJECT_PLAN.md          ← Milestone breakdown
│
├── .env.example                 ← Copy to .env and fill API keys
├── .gitignore
├── docker-compose.yml           ← Neo4j container
├── Makefile                     ← Shortcut commands
└── requirements.txt             ← Python dependencies
```

---

## Network Topology Model

```
REGION
  └── SITE
        └── gNB
              ├── CU ──→ ROUTER ──→ (transport)
              └── DU ──→ ROUTER
                    ├── CELL-01
                    ├── CELL-02
                    └── CELL-03
```

---

## Alarm Types

| Alarm | Severity | Typical Source |
|-------|----------|----------------|
| `HIGH_CPU` | WARNING | DU, CU |
| `HIGH_MEMORY` | WARNING | DU, CU |
| `PACKET_LOSS` | MAJOR | Router, Link |
| `PTP_SYNC_LOSS` | CRITICAL | DU |
| `LINK_DOWN` | CRITICAL | Router, Transport |
| `CELL_UNAVAILABLE` | CRITICAL | Cell |
| `DU_UNAVAILABLE` | CRITICAL | DU |
| `DU_UNREACHABLE` | CRITICAL | DU |

---

## ML Pipeline

```
Alarm history (CSV)
      ↓
Feature engineering  ← alarm_count, severity_score, upstream_alarms, time_window
      ↓
Random Forest        ← target: cell_down_next_10min (binary)
      ↓
Prediction output:
  CELL001 → CELL_DOWN  prob=0.91  risk=HIGH
```

---

## LLM / Agent Layer (Box 7)

The LLM layer sits **on top** of the deterministic ML + graph pipeline.
It does **not** replace ML — it explains results in plain English.

```
User: "Why is CELL001 predicted to fail?"
         ↓
  llm/rca_explainer.py
         ↓
  Sends to Claude API (outbound HTTPS from Codespace)
         ↓
  Claude reads: prediction (91%), top features, Neo4j topology
         ↓
  Returns: "CELL001 is at high risk because DU001 has lost PTP sync,
            which historically precedes cell outages within 10 minutes.
            Root cause is likely RTR001 (LINK_DOWN).
            Impacted: CELL001, CELL002, CELL003 under DU001."
```

**Planned agent tools:**
- `get_prediction(cell_id)` — call ML predict endpoint
- `get_rca(node_id)` — query Neo4j for upstream root cause
- `get_impact(node_id)` — get downstream impacted cells
- `get_alarm_history(node_id, window)` — fetch recent alarms

---

## Prediction Output Example

```
Predicted Event : CELL001 → CELL_DOWN
Probability     : 91%
Risk            : HIGH

Possible Root Cause:
  RTR001  →  NODE_DOWN

Affected Resources:
  RAN1 | CELL001 | CELL002 | CELL003
```

---

## Implementation Phases

| Phase | What | Status |
|-------|------|--------|
| 1 | GitHub repo + Codespace + Python + Docker | ✅ Ready |
| 2 | Synthetic inventory CSVs | ✅ Data files exist |
| 3 | Neo4j topology load | 🔲 Implement |
| 4 | Synthetic alarm generator | 🔲 Implement |
| 5 | Alarm ingestion API | 🔲 Implement |
| 6 | ML feature engineering | 🔲 Implement |
| 7 | Random Forest prediction | 🔲 Implement |
| 8 | Graph RCA + Impact analysis | 🔲 Implement |
| 9 | FastAPI endpoints | 🔲 Implement |
| 10 | Streamlit dashboard | 🔲 Implement |
| 11 | LLM / Agent (Claude API) | 🔲 Implement last |

> **Rule:** Build ML + Graph first. Add LLM only after deterministic pipeline works end-to-end.

---

## Quick Start — GitHub Codespaces

### 1. Upload repo to GitHub

```bash
# In your local terminal
git init
git add .
git commit -m "Initial project structure"
git remote add origin https://github.com/<your-username>/fm-alarm-prediction.git
git push -u origin main
```

### 2. Open Codespace

Go to your GitHub repo → **Code → Codespaces → Create codespace on main**

The `.devcontainer/devcontainer.json` auto-installs Python 3.11, Docker, and VS Code extensions.

### 3. Set up environment

```bash
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and Neo4j password
```

### 4. Start Neo4j

```bash
make neo4j
# Neo4j browser → http://localhost:7474  (neo4j / password123)
```

### 5. Run the pipeline step by step

```bash
make inventory    # Load CSVs into Neo4j
make alarms       # Generate synthetic alarms
make train        # Train ML model
make api          # Start FastAPI  → http://localhost:8000
make dashboard    # Start Streamlit → http://localhost:8501
```

---

## SSH into Codespace (optional)

```bash
# Install GitHub CLI locally, then:
gh auth login
gh codespace list
gh codespace ssh --codespace <your-codespace-name>

# Inside Codespace — install Claude Code CLI
npm install -g @anthropic-ai/claude-code
claude
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| ML | scikit-learn (Random Forest) |
| Graph DB | Neo4j 5 (Docker) |
| API | FastAPI + Uvicorn |
| Dashboard | Streamlit |
| LLM | Anthropic Claude API (`anthropic` SDK) |
| Dev environment | GitHub Codespaces |
| Orchestration | Docker Compose |

---

## Key Benefits

- **Proactive fault detection** — predict cell down before it happens
- **Reduced MTTR** — automated root cause narrows investigation instantly
- **No local setup** — everything runs in Codespaces
- **LLM-ready** — agent layer extensible with tool calling
- **Scalable** — swap synthetic data for real OSS/BSS feeds
