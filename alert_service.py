import requests
import json
import logging
from typing import Optional, Dict, Any
from config import settings
from models import PPEComplianceRecord
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from twilio.rest import Client as TwilioClient

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.slack_client = None
        self.twilio_client = None
        self.sendgrid_client = None
        
        # Initialize Slack client
        if settings.SLACK_BOT_TOKEN:
            self.slack_client = WebClient(token=settings.SLACK_BOT_TOKEN)
        
        # Initialize Twilio client for WhatsApp
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID, 
                settings.TWILIO_AUTH_TOKEN
            )
        
        # Initialize SendGrid client for email
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    def send_slack_alert(self, message: str, record: PPEComplianceRecord) -> bool:
        """Send alert to Slack channel"""
        if not self.slack_client or not settings.SLACK_CHANNEL_ID:
            logger.warning("Slack not configured")
            return False
        
        try:
            # Create rich message with blocks
            blocks = self._create_slack_blocks(message, record)
            
            response = self.slack_client.chat_postMessage(
                channel=settings.SLACK_CHANNEL_ID,
                text=message,
                blocks=blocks
            )
            
            logger.info(f"Slack alert sent successfully: {response['ts']}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
            return False

    def _create_slack_blocks(self, message: str, record: PPEComplianceRecord) -> list:
        """Create Slack blocks for rich message formatting"""
        # Determine color based on compliance
        color = "#ff0000" if not record.is_compliant else "#00ff00"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 PPE Compliance Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Worker:* {record.worker_name}\n*ID:* {record.worker_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Department:* {record.department or 'Unknown'}\n*Location:* {record.location or 'Unknown'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:* {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n*Shift:* {record.shift or 'Unknown'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Compliance Score:* {record.compliance_score:.1f}%\n*Status:* {'✅ Compliant' if record.is_compliant else '❌ Non-Compliant'}"
                    }
                ]
            }
        ]
        
        # Add PPE detection details
        ppe_details = []
        if record.helmet_detected:
            ppe_details.append(f"🪖 Helmet: ✅ ({record.helmet_confidence:.1%})")
        else:
            ppe_details.append("🪖 Helmet: ❌")
            
        if record.mask_detected:
            ppe_details.append(f"😷 Mask: ✅ ({record.mask_confidence:.1%})")
        else:
            ppe_details.append("😷 Mask: ❌")
            
        if record.gloves_detected:
            ppe_details.append(f"🧤 Gloves: ✅ ({record.gloves_confidence:.1%})")
        else:
            ppe_details.append("🧤 Gloves: ❌")
            
        if record.jacket_detected:
            ppe_details.append(f"🦺 Jacket: ✅ ({record.jacket_confidence:.1%})")
        else:
            ppe_details.append("🦺 Jacket: ❌")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*PPE Detection Results:*\n" + "\n".join(ppe_details)
            }
        })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        return blocks

    def send_email_alert(self, message: str, record: PPEComplianceRecord) -> bool:
        """Send alert via email using SendGrid"""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured")
            return False
        
        try:
            # Create email content
            subject = f"PPE Compliance Alert - {record.worker_name} ({record.worker_id})"
            
            html_content = self._create_email_html(message, record)
            text_content = self._create_email_text(message, record)
            
            mail = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=self._get_alert_recipients(record),
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email alert sent successfully: {response.status_code}")
                return True
            else:
                logger.error(f"Email send failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            return False

    def _create_email_html(self, message: str, record: PPEComplianceRecord) -> str:
        """Create HTML content for email alert"""
        status_color = "#28a745" if record.is_compliant else "#dc3545"
        status_text = "COMPLIANT" if record.is_compliant else "NON-COMPLIANT"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .details {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .ppe-item {{ margin: 5px 0; }}
                .compliant {{ color: #28a745; }}
                .non-compliant {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 PPE Compliance Alert</h1>
                    <h2>Status: {status_text}</h2>
                </div>
                <div class="content">
                    <div class="details">
                        <h3>Worker Information</h3>
                        <p><strong>Name:</strong> {record.worker_name}</p>
                        <p><strong>ID:</strong> {record.worker_id}</p>
                        <p><strong>Department:</strong> {record.department or 'Unknown'}</p>
                        <p><strong>Location:</strong> {record.location or 'Unknown'}</p>
                        <p><strong>Shift:</strong> {record.shift or 'Unknown'}</p>
                        <p><strong>Time:</strong> {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="details">
                        <h3>Compliance Score: {record.compliance_score:.1f}%</h3>
                    </div>
                    
                    <div class="details">
                        <h3>PPE Detection Results</h3>
                        <div class="ppe-item">
                            🪖 Helmet: {'<span class="compliant">✅ Detected</span>' if record.helmet_detected else '<span class="non-compliant">❌ Missing</span>'}
                            {f' (Confidence: {record.helmet_confidence:.1%})' if record.helmet_detected else ''}
                        </div>
                        <div class="ppe-item">
                            😷 Mask: {'<span class="compliant">✅ Detected</span>' if record.mask_detected else '<span class="non-compliant">❌ Missing</span>'}
                            {f' (Confidence: {record.mask_confidence:.1%})' if record.mask_detected else ''}
                        </div>
                        <div class="ppe-item">
                            🧤 Gloves: {'<span class="compliant">✅ Detected</span>' if record.gloves_detected else '<span class="non-compliant">❌ Missing</span>'}
                            {f' (Confidence: {record.gloves_confidence:.1%})' if record.gloves_detected else ''}
                        </div>
                        <div class="ppe-item">
                            🦺 Jacket: {'<span class="compliant">✅ Detected</span>' if record.jacket_detected else '<span class="non-compliant">❌ Missing</span>'}
                            {f' (Confidence: {record.jacket_confidence:.1%})' if record.jacket_detected else ''}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _create_email_text(self, message: str, record: PPEComplianceRecord) -> str:
        """Create plain text content for email alert"""
        text = f"""
PPE COMPLIANCE ALERT
===================

Worker: {record.worker_name} (ID: {record.worker_id})
Department: {record.department or 'Unknown'}
Location: {record.location or 'Unknown'}
Shift: {record.shift or 'Unknown'}
Time: {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Compliance Score: {record.compliance_score:.1f}%
Status: {'COMPLIANT' if record.is_compliant else 'NON-COMPLIANT'}

PPE Detection Results:
- Helmet: {'✅ Detected' if record.helmet_detected else '❌ Missing'} {f'({record.helmet_confidence:.1%})' if record.helmet_detected else ''}
- Mask: {'✅ Detected' if record.mask_detected else '❌ Missing'} {f'({record.mask_confidence:.1%})' if record.mask_detected else ''}
- Gloves: {'✅ Detected' if record.gloves_detected else '❌ Missing'} {f'({record.gloves_confidence:.1%})' if record.gloves_detected else ''}
- Jacket: {'✅ Detected' if record.jacket_detected else '❌ Missing'} {f'({record.jacket_confidence:.1%})' if record.jacket_detected else ''}

Please take appropriate action to ensure worker safety compliance.
        """
        return text

    def send_whatsapp_alert(self, message: str, record: PPEComplianceRecord) -> bool:
        """Send alert via WhatsApp using Twilio"""
        if not self.twilio_client:
            logger.warning("Twilio not configured")
            return False
        
        try:
            # Get recipient phone numbers
            recipients = self._get_whatsapp_recipients(record)
            
            if not recipients:
                logger.warning("No WhatsApp recipients configured")
                return False
            
            # Create WhatsApp message
            whatsapp_message = f"""
🚨 *PPE Compliance Alert*

*Worker:* {record.worker_name}
*ID:* {record.worker_id}
*Department:* {record.department or 'Unknown'}
*Location:* {record.location or 'Unknown'}
*Time:* {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

*Compliance Score:* {record.compliance_score:.1f}%
*Status:* {'✅ Compliant' if record.is_compliant else '❌ Non-Compliant'}

*PPE Detection:*
🪖 Helmet: {'✅' if record.helmet_detected else '❌'}
😷 Mask: {'✅' if record.mask_detected else '❌'}
🧤 Gloves: {'✅' if record.gloves_detected else '❌'}
🦺 Jacket: {'✅' if record.jacket_detected else '❌'}

Please take immediate action if non-compliant.
            """
            
            # Send to all recipients
            success_count = 0
            for recipient in recipients:
                try:
                    message_obj = self.twilio_client.messages.create(
                        body=whatsapp_message,
                        from_=settings.TWILIO_WHATSAPP_NUMBER,
                        to=f"whatsapp:{recipient}"
                    )
                    logger.info(f"WhatsApp alert sent to {recipient}: {message_obj.sid}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error sending WhatsApp to {recipient}: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp alert: {str(e)}")
            return False

    def _get_alert_recipients(self, record: PPEComplianceRecord) -> list:
        """Get email recipients for alerts"""
        # This should be configured based on your organization's structure
        # For now, return a default list - you should customize this
        default_recipients = [
            "safety@yourcompany.com",
            "supervisor@yourcompany.com"
        ]
        
        # Add department-specific recipients
        if record.department:
            dept_recipients = {
                "production": ["production-manager@yourcompany.com"],
                "maintenance": ["maintenance-manager@yourcompany.com"],
                "warehouse": ["warehouse-manager@yourcompany.com"]
            }
            default_recipients.extend(dept_recipients.get(record.department.lower(), []))
        
        return default_recipients

    def _get_whatsapp_recipients(self, record: PPEComplianceRecord) -> list:
        """Get WhatsApp recipients for alerts"""
        # This should be configured based on your organization's structure
        # For now, return a default list - you should customize this
        default_recipients = [
            "+1234567890",  # Safety manager
            "+1234567891"   # Supervisor
        ]
        
        # Add department-specific recipients
        if record.department:
            dept_recipients = {
                "production": ["+1234567892"],
                "maintenance": ["+1234567893"],
                "warehouse": ["+1234567894"]
            }
            default_recipients.extend(dept_recipients.get(record.department.lower(), []))
        
        return default_recipients

    def send_custom_alert(self, message: str, channels: list, record: PPEComplianceRecord) -> Dict[str, bool]:
        """Send custom alert to specified channels"""
        results = {}
        
        if "slack" in channels:
            results["slack"] = self.send_slack_alert(message, record)
        
        if "email" in channels:
            results["email"] = self.send_email_alert(message, record)
        
        if "whatsapp" in channels:
            results["whatsapp"] = self.send_whatsapp_alert(message, record)
        
        return results


