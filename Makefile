.PHONY: help setup neo4j inventory alarms train api dashboard test

help:
	@echo "FM Alarm Prediction — available commands:"
	@echo "  make setup      Install Python deps + copy .env template"
	@echo "  make neo4j      Start Neo4j via Docker Compose"
	@echo "  make inventory  Load inventory CSV into Neo4j"
	@echo "  make alarms     Generate synthetic alarms"
	@echo "  make train      Train the ML model"
	@echo "  make api        Run the FastAPI server  (http://localhost:8000)"
	@echo "  make dashboard  Run the Streamlit UI    (http://localhost:8501)"
	@echo "  make test       Run smoke tests"

setup:
	pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env — fill in your API keys"; fi

neo4j:
	docker compose up -d neo4j
	@echo "Neo4j browser → http://localhost:7474  (neo4j / password123)"

inventory:
	python -m ingestion.inventory_loader

alarms:
	python -m ingestion.alarm_generator

train:
	python -m ml.feature_engineering
	python -m ml.train
	python -m ml.evaluate

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0

test:
	pytest tests/ -v

all: 
	docker start fm-neo4j &
	sleep 5
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
	streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
