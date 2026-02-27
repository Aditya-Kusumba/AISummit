from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from routing_osm import generate_osm_route
from pydantic import BaseModel
from datetime import datetime
from models import ResourceInventory

from database import SessionLocal, engine
from models import Base, Village, Disease, OutbreakReport

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rural Health Logistics Agent")


# ----------------------------
# DB Dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Pydantic Input Model
# ----------------------------
class OutbreakInput(BaseModel):
    village_id: int
    disease_id: int
    tests_done: int
    positive_cases: int


# ----------------------------
# Health Check
# ----------------------------
@app.get("/")
def health():
    return {"status": "API running"}


# ----------------------------
# Ingestion API (Stage 1–3)
# ----------------------------
@app.post("/ingest")
def ingest(
    reports: List[OutbreakInput],
    db: Session = Depends(get_db)
):
    inserted_count = 0

    for report in reports:

        # 1️⃣ Validate village
        village = db.query(Village).filter(
            Village.id == report.village_id
        ).first()

        if not village:
            return {"error": f"Village {report.village_id} not found"}

        # 2️⃣ Validate disease
        disease = db.query(Disease).filter(
            Disease.id == report.disease_id
        ).first()

        if not disease:
            return {"error": f"Disease {report.disease_id} not found"}

        # 3️⃣ Positivity rate
        positivity_rate = (
            report.positive_cases / report.tests_done
            if report.tests_done > 0 else 0
        )

        # 4️⃣ Fetch last report
        last_report = (
            db.query(OutbreakReport)
            .filter(
                OutbreakReport.village_id == report.village_id,
                OutbreakReport.disease_id == report.disease_id
            )
            .order_by(OutbreakReport.report_time.desc())
            .first()
        )

        # 5️⃣ Spread velocity
        if last_report and last_report.positive_cases > 0:
            spread_velocity = (
                (report.positive_cases - last_report.positive_cases)
                / last_report.positive_cases
            )
        else:
            spread_velocity = 0.0

        spread_velocity = max(spread_velocity, -1.0)

        # 6️⃣ Risk scoring
        normalized_population = village.population / 10000

        W1 = 0.30
        W2 = 0.25
        W3 = 0.20
        W4 = 0.15
        W5 = 0.10

        risk_score = (
            (W1 * positivity_rate) +
            (W2 * spread_velocity) +
            (W3 * village.vulnerability_index) +
            (W4 * normalized_population) +
            (W5 * disease.severity_weight)
        )

        risk_score = max(risk_score, 0.0)

        # 7️⃣ Insert record
        outbreak = OutbreakReport(
            village_id=report.village_id,
            disease_id=report.disease_id,
            report_time=datetime.utcnow(),
            tests_done=report.tests_done,
            positive_cases=report.positive_cases,
            positivity_rate=positivity_rate,
            spread_velocity=spread_velocity,
            risk_score=risk_score,
            reporter_type="dashboard",
            confidence_score=1.0
        )

        db.add(outbreak)
        inserted_count += 1

    db.commit()

    return {
        "message": "Data ingested successfully",
        "records_inserted": inserted_count
    }

@app.post("/admin/generate-route/{batch_id}")
def generate_route(batch_id: int, db: Session = Depends(get_db)):

    allocations = db.query(AllocationDetail).filter(
        AllocationDetail.batch_id == batch_id
    ).all()

    if not allocations:
        return {"error": "No allocations found"}

    villages = [a.village for a in allocations]

    result = generate_osm_route(villages)

    return result

@app.get("/admin/dashboard")
def dashboard(db: Session = Depends(get_db)):

    total_reports = db.query(OutbreakReport).count()
    total_villages = db.query(Village).count()

    return {
        "total_reports": total_reports,
        "total_villages": total_villages
    }


# ----------------------------
# Priority Ranking (Stage 4)
# ----------------------------
@app.get("/admin/priority-ranking")
def priority_ranking(db: Session = Depends(get_db)):

    subquery = (
        db.query(
            OutbreakReport.village_id,
            func.max(OutbreakReport.report_time).label("latest_time")
        )
        .group_by(OutbreakReport.village_id)
        .subquery()
    )

    latest_reports = (
        db.query(OutbreakReport)
        .join(
            subquery,
            (OutbreakReport.village_id == subquery.c.village_id) &
            (OutbreakReport.report_time == subquery.c.latest_time)
        )
        .order_by(OutbreakReport.risk_score.desc())
        .all()
    )

    return [
        {
            "village_id": r.village_id,
            "risk_score": round(r.risk_score, 4),
            "positivity_rate": round(r.positivity_rate, 4),
            "spread_velocity": round(r.spread_velocity, 4)
        }
        for r in latest_reports
    ]


# ----------------------------
# Mock Data Seeder
# ----------------------------

