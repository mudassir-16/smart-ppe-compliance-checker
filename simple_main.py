from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import os
import base64
from datetime import datetime, timedelta
import json
import random

# Import our modules
from models import get_db, create_tables, PPEComplianceRecord, Worker, ComplianceAlert
from schemas import (
    ComplianceCheckRequest, ComplianceCheckResponse, WorkerCreate, WorkerResponse,
    ComplianceRecordResponse, DashboardStats, WebhookPayload, AlertRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart PPE Compliance Checker - Demo Version",
    description="Real-time PPE compliance detection and monitoring system (Demo Mode)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "mode": "demo"}

# Mock PPE Detection for Demo
def mock_ppe_detection() -> Dict[str, Any]:
    """Mock PPE detection for demo purposes"""
    # Simulate realistic detection results
    helmet_detected = random.choice([True, True, True, False])  # 75% chance
    mask_detected = random.choice([True, True, False, False])   # 50% chance
    gloves_detected = random.choice([True, True, True, False])  # 75% chance
    jacket_detected = random.choice([True, True, False, False]) # 50% chance
    
    helmet_confidence = random.uniform(0.7, 0.95) if helmet_detected else 0.0
    mask_confidence = random.uniform(0.6, 0.9) if mask_detected else 0.0
    gloves_confidence = random.uniform(0.7, 0.9) if gloves_detected else 0.0
    jacket_confidence = random.uniform(0.6, 0.85) if jacket_detected else 0.0
    
    # Calculate compliance
    detected_count = sum([helmet_detected, mask_detected, gloves_detected, jacket_detected])
    compliance_score = (detected_count / 4) * 100
    is_compliant = compliance_score >= 75.0
    
    return {
        "helmet_detected": helmet_detected,
        "mask_detected": mask_detected,
        "gloves_detected": gloves_detected,
        "jacket_detected": jacket_detected,
        "helmet_confidence": helmet_confidence,
        "mask_confidence": mask_confidence,
        "gloves_confidence": gloves_confidence,
        "jacket_confidence": jacket_confidence,
        "is_compliant": is_compliant,
        "compliance_score": compliance_score
    }

# PPE Compliance Check Endpoints
@app.post("/api/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: ComplianceCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Main endpoint for PPE compliance checking (Demo Mode)"""
    try:
        # Get or create worker
        worker = db.query(Worker).filter(Worker.worker_id == request.worker_id).first()
        
        if not worker:
            worker = Worker(
                worker_id=request.worker_id,
                name=request.worker_name or "Unknown",
                department=request.department or "Unknown",
                shift=request.shift
            )
            db.add(worker)
            db.commit()
            db.refresh(worker)
        
        # Mock PPE detection
        detection_result = mock_ppe_detection()
        
        # Create compliance record
        record = PPEComplianceRecord(
            worker_id=request.worker_id,
            worker_name=worker.name,
            helmet_detected=detection_result["helmet_detected"],
            mask_detected=detection_result["mask_detected"],
            gloves_detected=detection_result["gloves_detected"],
            jacket_detected=detection_result["jacket_detected"],
            helmet_confidence=detection_result["helmet_confidence"],
            mask_confidence=detection_result["mask_confidence"],
            gloves_confidence=detection_result["gloves_confidence"],
            jacket_confidence=detection_result["jacket_confidence"],
            is_compliant=detection_result["is_compliant"],
            compliance_score=detection_result["compliance_score"],
            location=request.location,
            department=request.department or worker.department,
            shift=request.shift or worker.shift,
            raw_detection_data=json.dumps(detection_result)
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        # Mock alert sending
        alert_sent = False
        if not detection_result["is_compliant"]:
            alert_sent = True
            logger.info(f"Mock alert sent for non-compliant worker: {worker.name}")
        
        return ComplianceCheckResponse(
            success=True,
            message="Compliance check completed successfully (Demo Mode)",
            data=detection_result,
            record_id=record.id,
            alert_sent=alert_sent
        )
        
    except Exception as e:
        logger.error(f"Error in compliance check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compliance/check-upload")
async def check_compliance_upload(
    background_tasks: BackgroundTasks,
    worker_id: str = Form(...),
    worker_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    shift: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Check compliance from uploaded image file (Demo Mode)"""
    try:
        # Read image data (we'll just use it for demo purposes)
        image_data = await file.read()
        
        # Create request
        request = ComplianceCheckRequest(
            worker_id=worker_id,
            worker_name=worker_name,
            location=location,
            department=department,
            shift=shift,
            image_base64=base64.b64encode(image_data).decode('utf-8')
        )
        
        # Use the same logic as the regular check endpoint
        return await check_compliance(request, background_tasks, db)
        
    except Exception as e:
        logger.error(f"Error in compliance check upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Worker Management Endpoints
@app.post("/api/workers", response_model=WorkerResponse)
async def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker"""
    try:
        # Check if worker already exists
        existing_worker = db.query(Worker).filter(Worker.worker_id == worker.worker_id).first()
        if existing_worker:
            raise HTTPException(status_code=400, detail="Worker ID already exists")
        
        # Create new worker
        db_worker = Worker(**worker.dict())
        db.add(db_worker)
        db.commit()
        db.refresh(db_worker)
        
        return db_worker
        
    except Exception as e:
        logger.error(f"Error creating worker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workers", response_model=List[WorkerResponse])
async def get_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of workers"""
    try:
        workers = db.query(Worker).offset(skip).limit(limit).all()
        return workers
        
    except Exception as e:
        logger.error(f"Error getting workers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workers/{worker_id}", response_model=WorkerResponse)
async def get_worker(worker_id: str, db: Session = Depends(get_db)):
    """Get specific worker by ID"""
    try:
        worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        return worker
        
    except Exception as e:
        logger.error(f"Error getting worker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance Records Endpoints
@app.get("/api/compliance/records", response_model=List[ComplianceRecordResponse])
async def get_compliance_records(
    skip: int = 0,
    limit: int = 100,
    worker_id: Optional[str] = None,
    department: Optional[str] = None,
    is_compliant: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get compliance records with optional filters"""
    try:
        query = db.query(PPEComplianceRecord)
        
        if worker_id:
            query = query.filter(PPEComplianceRecord.worker_id == worker_id)
        if department:
            query = query.filter(PPEComplianceRecord.department == department)
        if is_compliant is not None:
            query = query.filter(PPEComplianceRecord.is_compliant == is_compliant)
        
        records = query.order_by(PPEComplianceRecord.timestamp.desc()).offset(skip).limit(limit).all()
        return records
        
    except Exception as e:
        logger.error(f"Error getting compliance records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/records/{record_id}", response_model=ComplianceRecordResponse)
async def get_compliance_record(record_id: int, db: Session = Depends(get_db)):
    """Get specific compliance record by ID"""
    try:
        record = db.query(PPEComplianceRecord).filter(PPEComplianceRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return record
        
    except Exception as e:
        logger.error(f"Error getting compliance record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard and Analytics Endpoints
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: int = 7,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.timestamp >= start_date
        )
        
        if department:
            query = query.filter(PPEComplianceRecord.department == department)
        
        records = query.all()
        
        total_checks = len(records)
        compliant_checks = len([r for r in records if r.is_compliant])
        non_compliant_checks = total_checks - compliant_checks
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Get today's stats
        today = datetime.utcnow().date()
        today_records = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.timestamp >= today
        ).all()
        
        today_total = len(today_records)
        today_compliant = len([r for r in today_records if r.is_compliant])
        today_non_compliant = today_total - today_compliant
        today_rate = (today_compliant / today_total * 100) if today_total > 0 else 0
        
        # Department breakdown
        departments = {}
        for record in records:
            dept = record.department or 'Unknown'
            if dept not in departments:
                departments[dept] = {'total': 0, 'compliant': 0}
            departments[dept]['total'] += 1
            if record.is_compliant:
                departments[dept]['compliant'] += 1
        
        # Calculate department rates
        for dept in departments:
            total = departments[dept]['total']
            compliant = departments[dept]['compliant']
            departments[dept]['rate'] = (compliant / total * 100) if total > 0 else 0
        
        # Get recent violations
        recent_violations = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.is_compliant == False
        ).order_by(PPEComplianceRecord.timestamp.desc()).limit(10).all()
        
        return DashboardStats(
            total_checks=total_checks,
            compliant_checks=compliant_checks,
            non_compliant_checks=non_compliant_checks,
            compliance_rate=compliance_rate,
            today_checks=today_total,
            today_compliant=today_compliant,
            today_non_compliant=today_non_compliant,
            today_compliance_rate=today_rate,
            department_stats=departments,
            recent_violations=recent_violations
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook endpoints for n8n integration
@app.post("/api/webhooks/compliance")
async def compliance_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook endpoint for n8n compliance workflow (Demo Mode)"""
    try:
        logger.info(f"Received webhook: {payload.event_type}")
        
        if payload.event_type == "compliance_check":
            # Extract data from webhook payload
            data = payload.data
            
            # Create compliance check request
            request = ComplianceCheckRequest(
                worker_id=data.get("worker_id", ""),
                worker_name=data.get("worker_name"),
                location=data.get("location"),
                department=data.get("department"),
                shift=data.get("shift"),
                image_url=data.get("image_url"),
                image_base64=data.get("image_base64")
            )
            
            # Process compliance check
            result = await check_compliance(request, background_tasks, db)
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data.dict() if result.data else None,
                "record_id": result.record_id,
                "alert_sent": result.alert_sent
            }
        
        else:
            return {"success": False, "message": f"Unknown event type: {payload.event_type}"}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


