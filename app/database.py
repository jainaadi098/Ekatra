import os
from datetime import datetime
from typing import Generator
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pmajay_production.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BeneficiaryProfile(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    phone_number = Column(String(16), index=True, nullable=True)
    full_name = Column(String(128), default="Anonymous Artisan")
    age = Column(Integer, nullable=True)
    gender = Column(String(16), nullable=True)

    # Location Metadata
    village = Column(String(128), default="रतनपुर", nullable=False)
    block = Column(String(128), default="Phanda", nullable=False)
    district = Column(String(128), default="Bhopal", nullable=False)
    latitude = Column(Float, default=23.2599, nullable=False)
    longitude = Column(Float, default=77.4126, nullable=False)

    # Dialect & Intake Metadata
    preferred_dialect = Column(String(32), default="hindi")
    voice_consent_granted = Column(Boolean, default=False)
    formal_education = Column(String(64), default="No Formal Education")

    # Work Background & Aspiration
    current_occupation = Column(String(128), nullable=True)
    aspired_trade = Column(String(128), default="solar_installer", index=True, nullable=False)
    selected_course_title = Column(String(256), nullable=True)
    selected_course_id = Column(String(64), nullable=True)

    # Mobility Constraints
    available_months = Column(JSON, default=lambda: ["november", "december"])
    mobility_radius_km = Column(Float, default=5.0)

    # Oral RPL Diagnostic Scoring
    oral_rpl_score = Column(Float, default=0.0)
    diagnosed_skill_gaps = Column(JSON, default=list)

    # Cohort Enrollment Gate
    enrollment_confirmed = Column(Boolean, default=False)
    batch_id = Column(Integer, ForeignKey("training_batches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("TrainingBatch", back_populates="enrolled_candidates")


class TrainingCenter(Base):
    __tablename__ = "training_centers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    center_name = Column(String(256), nullable=False)
    center_type = Column(String(64), nullable=False)
    district = Column(String(128), index=True, nullable=False)
    block = Column(String(128), index=True, nullable=False)
    village = Column(String(128), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    host_capacity = Column(Integer, default=40)
    supported_trades = Column(JSON, default=list)


class TrainingBatch(Base):
    __tablename__ = "training_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_code = Column(String(64), unique=True, index=True, nullable=False)
    trade_name = Column(String(128), index=True, nullable=False)
    center_id = Column(Integer, ForeignKey("training_centers.id"), nullable=False)
    target_capacity = Column(Integer, default=20)
    current_count = Column(Integer, default=0)
    status = Column(String(32), default="FORMING")
    scheduled_season = Column(String(64), default="Post-Harvest (Oct-Nov)")
    created_at = Column(DateTime, default=datetime.utcnow)

    center = relationship("TrainingCenter")
    enrolled_candidates = relationship("BeneficiaryProfile", back_populates="batch")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(TrainingCenter).count() == 0:
        centers = [
            TrainingCenter(
                center_name="Gram Panchayat Bhawan Ratanpur",
                center_type="PANCHAYAT_BHAWAN",
                district="Bhopal",
                block="Phanda",
                village="Ratanpur",
                latitude=23.2599,
                longitude=77.4126,
                host_capacity=40,
                supported_trades=["solar_installer", "tailoring", "electrician"]
            ),
            TrainingCenter(
                center_name="PMKK Skill Hub Mandideep",
                center_type="PMKK",
                district="Bhopal",
                block="Mandideep",
                village="Industrial Sector A",
                latitude=23.0722,
                longitude=77.5186,
                host_capacity=100,
                supported_trades=["solar_installer", "electrician", "automotive"]
            ),
            TrainingCenter(
                center_name="RSETI Center Berasia",
                center_type="RSETI",
                district="Bhopal",
                block="Berasia",
                village="Berasia Central",
                latitude=23.6334,
                longitude=77.4338,
                host_capacity=60,
                supported_trades=["tailoring", "vermicompost", "masonry"]
            )
        ]
        db.add_all(centers)
        db.commit()

        # Seed synthetic existing cohort (14 baseline candidates in Ratanpur cluster)
        synthetic_pool = [
            BeneficiaryProfile(
                session_id=f"seed-artisan-{i}",
                full_name=f"Artisan {i}",
                village="रतनपुर",
                block="Phanda",
                district="Bhopal",
                latitude=23.2599 + (i * 0.0007),
                longitude=77.4126 + (i * 0.0006),
                preferred_dialect="hindi",
                voice_consent_granted=True,
                formal_education="5th Pass",
                aspired_trade="solar_installer",
                selected_course_title="Solar PV Installer (Suryamitra)",
                selected_course_id="ELE/Q5901",
                mobility_radius_km=5.0,
                oral_rpl_score=0.85,
                enrollment_confirmed=True
            )
            for i in range(1, 15)
        ]
        db.add_all(synthetic_pool)
        db.commit()

    db.close()