# FM Alarm Prediction Project Structure

This project is an end-to-end telecom alarm intelligence system. It combines:

- Synthetic network inventory data
- Alarm generation and ingestion
- ML-based fault prediction
- Neo4j graph analysis for root cause and impact
- FastAPI backend services
- Streamlit dashboard for monitoring and simulation
- Optional LLM explanation layer for natural-language RCA

The goal is to predict device or cell failures, trace the likely root cause, and show the affected topology in a simple operator dashboard.

---

## 1. High-Level Architecture

```text
Synthetic alarms / inventory
        ↓
Ingestion layer
        ↓
ML prediction engine
        ↓
Neo4j topology + RCA graph analysis
        ↓
FastAPI endpoints
        ↓
Streamlit dashboard / operator UI
        ↓
LLM explanation (optional)
```

Main technologies used:

- Python
- FastAPI
- Streamlit
- Neo4j
- Docker Compose
- Pandas / scikit-learn / networkx-like graph logic
- Optional Claude/OpenAI-style LLM reasoning layer

---

## 2. Folder Overview

```text
fm-alarm-prediction/
├── .devcontainer/              # Codespaces/devcontainer setup
├── .env / .env.example         # Neo4j and environment configuration
├── .gitignore                  # Ignore generated files and secrets
├── api/                        # FastAPI backend
├── dashboard/                  # Main Streamlit dashboard app
├── dashboard_new.py            # Alternative/experimental dashboard entry file
├── data/                       # Raw project datasets
├── docs/                       # Project plan and setup instructions
├── graph/                      # Neo4j topology and graph queries
├── ingestion/                  # Alarm generation and ingestion logic
├── llm/                        # RCA explanation via LLM
├── ml/                         # Feature engineering, training and prediction
├── notebooks/                  # Jupyter analysis notebooks
├── rca/                        # Root cause and impact analysis
├── tests/                      # Smoke tests
├── docker-compose.yml          # Neo4j service configuration
├── Makefile                    # Common commands
├── README.md                   # Main project overview
├── requirements.txt            # Python dependencies
├── autopush.sh                 # Push helper script
├── lib/                        # JS/CSS libraries for UI visuals
├── ts/                         # Extra support files / workspace support
└── files.zip                   # Project archive or sample data bundle
```

---

## 3. Root Files and Their Purpose

### `.env` and `.env.example`
These hold environment variables for Neo4j connection values.

Example values:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

These are essential for connecting the Python app to Neo4j.

### `docker-compose.yml`
Defines the Docker services, especially Neo4j.

This allows the app to run a local graph database without manually installing Neo4j locally.

### `Makefile`
Contains shortcuts such as:

- `make setup`
- `make neo4j`
- `make inventory`
- `make alarms`
- `make train`
- `make api`
- `make dashboard`
- `make test`

This is the easiest way to run the project.

### `requirements.txt`
Lists the Python packages required by the project, such as:

- FastAPI
- Streamlit
- Pandas
- Neo4j
- Uvicorn
- dotenv

### `README.md`
Main project summary and architecture guide.

It explains the use case, the folder structure, ML flow, graph analysis flow, and quick-start guidance.

---

## 4. Data Layer

### `data/`
This folder holds the operational data used by the app.

```text
data/
├── alarms/
│   └── alarms.csv
├── features/
│   └── features.csv
├── inventory/
│   ├── cells.csv
│   ├── inventory_devices.csv
│   ├── inventory_links.csv
│   ├── links.csv
│   ├── nodes.csv
│   └── sites.csv
```

#### `data/inventory/`
Contains synthetic network inventory data representing a telecom topology.

Typical entities include:

- sites
- cells
- nodes
- links
- devices

These files describe how equipment is connected inside the network.

#### `data/alarms/`
This is where alarm records are stored. They are used by:

- alarm ingestion
- feature engineering
- prediction requests
- dashboard display

---

## 5. Ingestion Layer

