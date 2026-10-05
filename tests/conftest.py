import os
import sys

# Guarantee repository root is on sys.path regardless of execution context
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, TrainingCenter, BeneficiaryProfile

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Baseline fixture data
    center = TrainingCenter(
        center_name="Gram Panchayat Bhawan Test",
        center_type="PANCHAYAT_BHAWAN",
        district="Bhopal",
        block="Phanda",
        village="Ratanpur",
        latitude=23.2599,
        longitude=77.4126,
        host_capacity=40,
        supported_trades=["solar_installer", "retail_business"]
    )
    db.add(center)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)