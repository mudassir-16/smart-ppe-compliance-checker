from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PPEDetectionResult(BaseModel):
    helmet_detected: bool = False
    mask_detected: bool = False
    gloves_detected: bool = False
    jacket_detected: bool = False
    
    helmet_confidence: float = 0.0
    mask_confidence: float = 0.0
    gloves_confidence: float = 0.0
    jacket_confidence: float = 0.0
    
    is_compliant: bool = False
    compliance_score: float = 0.0

class RoboflowDetection(BaseModel):
    class_name: str
    confidence: float
    x: float
    y: float
    width: float
    height: float

class RoboflowResponse(BaseModel):
    predictions: List[RoboflowDetection]
    image: str

class ComplianceCheckRequest(BaseModel):
    worker_id: str
    worker_name: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    shift: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None

class ComplianceCheckResponse(BaseModel):
    success: bool
    message: str
    data: Optional[PPEDetectionResult] = None
    record_id: Optional[int] = None
    alert_sent: bool = False

class WorkerCreate(BaseModel):
    worker_id: str
    name: str
    department: str
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    shift: Optional[str] = None

class WorkerResponse(BaseModel):
    id: int
    worker_id: str
    name: str
    department: str
    position: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    shift: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ComplianceRecordResponse(BaseModel):
    id: int
    worker_id: str
    worker_name: Optional[str]
    timestamp: datetime
    image_path: Optional[str]
    helmet_detected: bool
    mask_detected: bool
    gloves_detected: bool
    jacket_detected: bool
    helmet_confidence: float
    mask_confidence: float
    gloves_confidence: float
    jacket_confidence: float
    is_compliant: bool
    compliance_score: float
    location: Optional[str]
    department: Optional[str]
    shift: Optional[str]
    alert_sent: bool

class AlertRequest(BaseModel):
    record_id: int
    worker_id: str
    alert_type: str = "non_compliance"
    message: str
    channels: List[str] = ["slack", "email"]

class DashboardStats(BaseModel):
    total_checks: int
    compliant_checks: int
    non_compliant_checks: int
    compliance_rate: float
    today_checks: int
    today_compliant: int
    today_non_compliant: int
    today_compliance_rate: float
    department_stats: Dict[str, Dict[str, Any]]
    recent_violations: List[ComplianceRecordResponse]

class WebhookPayload(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
