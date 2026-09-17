from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

from ingestion.alarm_generator import load_alarms
from ml.predict import predict_device
from rca.dependency_analysis import find_root_cause
from rca.impact_analysis import get_blast_radius
from llm.rca_explainer import explain_rca

app = FastAPI(title="FM Alarm Prediction API", version="1.0")

# ── Models ────────────────────────────────────────────────────────────────────

class AlarmIn(BaseModel):
    device_name:  str
    alarm_type:   str
    severity:     str
    device_type:  Optional[str] = "Access"
    vendor:       Optional[str] = "HUAWEI"
    hierarchy_level: Optional[int] = 9

class PredictResponse(BaseModel):
    device_name:       str
    fault_probability: float
    risk:              str
    alarm_count:       int
    top_alarms:        List[str]

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"project": "FM Alarm Prediction", "status": "running", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/alarms")
def get_alarms(status: Optional[str] = None, severity: Optional[str] = None, limit: int = 50):
    df = load_alarms()
    if status:
        df = df[df["Status"] == status.upper()]
    if severity:
        df = df[df["Severity"] == severity.upper()]
    return {"total": len(df), "alarms": df.head(limit).to_dict(orient="records")}

@app.get("/predict/{device_name}")
def predict(device_name: str, window_minutes: int = 10):
    df = load_alarms()
    device_alarms = df[
        (df["Device Name"] == device_name) &
        (df["Status"].isin(["ACTIVE", "ACKNOWLEDGED"]))
    ]
    if device_alarms.empty:
        raise HTTPException(status_code=404, detail=f"No active alarms for {device_name}")

    recent = device_alarms.tail(10).to_dict(orient="records")
    alarm_list = [
        {
            "Alarm Type":      r["Alarm Type"],
            "Severity":        r["Severity"],
            "Device Type":     r["Device Type"],
            "Vendor":          r["Vendor"],
            "Hierarchy Level": r["Hierarchy Level"],
        }
        for r in recent
    ]
    result = predict_device(device_name, alarm_list)
    return result

@app.get("/rca/{device_name}")
def rca(device_name: str):
    prediction = predict(device_name)
    rca_result  = find_root_cause(device_name)
    blast       = get_blast_radius(device_name)
    explanation = explain_rca(prediction, rca_result, blast)
    return {
        "device_name": device_name,
        "prediction":  prediction,
        "rca":         rca_result,
        "blast_radius": blast,
        "explanation": explanation,
    }

@app.get("/topology/{device_name}")
def topology(device_name: str):
    from graph.graph_queries import get_upstream, get_downstream, get_neighbours, get_path_to_core
    return {
        "device_name": device_name,
        "upstream":    get_upstream(device_name),
        "downstream":  get_downstream(device_name),
        "neighbours":  get_neighbours(device_name),
        "path_to_core": get_path_to_core(device_name),
    }

@app.get("/impact/{device_name}")
def impact(device_name: str):
    return get_blast_radius(device_name)

@app.post("/alarms")
def inject_alarm(alarm: AlarmIn):
    alarm_list = [{
        "Alarm Type":      alarm.alarm_type,
        "Severity":        alarm.severity,
        "Device Type":     alarm.device_type,
        "Vendor":          alarm.vendor,
        "Hierarchy Level": alarm.hierarchy_level,
    }]
    prediction = predict_device(alarm.device_name, alarm_list)
    rca_result  = find_root_cause(alarm.device_name)
    blast       = get_blast_radius(alarm.device_name)
    explanation = explain_rca(prediction, rca_result, blast)
    return {
        "device_name": alarm.device_name,
        "prediction":  prediction,
        "rca":         rca_result,
        "blast_radius": blast,
        "explanation": explanation,
    }
