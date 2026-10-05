import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Index
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ekatra_master.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BeneficiaryProfile(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    
    # Slot 1: Name
    full_name = Column(String(128), index=True, nullable=False)
    
    # Slots 2 & 3: District & Tehsil/Block (MP Focus)
    state = Column(String(64), default="Madhya Pradesh")
    district = Column(String(64), index=True, nullable=False)
    block = Column(String(64), index=True, nullable=False)
    village = Column(String(128), index=True, nullable=False)
    latitude = Column(Float, default=23.2599)
    longitude = Column(Float, default=77.4126)
    
    # Slot 4: Schooling & NSQF mapping
    formal_education = Column(String(64), nullable=False)
    nsqf_eligible_level = Column(Integer, default=4)
    
    # Slot 5: Current Work
    current_occupation = Column(String(128), nullable=False)
    oral_rpl_score = Column(Float, default=0.95)
    
    # Slot 6: Desire Trade
    aspired_trade = Column(String(64), index=True, nullable=False)
    selected_course_title = Column(String(256))
    selected_course_id = Column(String(64), index=True)
    
    # Slot 7: Job / Setup
    livelihood_intent = Column(String(32), default="SETUP")  # SETUP vs JOB
    
    # Slot 8: Time Limit
    availability_window = Column(String(64), default="Morning (2-4 Hours)")
    
    # Slot 9: SC Status
    sc_status_verified = Column(Boolean, default=True, index=True)
    
    # Spatial Calculation (15 km rule)
    allocated_center_name = Column(String(128))
    distance_to_center_km = Column(Float, default=3.2)
    radius_status = Column(String(16), default="GREEN")  # GREEN (<=15km) | RED (>15km)
    
    enrollment_confirmed = Column(Boolean, default=False, index=True)

    __table_args__ = (
        Index("ix_beneficiary_search", "full_name", "district", "block", "aspired_trade"),
    )


class TrainingCenterNode(Base):
    __tablename__ = "training_centers"

    id = Column(Integer, primary_key=True, index=True)
    center_name = Column(String(128), nullable=False)
    center_type = Column(String(64), default="PANCHAYAT_BHAWAN")
    state = Column(String(64), default="Madhya Pradesh")
    district = Column(String(64), index=True)
    block = Column(String(64), index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    target_capacity = Column(Integer, default=20)
    current_enrolled = Column(Integer, default=14)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(TrainingCenterNode).count() == 0:
        centers = [
            TrainingCenterNode(
                center_name="Gram Panchayat Bhawan Ratanpur",
                center_type="PANCHAYAT_BHAWAN",
                state="Madhya Pradesh",
                district="Bhopal",
                block="Phanda",
                latitude=23.2599,
                longitude=77.4126,
                current_enrolled=14
            ),
            TrainingCenterNode(
                center_name="Janpad Skill Hub Berasia",
                center_type="JANPAD_KENDRA",
                state="Madhya Pradesh",
                district="Bhopal",
                block="Berasia",
                latitude=23.6338,
                longitude=77.4334,
                current_enrolled=11
            ),
            TrainingCenterNode(
                center_name="Gram Panchayat Bhawan Mandideep",
                center_type="PANCHAYAT_BHAWAN",
                state="Madhya Pradesh",
                district="Raisen",
                block="Mandideep",
                latitude=23.0722,
                longitude=77.5186,
                current_enrolled=8
            )
        ]
        db.add_all(centers)
        db.commit()
    db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()