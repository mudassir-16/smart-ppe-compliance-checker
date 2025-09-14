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

# Import our modules
from models import get_db, create_tables, PPEComplianceRecord, Worker, ComplianceAlert
from schemas import (
    ComplianceCheckRequest, ComplianceCheckResponse, WorkerCreate, WorkerResponse,
    ComplianceRecordResponse, DashboardStats, WebhookPayload, AlertRequest
)
from compliance_service import ComplianceService
from alert_service import AlertService
from data_storage import data_storage
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart PPE Compliance Checker",
    description="Real-time PPE compliance detection and monitoring system",
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

# Initialize services
alert_service = AlertService()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# PPE Compliance Check Endpoints
@app.post("/api/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: ComplianceCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Main endpoint for PPE compliance checking"""
    try:
        compliance_service = ComplianceService(db)
        result = compliance_service.check_compliance(request)
        
        # Log to external storage in background
        if result.success and result.record_id:
            record = db.query(PPEComplianceRecord).filter(
                PPEComplianceRecord.id == result.record_id
            ).first()
            if record:
                background_tasks.add_task(data_storage.log_compliance_record, record)
        
        return result
        
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
    """Check compliance from uploaded image file"""
    try:
        # Read and encode image
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create request
        request = ComplianceCheckRequest(
            worker_id=worker_id,
            worker_name=worker_name,
            location=location,
            department=department,
            shift=shift,
            image_base64=image_base64
        )
        
        # Check compliance
        compliance_service = ComplianceService(db)
        result = compliance_service.check_compliance(request)
        
        # Log to external storage in background
        if result.success and result.record_id:
            record = db.query(PPEComplianceRecord).filter(
                PPEComplianceRecord.id == result.record_id
            ).first()
            if record:
                background_tasks.add_task(data_storage.log_compliance_record, record)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in compliance check upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook endpoints for n8n integration
@app.post("/api/webhooks/compliance")
async def compliance_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook endpoint for n8n compliance workflow"""
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
            compliance_service = ComplianceService(db)
            result = compliance_service.check_compliance(request)
            
            # Log to external storage in background
            if result.success and result.record_id:
                record = db.query(PPEComplianceRecord).filter(
                    PPEComplianceRecord.id == result.record_id
                ).first()
                if record:
                    background_tasks.add_task(data_storage.log_compliance_record, record)
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data.dict() if result.data else None,
                "record_id": result.record_id,
                "alert_sent": result.alert_sent
            }
        
        elif payload.event_type == "manual_alert":
            # Send manual alert
            alert_data = payload.data
            record_id = alert_data.get("record_id")
            
            if record_id:
                record = db.query(PPEComplianceRecord).filter(
                    PPEComplianceRecord.id == record_id
                ).first()
                
                if record:
                    message = alert_data.get("message", "Manual alert triggered")
                    channels = alert_data.get("channels", ["slack", "email"])
                    
                    results = alert_service.send_custom_alert(message, channels, record)
                    return {"success": True, "alert_results": results}
            
            return {"success": False, "message": "Record not found"}
        
        else:
            return {"success": False, "message": f"Unknown event type: {payload.event_type}"}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
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
        compliance_service = ComplianceService(db)
        
        if department:
            stats = compliance_service.get_department_compliance_stats(department, days)
        else:
            stats = compliance_service.get_overall_compliance_stats(days)
        
        # Get today's stats
        today = datetime.utcnow().date()
        today_records = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.timestamp >= today
        ).all()
        
        today_total = len(today_records)
        today_compliant = len([r for r in today_records if r.is_compliant])
        today_non_compliant = today_total - today_compliant
        today_rate = (today_compliant / today_total * 100) if today_total > 0 else 0
        
        # Get recent violations
        recent_violations = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.is_compliant == False
        ).order_by(PPEComplianceRecord.timestamp.desc()).limit(10).all()
        
        return DashboardStats(
            total_checks=stats['total_checks'],
            compliant_checks=stats['compliant_checks'],
            non_compliant_checks=stats['non_compliant_checks'],
            compliance_rate=stats['compliance_rate'],
            today_checks=today_total,
            today_compliant=today_compliant,
            today_non_compliant=today_non_compliant,
            today_compliance_rate=today_rate,
            department_stats=stats.get('departments', {}),
            recent_violations=recent_violations
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/compliance")
async def get_compliance_analytics(
    days: int = 30,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get detailed compliance analytics"""
    try:
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.timestamp >= start_date
        )
        
        if department:
            query = query.filter(PPEComplianceRecord.department == department)
        
        records = query.all()
        
        # Generate analytics
        analytics = data_storage.get_compliance_analytics(records)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting compliance analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Alert Management Endpoints
@app.post("/api/alerts/send")
async def send_alert(alert_request: AlertRequest, db: Session = Depends(get_db)):
    """Send manual alert"""
    try:
        record = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.id == alert_request.record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        results = alert_service.send_custom_alert(
            alert_request.message,
            alert_request.channels,
            record
        )
        
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Export Endpoints
@app.get("/api/export/compliance")
async def export_compliance_data(
    format: str = "csv",
    days: int = 30,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export compliance data"""
    try:
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PPEComplianceRecord).filter(
            PPEComplianceRecord.timestamp >= start_date
        )
        
        if department:
            query = query.filter(PPEComplianceRecord.department == department)
        
        records = query.all()
        
        # Export data
        filename = data_storage.export_compliance_report(records, format)
        
        if filename and os.path.exists(filename):
            return FileResponse(
                filename,
                media_type='application/octet-stream',
                filename=filename
            )
        else:
            raise HTTPException(status_code=500, detail="Export failed")
        
    except Exception as e:
        logger.error(f"Error exporting compliance data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Sync Endpoints
@app.post("/api/sync/workers")
async def sync_workers_to_external(db: Session = Depends(get_db)):
    """Sync workers to external storage systems"""
    try:
        workers = db.query(Worker).all()
        
        results = {}
        results['google_sheets'] = data_storage.sync_workers_to_sheets(workers)
        results['airtable'] = data_storage.sync_workers_to_airtable(workers)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"Error syncing workers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )


