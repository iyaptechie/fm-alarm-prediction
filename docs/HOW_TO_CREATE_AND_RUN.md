# How to Create and Run the Project

This guide reflects the current project structure and execution flow in the repo.

---

## 1. Clone or create the repository

Create a repo named `fm-alarm-prediction` and add the project files to it.

If you are working inside GitHub Codespaces, this will already be available in your workspace.

---

## 2. Create the Python environment

```bash
python --version
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The repo expects environment variables for Neo4j and LLM access.

---

## 3. Configure environment variables

Update `.env` with your runtime values.

Example structure:

```dotenv
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
GROQ_API_KEY=your_groq_key
```

If the LLM layer is not being used, the RCA explanation step can be skipped, but the app expects the key to be configured when calling `llm/rca_explainer.py`.

---

## 4. Start Neo4j

```bash
docker compose up -d neo4j
```

Then open the browser UI at:

```text
http://localhost:7474
```

Credentials:

```text
username: neo4j
password: password123
```

---

## 5. Load the inventory and alarms

```bash
make inventory
make alarms
```

This reads the CSV data in `data/inventory/` and the alarm records in `data/alarms/alarms.csv` for downstream analysis.

---

## 6. Train the prediction model

```bash
make train
```

This runs:
- feature engineering
- ML training
- model evaluation

The model is saved in `ml/model_registry/` and used by `ml/predict.py`.

---

## 7. Run the API

```bash
make api
```

This starts the FastAPI app on:

```text
http://localhost:8000
```

Main routes:

```text
GET /health
GET /alarms
GET /predict/{device_name}
GET /rca/{device_name}
GET /topology/{device_name}
GET /impact/{device_name}
POST /alarms
```

Example request:

```bash
curl http://localhost:8000/predict/BLR-ACC01-HW01
curl http://localhost:8000/rca/BLR-ACC01-HW01
```

---

## 8. Run the dashboard

```bash
make dashboard
```

Then open:

```text
http://localhost:8501
```

The dashboard calls the API and displays alarm state, risk, RCA, and impact information.

---

## 9. Run tests

```bash
make test
```

---

## Current project flow

```text
Inventory CSVs
   ↓
Alarm dataset
   ↓
API loads alarms and recent device history
   ↓
ML prediction computes device fault probability
   ↓
Graph queries find upstream/downstream topology
   ↓
RCA logic selects likely root cause from active critical alarms
   ↓
Impact analysis estimates blast radius
   ↓
LLM explains the issue in plain English
   ↓
Dashboard presents the operational view
```

---

## Likely user scenario

A telecom operator can:

1. see active alarms in the dashboard or API
2. query a device by name
3. run prediction to estimate fault probability
4. inspect the dependency path to identify upstream causes
5. review impacted downstream devices
6. read the LLM-generated RCA explanation for next steps

---

## Useful commands summary

```bash
make help
make setup
make neo4j
make inventory
make alarms
make train
make api
make dashboard
make test
```

---

## Notes

- This project is based on synthetic telecom data for demonstration and learning.
- The graph, ML, RCA, and LLM layers are designed to work together, but each layer can also be validated independently.
- The LLM explanation layer is not a replacement for deterministic prediction and RCA logic; it adds human-readable context on top of the actual analysis pipeline.


### Phase 11
LLM / Agentic AI

Only add the LLM after the deterministic ML + graph solution is working.
