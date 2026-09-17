# Project Plan

## Milestone 1 — Foundation
- GitHub repository
- Codespace
- Python environment
- Docker

## Milestone 2 — Network Inventory
- Sites
- gNB
- CU
- DU
- Cells
- Routers
- Links

## Milestone 3 — Graph DB
- Neo4j
- Nodes
- Relationships
- Cypher topology queries

## Milestone 4 — Alarm System
- Synthetic alarm generator
- Alarm injection
- Alarm ingestion API
- Historical alarm store

## Milestone 5 — ML
- Feature engineering
- Random Forest
- Evaluation
- Prediction
- Model registry

## Milestone 6 — RCA
- ML prediction
- Graph topology
- Dependency analysis
- Impact analysis

## Milestone 7 — Application
- FastAPI
- Streamlit dashboard

## Milestone 8 — GenAI
- LLM explanation
- Tool calling
- Agent workflow
- Natural language RCA

## Final demo

Input:

```text
Inject PTP_SYNC_LOSS on DU001
```

System:

```text
Alarm received
      ↓
Features updated
      ↓
ML prediction
      ↓
CELL_DOWN probability = 91%
      ↓
Neo4j dependency analysis
      ↓
Possible root cause
      ↓
Affected cells
      ↓
Final RCA response
```
