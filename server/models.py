from sqlalchemy import Column, Integer, Float, String
from database import Base

class Outbreak(Base):
    __tablename__ = "outbreaks"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer)
    village_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)
    vulnerability_index = Column(Float)
    tests_done = Column(Integer)
    positive_cases = Column(Integer)