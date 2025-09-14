import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import settings
from models import PPEComplianceRecord, Worker
import pandas as pd

# Google Sheets integration
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# Airtable integration
try:
    from airtable import Airtable
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self):
        self.google_sheets_service = None
        self.airtable_service = None
        
        # Initialize Google Sheets
        if GOOGLE_SHEETS_AVAILABLE and settings.GOOGLE_SHEETS_CREDENTIALS_FILE:
            self._init_google_sheets()
        
        # Initialize Airtable
        if AIRTABLE_AVAILABLE and settings.AIRTABLE_API_KEY:
            self._init_airtable()

    def _init_google_sheets(self):
        """Initialize Google Sheets service"""
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE, 
                scopes=scopes
            )
            self.google_sheets_service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {str(e)}")

    def _init_airtable(self):
        """Initialize Airtable service"""
        try:
            self.airtable_service = Airtable(
                settings.AIRTABLE_BASE_ID,
                settings.AIRTABLE_TABLE_NAME,
                settings.AIRTABLE_API_KEY
            )
            logger.info("Airtable service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Airtable: {str(e)}")

    def log_compliance_record(self, record: PPEComplianceRecord) -> Dict[str, bool]:
        """Log compliance record to external storage systems"""
        results = {}
        
        # Log to Google Sheets
        if self.google_sheets_service:
            results['google_sheets'] = self._log_to_google_sheets(record)
        
        # Log to Airtable
        if self.airtable_service:
            results['airtable'] = self._log_to_airtable(record)
        
        return results

    def _log_to_google_sheets(self, record: PPEComplianceRecord) -> bool:
        """Log compliance record to Google Sheets"""
        try:
            # Prepare data row
            row_data = [
                record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                record.worker_id,
                record.worker_name or '',
                record.department or '',
                record.location or '',
                record.shift or '',
                'Yes' if record.helmet_detected else 'No',
                f"{record.helmet_confidence:.2f}",
                'Yes' if record.mask_detected else 'No',
                f"{record.mask_confidence:.2f}",
                'Yes' if record.gloves_detected else 'No',
                f"{record.gloves_confidence:.2f}",
                'Yes' if record.jacket_detected else 'No',
                f"{record.jacket_confidence:.2f}",
                'Yes' if record.is_compliant else 'No',
                f"{record.compliance_score:.2f}",
                'Yes' if record.alert_sent else 'No',
                record.alert_channels or '',
                record.notes or ''
            ]
            
            # Append to sheet
            body = {
                'values': [row_data]
            }
            
            result = self.google_sheets_service.spreadsheets().values().append(
                spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                range='Sheet1!A:S',  # Adjust range as needed
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Record logged to Google Sheets: {result.get('updates', {}).get('updatedRows', 0)} rows updated")
            return True
            
        except Exception as e:
            logger.error(f"Error logging to Google Sheets: {str(e)}")
            return False

    def _log_to_airtable(self, record: PPEComplianceRecord) -> bool:
        """Log compliance record to Airtable"""
        try:
            # Prepare data for Airtable
            airtable_data = {
                'Worker ID': record.worker_id,
                'Worker Name': record.worker_name or '',
                'Timestamp': record.timestamp.isoformat(),
                'Department': record.department or '',
                'Location': record.location or '',
                'Shift': record.shift or '',
                'Helmet Detected': record.helmet_detected,
                'Helmet Confidence': record.helmet_confidence,
                'Mask Detected': record.mask_detected,
                'Mask Confidence': record.mask_confidence,
                'Gloves Detected': record.gloves_detected,
                'Gloves Confidence': record.gloves_confidence,
                'Jacket Detected': record.jacket_detected,
                'Jacket Confidence': record.jacket_confidence,
                'Is Compliant': record.is_compliant,
                'Compliance Score': record.compliance_score,
                'Alert Sent': record.alert_sent,
                'Alert Channels': record.alert_channels or '',
                'Notes': record.notes or ''
            }
            
            # Insert record
            result = self.airtable_service.insert(airtable_data)
            logger.info(f"Record logged to Airtable: {result.get('id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging to Airtable: {str(e)}")
            return False

    def sync_workers_to_sheets(self, workers: List[Worker]) -> bool:
        """Sync worker data to Google Sheets"""
        if not self.google_sheets_service:
            return False
        
        try:
            # Prepare worker data
            worker_data = []
            for worker in workers:
                worker_data.append([
                    worker.worker_id,
                    worker.name,
                    worker.department,
                    worker.position or '',
                    worker.email or '',
                    worker.phone or '',
                    worker.shift or '',
                    'Active' if worker.is_active else 'Inactive',
                    worker.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    worker.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # Clear existing data and add new data
            body = {
                'values': worker_data
            }
            
            # Clear the sheet first
            self.google_sheets_service.spreadsheets().values().clear(
                spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                range='Workers!A:J'
            ).execute()
            
            # Add new data
            result = self.google_sheets_service.spreadsheets().values().update(
                spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                range='Workers!A:J',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Workers synced to Google Sheets: {result.get('updatedRows', 0)} rows updated")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing workers to Google Sheets: {str(e)}")
            return False

    def sync_workers_to_airtable(self, workers: List[Worker]) -> bool:
        """Sync worker data to Airtable"""
        if not self.airtable_service:
            return False
        
        try:
            # Get existing records
            existing_records = self.airtable_service.get_all()
            existing_worker_ids = {record['fields'].get('Worker ID') for record in existing_records}
            
            # Prepare worker data
            for worker in workers:
                worker_data = {
                    'Worker ID': worker.worker_id,
                    'Name': worker.name,
                    'Department': worker.department,
                    'Position': worker.position or '',
                    'Email': worker.email or '',
                    'Phone': worker.phone or '',
                    'Shift': worker.shift or '',
                    'Status': 'Active' if worker.is_active else 'Inactive',
                    'Created At': worker.created_at.isoformat(),
                    'Updated At': worker.updated_at.isoformat()
                }
                
                if worker.worker_id in existing_worker_ids:
                    # Update existing record
                    record_id = next(
                        record['id'] for record in existing_records 
                        if record['fields'].get('Worker ID') == worker.worker_id
                    )
                    self.airtable_service.update(record_id, worker_data)
                else:
                    # Create new record
                    self.airtable_service.insert(worker_data)
            
            logger.info(f"Workers synced to Airtable: {len(workers)} records processed")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing workers to Airtable: {str(e)}")
            return False

    def export_compliance_report(self, records: List[PPEComplianceRecord], 
                               format: str = 'csv') -> Optional[str]:
        """Export compliance records to file"""
        try:
            # Convert records to DataFrame
            data = []
            for record in records:
                data.append({
                    'Timestamp': record.timestamp,
                    'Worker ID': record.worker_id,
                    'Worker Name': record.worker_name,
                    'Department': record.department,
                    'Location': record.location,
                    'Shift': record.shift,
                    'Helmet Detected': record.helmet_detected,
                    'Helmet Confidence': record.helmet_confidence,
                    'Mask Detected': record.mask_detected,
                    'Mask Confidence': record.mask_confidence,
                    'Gloves Detected': record.gloves_detected,
                    'Gloves Confidence': record.gloves_confidence,
                    'Jacket Detected': record.jacket_detected,
                    'Jacket Confidence': record.jacket_confidence,
                    'Is Compliant': record.is_compliant,
                    'Compliance Score': record.compliance_score,
                    'Alert Sent': record.alert_sent,
                    'Alert Channels': record.alert_channels,
                    'Notes': record.notes
                })
            
            df = pd.DataFrame(data)
            
            # Export based on format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"compliance_report_{timestamp}.{format}"
            
            if format.lower() == 'csv':
                df.to_csv(filename, index=False)
            elif format.lower() == 'excel':
                df.to_excel(filename, index=False)
            elif format.lower() == 'json':
                df.to_json(filename, orient='records', date_format='iso')
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
            
            logger.info(f"Compliance report exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting compliance report: {str(e)}")
            return None

    def get_compliance_analytics(self, records: List[PPEComplianceRecord]) -> Dict[str, Any]:
        """Generate analytics from compliance records"""
        try:
            if not records:
                return {}
            
            # Basic statistics
            total_records = len(records)
            compliant_records = len([r for r in records if r.is_compliant])
            non_compliant_records = total_records - compliant_records
            compliance_rate = (compliant_records / total_records * 100) if total_records > 0 else 0
            
            # PPE item statistics
            ppe_stats = {
                'helmet': {
                    'detected': len([r for r in records if r.helmet_detected]),
                    'rate': len([r for r in records if r.helmet_detected]) / total_records * 100
                },
                'mask': {
                    'detected': len([r for r in records if r.mask_detected]),
                    'rate': len([r for r in records if r.mask_detected]) / total_records * 100
                },
                'gloves': {
                    'detected': len([r for r in records if r.gloves_detected]),
                    'rate': len([r for r in records if r.gloves_detected]) / total_records * 100
                },
                'jacket': {
                    'detected': len([r for r in records if r.jacket_detected]),
                    'rate': len([r for r in records if r.jacket_detected]) / total_records * 100
                }
            }
            
            # Department statistics
            departments = {}
            for record in records:
                dept = record.department or 'Unknown'
                if dept not in departments:
                    departments[dept] = {'total': 0, 'compliant': 0}
                departments[dept]['total'] += 1
                if record.is_compliant:
                    departments[dept]['compliant'] += 1
            
            # Calculate department compliance rates
            for dept in departments:
                total = departments[dept]['total']
                compliant = departments[dept]['compliant']
                departments[dept]['rate'] = (compliant / total * 100) if total > 0 else 0
            
            # Time-based analysis
            records_by_hour = {}
            for record in records:
                hour = record.timestamp.hour
                if hour not in records_by_hour:
                    records_by_hour[hour] = {'total': 0, 'compliant': 0}
                records_by_hour[hour]['total'] += 1
                if record.is_compliant:
                    records_by_hour[hour]['compliant'] += 1
            
            # Calculate hourly compliance rates
            for hour in records_by_hour:
                total = records_by_hour[hour]['total']
                compliant = records_by_hour[hour]['compliant']
                records_by_hour[hour]['rate'] = (compliant / total * 100) if total > 0 else 0
            
            return {
                'summary': {
                    'total_records': total_records,
                    'compliant_records': compliant_records,
                    'non_compliant_records': non_compliant_records,
                    'compliance_rate': compliance_rate
                },
                'ppe_statistics': ppe_stats,
                'department_statistics': departments,
                'hourly_statistics': records_by_hour,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance analytics: {str(e)}")
            return {}

# Global data storage service instance
data_storage = DataStorageService()


