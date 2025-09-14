import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Roboflow API Configuration
    ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
    ROBOFLOW_PROJECT_ID = os.getenv("ROBOFLOW_PROJECT_ID", "")
    ROBOFLOW_MODEL_VERSION = os.getenv("ROBOFLOW_MODEL_VERSION", "1")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ppe_compliance.db")
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    
    # Airtable Configuration
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
    AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "PPE_Compliance")
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")
    
    # WhatsApp Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "safety@yourcompany.com")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()