### `ingestion/`
This folder is responsible for creating and loading alarm/network data.

```text
ingestion/
├── alarm_api.py
├── alarm_generator.py
├── inventory_loader.py
```

#### `inventory_loader.py`
Loads the CSV inventory into the graph database (Neo4j).

This creates the network topology used by graph-based RCA and impact analysis.

#### `alarm_generator.py`
Generates synthetic telecom alarms such as:

- `HIGH_CPU`
- `PACKET_LOSS`
- `PTP_SYNC_LOSS`
- `LINK_DOWN`
- `CELL_UNAVAILABLE`
- `DU_UNREACHABLE`

This simulates real alarm traffic for training and testing.

#### `alarm_api.py`
Handles alarm ingestion logic and acts as a bridge between incoming alarms and the rest of the system.

---

## 6. Graph / Neo4j Layer

### `graph/`
This is the topology engine of the project.

```text
graph/
├── graph_queries.py
├── neo4j_loader.py
├── topology.py
```

#### `neo4j_loader.py`
Loads inventory objects into Neo4j as graph nodes and edges.

Typical graph structure:

- Site
- Router
- DU
- CU
- Cell
- Links

This creates a dependency graph that can be traversed to find upstream and downstream relationships.

#### `graph_queries.py`
Contains Cypher queries to retrieve:

- upstream nodes
- downstream nodes
- neighbours
- shortest path to core

This is used for topology exploration and RCA.

#### `topology.py`
Supports graph topology structure and more detailed network traversal logic.

---

## 7. Machine Learning Layer

### `ml/`
This folder contains the prediction pipeline.

```text
ml/
├── evaluate.py
├── feature_engineering.py
├── predict.py
├── train.py
└── model_registry/
```

#### `feature_engineering.py`
Builds the input features that will feed the prediction model.

Examples of features:

- alarm count
- severity score
- time-window patterns
- device-level trends
- upstream/downstream alarm context

#### `train.py`
Trains the predictive model, usually a tree-based model such as a Random Forest.

#### `evaluate.py`
Measures model performance and evaluates prediction quality.

#### `predict.py`
Runs the model on a device or cell and returns probability/fault score.

#### `model_registry/`
Stores saved model artifacts such as `.pkl` or serialized model files.

---

## 8. RCA / Impact Analysis

### `rca/`
This module performs root-cause analysis and blast-radius estimation.

```text
rca/
├── dependency_analysis.py
└── impact_analysis.py
```

#### `dependency_analysis.py`
Finds upstream dependency chains to identify the real cause of a failure.

This is where the graph database is used to answer: “What device or failure is upstream of this outage?”

#### `impact_analysis.py`
Finds what else will be affected if one device fails.

This gives the operator a blast radius or impact scope of the issue.

---

## 9. LLM Layer

### `llm/`
This layer explains the result in human language.

```text
llm/
├── __init__.py
└── rca_explainer.py
```

#### `rca_explainer.py`
Interfaces with an LLM service to transform technical RCA results into understandable explanations.

Example output:

- Why a cell is predicted to fail
- Which root cause is likely
- What other services are impacted
- A plain-English summary for a NOC user

This is not the core decision engine; it mainly explains the result from ML and graph analysis.

---

## 10. API Layer

### `api/`
This is the backend API that serves the system.

```text
api/
└── main.py
```

#### `main.py`
Contains the FastAPI application.

Main routes include:

- `/` → basic app info
- `/health` → health check
- `/alarms` → read alarm records
- `/predict/{device_name}` → ML prediction for a device
- `/rca/{device_name}` → root cause and explanation
- `/topology/{device_name}` → network topology info
- `/impact/{device_name}` → impacted devices or cells
- `/alarms` (POST) → inject a new alarm event

This is the main backend interface for both the dashboard and external callers.

---

## 11. Dashboard Layer

### `dashboard/`
Main Streamlit application used by operators.

```text
dashboard/
└── app.py
```

This front-end shows:

