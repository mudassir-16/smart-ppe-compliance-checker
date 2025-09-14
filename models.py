from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from config import settings

Base = declarative_base()

class PPEComplianceRecord(Base):
    __tablename__ = "ppe_compliance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, index=True)
    worker_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String)
    
    # PPE Detection Results
    helmet_detected = Column(Boolean, default=False)
    mask_detected = Column(Boolean, default=False)
    gloves_detected = Column(Boolean, default=False)
    jacket_detected = Column(Boolean, default=False)
    
    # Confidence Scores
    helmet_confidence = Column(Float, default=0.0)
    mask_confidence = Column(Float, default=0.0)
    gloves_confidence = Column(Float, default=0.0)
    jacket_confidence = Column(Float, default=0.0)
    
    # Overall Compliance
    is_compliant = Column(Boolean, default=False)
    compliance_score = Column(Float, default=0.0)
    
    # Location and Context
    location = Column(String)
    department = Column(String)
    shift = Column(String)
    
    # Alert Status
    alert_sent = Column(Boolean, default=False)
    alert_channels = Column(Text)  # JSON string of channels used
    
    # Additional Data
    raw_detection_data = Column(Text)  # JSON string of full detection results
    notes = Column(Text)

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    position = Column(String)
    email = Column(String)
    phone = Column(String)
    shift = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, index=True)
    worker_id = Column(String, index=True)
    alert_type = Column(String)  # 'non_compliance', 'critical', 'warning'
    message = Column(Text)
    channels_sent = Column(Text)  # JSON string
    sent_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


