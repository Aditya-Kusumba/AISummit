#model.py

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    population = Column(Integer)
    vulnerability_index = Column(Float)  # 0 to 1 scale

    last_visit_date = Column(DateTime)

    outbreaks = relationship("OutbreakReport", back_populates="village")
    allocations = relationship("AllocationDetail", back_populates="village")

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    severity_weight = Column(Float)   # used in risk scoring

    outbreaks = relationship("OutbreakReport", back_populates="disease")

class OutbreakReport(Base):
    __tablename__ = "outbreak_reports"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(Integer, ForeignKey("villages.id"))
    disease_id = Column(Integer, ForeignKey("diseases.id"))

    report_time = Column(DateTime, default=datetime.utcnow)

    tests_done = Column(Integer)
    positive_cases = Column(Integer)

    positivity_rate = Column(Float)
    spread_velocity = Column(Float)   # change since last report
    risk_score = Column(Float)

    reporter_type = Column(String)    # dashboard / sms / van
    confidence_score = Column(Float)

    village = relationship("Village", back_populates="outbreaks")
    disease = relationship("Disease", back_populates="outbreaks")

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True)

    from_village_id = Column(Integer)
    to_village_id = Column(Integer)

    distance_km = Column(Float)
    road_type = Column(String)  # asphalt, gravel, mud
    reliability_score = Column(Float)  # 0–1 based on history

    last_updated = Column(DateTime, default=datetime.utcnow)

class ResourceInventory(Base):
    __tablename__ = "resource_inventory"

    id = Column(Integer, primary_key=True)

    doctors_available = Column(Integer)
    nurses_available = Column(Integer)

    malaria_kits = Column(Integer)
    dengue_kits = Column(Integer)
    cholera_kits = Column(Integer)

    vaccines = Column(Integer)

    last_updated = Column(DateTime, default=datetime.utcnow)

class MobileUnit(Base):
    __tablename__ = "mobile_units"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    capacity_doctors = Column(Integer)
    capacity_kits = Column(Integer)

    is_active = Column(Boolean, default=True)

class AllocationBatch(Base):
    __tablename__ = "allocation_batches"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mode = Column(String)  # online / offline
    total_villages_selected = Column(Integer)

    allocations = relationship("AllocationDetail", back_populates="batch")
    routes = relationship("RoutePlan", back_populates="batch")

class AllocationDetail(Base):
    __tablename__ = "allocation_details"

    id = Column(Integer, primary_key=True)

    batch_id = Column(Integer, ForeignKey("allocation_batches.id"))
    village_id = Column(Integer, ForeignKey("villages.id"))

    doctors_allocated = Column(Integer)
    nurses_allocated = Column(Integer)

    malaria_kits_allocated = Column(Integer)
    dengue_kits_allocated = Column(Integer)

    priority_score = Column(Float)

    batch = relationship("AllocationBatch", back_populates="allocations")
    village = relationship("Village", back_populates="allocations")

class RoutePlan(Base):
    __tablename__ = "route_plans"

    id = Column(Integer, primary_key=True)

    batch_id = Column(Integer, ForeignKey("allocation_batches.id"))
    mobile_unit_id = Column(Integer, ForeignKey("mobile_units.id"))

    route_sequence = Column(String)  # JSON string of village IDs
    estimated_distance = Column(Float)
    estimated_time_minutes = Column(Integer)

    batch = relationship("AllocationBatch", back_populates="routes")