@app.on_event("startup")
def seed_mock_data():
    db = SessionLocal()

    # Skip if already seeded
    if db.query(Village).first():
        db.close()
        return

    # ----------------------------
    # 1️⃣ Diseases
    # ----------------------------
    diseases = [
        Disease(id=1, name="Malaria", severity_weight=1.5),
        Disease(id=2, name="Dengue", severity_weight=1.8),
        Disease(id=3, name="Cholera", severity_weight=2.0),
    ]
    db.add_all(diseases)

    # ----------------------------
    # 2️⃣ Villages (clustered ~5km)
    # ----------------------------
    villages = [
        Village(id=1, name="Kothapet", latitude=17.123, longitude=78.456, population=2000, vulnerability_index=0.6),
        Village(id=2, name="Ramnagar", latitude=17.130, longitude=78.462, population=1500, vulnerability_index=0.5),
        Village(id=3, name="Lakshmipur", latitude=17.118, longitude=78.450, population=1800, vulnerability_index=0.7),
        Village(id=4, name="Shantinagar", latitude=17.135, longitude=78.470, population=2200, vulnerability_index=0.4),
    ]
    db.add_all(villages)

    # ----------------------------
    # 3️⃣ Resource Inventory
    # ----------------------------
    inventory = ResourceInventory(
        doctors_available=6,
        nurses_available=4,
        malaria_kits=300,
        dengue_kits=200,
        cholera_kits=150,
        vaccines=500
    )
    db.add(inventory)

    db.commit()
    db.close()

@app.get("/admin/batch/{batch_id}")
def get_batch(batch_id: int, db: Session = Depends(get_db)):

    batch = db.query(AllocationBatch).filter(
        AllocationBatch.id == batch_id
    ).first()

    if not batch:
        return {"error": "Batch not found"}

    allocations = db.query(AllocationDetail).filter(
        AllocationDetail.batch_id == batch_id
    ).all()

    return {
        "batch_id": batch.id,
        "mode": batch.mode,
        "total_villages_selected": batch.total_villages_selected,
        "allocations": [
            {
                "village_id": a.village_id,
                "doctors_allocated": a.doctors_allocated,
                "malaria_kits_allocated": a.malaria_kits_allocated,
                "priority_score": a.priority_score
            }
            for a in allocations
        ]
    }

from models import AllocationBatch, AllocationDetail, ResourceInventory

@app.post("/admin/run-allocation")
def run_allocation(db: Session = Depends(get_db)):

    # 1️⃣ Get available resources
    inventory = db.query(ResourceInventory).first()

    if not inventory:
        return {"error": "No resource inventory found"}

    doctors_available = inventory.doctors_available
    kits_available = inventory.malaria_kits  # simplified assumption

    # 2️⃣ Get latest ranked villages
    subquery = (
        db.query(
            OutbreakReport.village_id,
            func.max(OutbreakReport.report_time).label("latest_time")
        )
        .group_by(OutbreakReport.village_id)
        .subquery()
    )

    ranked_reports = (
        db.query(OutbreakReport)
        .join(
            subquery,
            (OutbreakReport.village_id == subquery.c.village_id) &
            (OutbreakReport.report_time == subquery.c.latest_time)
        )
        .order_by(OutbreakReport.risk_score.desc())
        .all()
    )

    # 3️⃣ Create allocation batch
    batch = AllocationBatch(
        mode="online",
        total_villages_selected=0
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    selected_count = 0

    # 4️⃣ Greedy allocation
    for report in ranked_reports:

        required_doctors = max(1, int(report.risk_score * 3))
        required_kits = max(10, int(report.risk_score * 100))

        if doctors_available >= required_doctors and kits_available >= required_kits:

            allocation = AllocationDetail(
                batch_id=batch.id,
                village_id=report.village_id,
                doctors_allocated=required_doctors,
                nurses_allocated=0,
                malaria_kits_allocated=required_kits,
                dengue_kits_allocated=0,
                priority_score=report.risk_score
            )

            db.add(allocation)

            doctors_available -= required_doctors
            kits_available -= required_kits
            selected_count += 1

        else:
            break  # stop when resources exhausted

    batch.total_villages_selected = selected_count

    # Update inventory
    inventory.doctors_available = doctors_available
    inventory.malaria_kits = kits_available

    db.commit()

    return {
        "batch_id": batch.id,
        "villages_selected": selected_count,
        "remaining_doctors": doctors_available,
        "remaining_kits": kits_available
    }

@app.get("/admin/heatmap")
def heatmap(db: Session = Depends(get_db)):

    subquery = (
        db.query(
            OutbreakReport.village_id,
            func.max(OutbreakReport.report_time).label("latest_time")
        )
        .group_by(OutbreakReport.village_id)
        .subquery()
    )

    latest_reports = (
        db.query(OutbreakReport)
        .join(
            subquery,
            (OutbreakReport.village_id == subquery.c.village_id) &
            (OutbreakReport.report_time == subquery.c.latest_time)
        )
        .all()
    )

    return [
        {
            "village_id": r.village_id,
            "latitude": r.village.latitude,
            "longitude": r.village.longitude,
            "risk_score": r.risk_score,
            "disease_id": r.disease_id
        }
        for r in latest_reports
    ]

@app.get("/debug/inventory")
def check_inventory(db: Session = Depends(get_db)):
    inventory = db.query(ResourceInventory).first()
    return {
        "doctors_available": inventory.doctors_available,
        "malaria_kits": inventory.malaria_kits
    }