# How to Create and Run the Project

## 1. Create the GitHub repository

Create a new GitHub repository named:

`fm-alarm-prediction`

Recommended settings:

- Public or Private: your choice
- Add README: No
- Add .gitignore: No
- License: optional

Then upload this complete folder to the repository.

## 2. Open GitHub Codespaces

Open the repository in GitHub and choose:

Code → Codespaces → Create codespace on main

The repository will open in a browser-based VS Code environment.

## 3. Create Python environment

In the Codespace terminal:

```bash
python --version
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

## 4. Start with synthetic data

The first coding target is:

```text
data/inventory/
    sites.csv
    nodes.csv
    cells.csv
    links.csv

data/alarms/
    historical_alarms.csv
```

Do not start with LLM or Agentic AI.

First make the ML + Graph DB pipeline work.

## 5. Run the alarm generator

Later, implement:

```bash
python ingestion/alarm_generator.py
```

Expected result:

`data/alarms/generated_alarms.csv`

## 6. Start Neo4j

Docker is recommended.

```bash
docker compose up -d neo4j
```

Then open the Neo4j browser exposed by the compose configuration.

## 7. Load network inventory

Implement:

```bash
python graph/neo4j_loader.py
```

The graph should represent:

```text
SITE
  |
  └── GNB
       |
       ├── CU
       |
       └── DU
            |
            ├── CELL
            ├── CELL
            └── CELL
```

and transport connectivity:

```text
DU → ROUTER
CU → ROUTER
```

## 8. Train the first ML model

Implement:

```bash
python ml/train.py
```

The first target should be:

`cell_down_next_10min`

Start with Random Forest.

Do not start with deep learning.

## 9. Run prediction

Implement:

```bash
python ml/predict.py
```

Example target output:

```text
CELL001
Prediction: CELL_DOWN
Probability: 0.91
Risk: HIGH
```

## 10. Add Graph-based RCA

After prediction works, query Neo4j to find:

- upstream nodes
- downstream nodes
- connected transport nodes
- alarms on dependent resources
- potentially impacted cells

Example:

```text
CELL001
   ↓
DU001
   ↓
GNB001
   ↓
RTR001
```

## 11. Add the alarm ingestion API

Use FastAPI.

Run:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Example request:

```json
{
  "node_id": "DU001",
  "alarm_type": "PTP_SYNC_LOSS",
  "severity": "CRITICAL"
}
```

## 12. Final target

The end-to-end solution should eventually work like:

```text
Alarm Injection
      ↓
Alarm API
      ↓
Feature Engineering
      ↓
ML Prediction
      ↓
Neo4j Topology
      ↓
RCA / Impact Analysis
      ↓
Prediction + Explanation
```

Example:

```text
Predicted Event: CELL_DOWN
Probability: 91%
Risk: HIGH

Possible Root Cause:
RTR001 LINK_DOWN

Potential Impact:
CELL001
CELL002
CELL003
```

## Suggested implementation order

### Phase 1
GitHub + Codespaces + Python

### Phase 2
Synthetic inventory

### Phase 3
Neo4j topology

### Phase 4
Synthetic alarms

### Phase 5
Alarm ingestion

### Phase 6
ML feature engineering

### Phase 7
Random Forest prediction

### Phase 8
Graph RCA

### Phase 9
FastAPI

### Phase 10
Dashboard

### Phase 11
LLM / Agentic AI

Only add the LLM after the deterministic ML + graph solution is working.
