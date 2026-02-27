# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd

app = FastAPI(title="Rural Health Logistics Agent")

outbreak_data = pd.DataFrame()
van_assignments: Dict[int, dict] = {}
optimization_status = "Not optimized"

class OutbreakReport(BaseModel):
    village_id: int
    village_name: str
    latitude: float
    longitude: float
    population: int
    vulnerability_index: float
    tests_done: int
    positive_cases: int

@app.get("/")
def health():
    return {"status": "API running"}


@app.post("/ingest")
def ingest(reports: List[OutbreakReport]):
    global outbreak_data

    df = pd.DataFrame([r.dict() for r in reports])

    if outbreak_data.empty:
        outbreak_data = df
    else:
        outbreak_data = pd.concat([outbreak_data, df], ignore_index=True)

    return {"message": "Data ingested", "total_rows": len(outbreak_data)}


@app.get("/admin/dashboard")
def dashboard():
    return {
        "records": len(outbreak_data),
        "optimization_status": optimization_status,
        "active_vans": len(van_assignments),
    }