- live active alarms
- device simulation
- prediction results
- root cause details
- graph topology views
- impact visualization

It talks to the FastAPI backend and displays results in a simple web UI.

### `dashboard_new.py`
This appears to be another dashboard or experimental version of the front-end. It may be a newer variant or a prototype.

In practice, the main active UI seems to be in `dashboard/app.py`.

---

## 12. Notebooks and Tests

### `notebooks/`
Contains exploratory notebooks for data science and model work.

```text
notebooks/
└── 01_alarm_prediction.ipynb
```

This is usually where data experiments, feature analysis, and model prototypes are tried before moving into production code.

### `tests/`
Contains basic smoke tests.

```text
tests/
└── test_smoke.py
```

This validates that the app starts or critical behavior remains working.

---

## 13. Docs Folder

### `docs/`
Contains project setup and planning material.

```text
docs/
├── HOW_TO_CREATE_AND_RUN.md
└── PROJECT_PLAN.md
```

These documents explain:

- how to run the environment
- how to install dependencies
- how to start Neo4j
- how to train the model
- how to launch services
- the project roadmap and milestones

---

## 14. UI / Library Assets

### `lib/`
This folder stores UI front-end libraries and components used by the dashboard visualization.

```text
lib/
├── bindings/
│   └── utils.js
├── tom-select/
│   ├── tom-select.complete.min.js
│   └── tom-select.css
└── vis-9.1.2/
    ├── vis-network.css
    └── vis-network.min.js
```

These are UI support files for graph/network rendering in web-based views.

---

## 15. Data Flow End-to-End

A typical execution flow in this project looks like this:

```text
1. Inventory CSV files are loaded into Neo4j
2. Alarm generator creates synthetic defects and alarms
3. API receives alarm event or user requests data
4. Feature engineering transforms alarm history into ML inputs
5. ML model predicts a fault probability for a device or cell
6. RCA layer queries the graph to find the upstream root cause
7. Impact analysis finds downstream affected systems
8. FastAPI returns results to the dashboard
9. Dashboard displays alarms, risk, graph, and explanation
10. Optional LLM writes a plain-English summary of the RCA
```

---

## 16. What Each Main Part Does

### Backend
- `api/main.py`
- `ingestion/*`
- `rca/*`
- `graph/*`

These form the application logic and service layer.

### Data + ML
- `data/`
- `ml/`
- `notebooks/`

These produce and analyze the alarm and prediction data.

### Graph Intelligence
- `graph/`
- `rca/`

These answer the question: “Why is this failing, and what is affected?”

### Frontend
- `dashboard/app.py`
- `dashboard_new.py`

These present results to the operator.

### Ops and Setup
- `docker-compose.yml`
- `Makefile`
- `docs/`
- `.env` files

These make the system easy to run and manage.

---

## 17. Most Important Files to Start With

If you want to understand the project quickly, read in this order:

1. `README.md` — project overview
2. `api/main.py` — API logic and endpoints
3. `dashboard/app.py` — dashboard interaction
4. `graph/graph_queries.py` — graph traversal logic
5. `ml/predict.py` — prediction logic
6. `rca/dependency_analysis.py` — RCA logic
7. `docker-compose.yml` — environment setup
8. `Makefile` — running commands

---

## 18. Short Summary

This repo is a telecom fault-prediction and RCA platform built around:

- network inventory data
- alarm simulation
- ML fault prediction
- graph-based root cause analysis
- API exposure
- operator dashboard
- optional LLM explanation

It is designed to help a network operations center (NOC) detect, explain, and respond to issues more quickly.

---

## 19. Recommended Reading Order

```text
README.md
  ↓
Makefile
  ↓
docker-compose.yml
  ↓
api/main.py
  ↓
graph/graph_queries.py
  ↓
ml/predict.py
  ↓
rca/dependency_analysis.py
  ↓
dashboard/app.py
```

This order gives the clearest understanding of the project from setup → data → intelligence → UI.
