from sqlalchemy.orm import Session
from models import PPEComplianceRecord, Worker, ComplianceAlert
from schemas import ComplianceCheckRequest, ComplianceCheckResponse, PPEDetectionResult
from ppe_detector import ppe_detector
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ComplianceService:
    def __init__(self, db: Session):
        self.db = db

    def check_compliance(self, request: ComplianceCheckRequest) -> ComplianceCheckResponse:
        """Main compliance checking function"""
        try:
            # Get or create worker
            worker = self._get_or_create_worker(request)
            
            # Perform PPE detection
            detection_result = self._perform_ppe_detection(request)
            
            # Create compliance record
            record = self._create_compliance_record(request, detection_result, worker)
            
            # Check if alerts need to be sent
            alert_sent = False
            if not detection_result.is_compliant:
                alert_sent = self._send_compliance_alerts(record, detection_result)
            
            return ComplianceCheckResponse(
                success=True,
                message="Compliance check completed successfully",
                data=detection_result,
                record_id=record.id,
                alert_sent=alert_sent
            )
            
        except Exception as e:
            logger.error(f"Error in compliance check: {str(e)}")
            return ComplianceCheckResponse(
                success=False,
                message=f"Error during compliance check: {str(e)}"
            )

    def _get_or_create_worker(self, request: ComplianceCheckRequest) -> Worker:
        """Get existing worker or create new one"""
        worker = self.db.query(Worker).filter(Worker.worker_id == request.worker_id).first()
        
        if not worker:
            worker = Worker(
                worker_id=request.worker_id,
                name=request.worker_name or "Unknown",
                department=request.department or "Unknown",
                shift=request.shift
            )
            self.db.add(worker)
            self.db.commit()
            self.db.refresh(worker)
        
        return worker

    def _perform_ppe_detection(self, request: ComplianceCheckRequest) -> PPEDetectionResult:
        """Perform PPE detection based on input type"""
        if request.image_url:
            return ppe_detector.detect_ppe_from_url(request.image_url)
        elif request.image_base64:
            return ppe_detector.detect_ppe_from_base64(request.image_base64)
        else:
            logger.warning("No image provided for PPE detection")
            return PPEDetectionResult()

    def _create_compliance_record(self, request: ComplianceCheckRequest, 
                                detection_result: PPEDetectionResult, worker: Worker) -> PPEComplianceRecord:
        """Create a new compliance record in the database"""
        record = PPEComplianceRecord(
            worker_id=request.worker_id,
            worker_name=worker.name,
            helmet_detected=detection_result.helmet_detected,
            mask_detected=detection_result.mask_detected,
            gloves_detected=detection_result.gloves_detected,
            jacket_detected=detection_result.jacket_detected,
            helmet_confidence=detection_result.helmet_confidence,
            mask_confidence=detection_result.mask_confidence,
            gloves_confidence=detection_result.gloves_confidence,
            jacket_confidence=detection_result.jacket_confidence,
            is_compliant=detection_result.is_compliant,
            compliance_score=detection_result.compliance_score,
            location=request.location,
            department=request.department or worker.department,
            shift=request.shift or worker.shift,
            raw_detection_data=json.dumps(ppe_detector.get_detection_summary(detection_result))
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return record

    def _send_compliance_alerts(self, record: PPEComplianceRecord, 
                              detection_result: PPEDetectionResult) -> bool:
        """Send alerts for non-compliance"""
        try:
            from alert_service import AlertService
            alert_service = AlertService()
            
            missing_items = ppe_detector._get_missing_items(detection_result)
            message = f"PPE Non-Compliance Alert for {record.worker_name} (ID: {record.worker_id})\n"
            message += f"Missing PPE: {', '.join(missing_items)}\n"
            message += f"Compliance Score: {detection_result.compliance_score:.1f}%\n"
            message += f"Location: {record.location or 'Unknown'}\n"
            message += f"Time: {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send alerts to all configured channels
            channels_used = []
            if alert_service.send_slack_alert(message, record):
                channels_used.append("slack")
            
            if alert_service.send_email_alert(message, record):
                channels_used.append("email")
            
            if alert_service.send_whatsapp_alert(message, record):
                channels_used.append("whatsapp")
            
            # Create alert record
            alert = ComplianceAlert(
                record_id=record.id,
                worker_id=record.worker_id,
                alert_type="non_compliance",
                message=message,
                channels_sent=json.dumps(channels_used)
            )
            
            self.db.add(alert)
            record.alert_sent = True
            record.alert_channels = json.dumps(channels_used)
            self.db.commit()
            
            return len(channels_used) > 0
            
        except Exception as e:
            logger.error(f"Error sending compliance alerts: {str(e)}")
            return False

    def get_worker_compliance_history(self, worker_id: str, limit: int = 10) -> list:
        """Get compliance history for a specific worker"""
        records = self.db.query(PPEComplianceRecord)\
            .filter(PPEComplianceRecord.worker_id == worker_id)\
            .order_by(PPEComplianceRecord.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return records

    def get_department_compliance_stats(self, department: str, days: int = 7) -> dict:
        """Get compliance statistics for a department"""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        records = self.db.query(PPEComplianceRecord)\
            .filter(PPEComplianceRecord.department == department)\
            .filter(PPEComplianceRecord.timestamp >= start_date)\
            .all()
        
        total_checks = len(records)
        compliant_checks = len([r for r in records if r.is_compliant])
        non_compliant_checks = total_checks - compliant_checks
        
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'department': department,
            'total_checks': total_checks,
            'compliant_checks': compliant_checks,
            'non_compliant_checks': non_compliant_checks,
            'compliance_rate': compliance_rate,
            'period_days': days
        }

    def get_overall_compliance_stats(self, days: int = 7) -> dict:
        """Get overall compliance statistics"""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        records = self.db.query(PPEComplianceRecord)\
            .filter(PPEComplianceRecord.timestamp >= start_date)\
            .all()
        
        total_checks = len(records)
        compliant_checks = len([r for r in records if r.is_compliant])
        non_compliant_checks = total_checks - compliant_checks
        
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
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
        
        return {
            'total_checks': total_checks,
            'compliant_checks': compliant_checks,
            'non_compliant_checks': non_compliant_checks,
            'compliance_rate': compliance_rate,
            'departments': departments,
            'period_days': days
        }


