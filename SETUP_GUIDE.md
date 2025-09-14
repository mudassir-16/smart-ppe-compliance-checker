# Smart PPE Compliance Checker - Setup Guide

This guide will walk you through setting up the Smart PPE Compliance Checker system step by step.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Node.js and npm installed (for n8n)
- [ ] A text editor or IDE
- [ ] Internet connection for API access
- [ ] Admin access to create accounts and get API keys

## 🔑 Required API Keys and Accounts

You'll need accounts and API keys for the following services:

### 1. Roboflow (PPE Detection)
- **Purpose**: AI-powered PPE detection
- **Sign up**: [roboflow.com](https://roboflow.com)
- **What you'll get**: API key, Project ID, Model version
- **Cost**: Free tier available

### 2. Google Cloud (Sheets Integration)
- **Purpose**: Data logging and storage
- **Sign up**: [cloud.google.com](https://cloud.google.com)
- **What you'll get**: Service account JSON, Spreadsheet ID
- **Cost**: Free tier available

### 3. Airtable (Database)
- **Purpose**: Alternative data storage
- **Sign up**: [airtable.com](https://airtable.com)
- **What you'll get**: API key, Base ID
- **Cost**: Free tier available

### 4. Slack (Notifications)
- **Purpose**: Team notifications
- **Sign up**: [slack.com](https://slack.com)
- **What you'll get**: Bot token, Channel ID
- **Cost**: Free tier available

### 5. Twilio (WhatsApp)
- **Purpose**: WhatsApp notifications
- **Sign up**: [twilio.com](https://twilio.com)
- **What you'll get**: Account SID, Auth token
- **Cost**: Pay-per-use

### 6. SendGrid (Email)
- **Purpose**: Email notifications
- **Sign up**: [sendgrid.com](https://sendgrid.com)
- **What you'll get**: API key
- **Cost**: Free tier available

## 🚀 Step-by-Step Setup

### Step 1: Project Setup

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd smart-ppe-compliance-checker
   
   # Or download and extract the ZIP file
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv ppe-env
   
   # On Windows
   ppe-env\Scripts\activate
   
   # On macOS/Linux
   source ppe-env/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Roboflow Setup

1. **Create Roboflow account**
   - Go to [roboflow.com](https://roboflow.com)
   - Sign up for a free account
   - Verify your email

2. **Create a PPE detection project**
   - Click "Create New Project"
   - Name it "PPE Compliance Detection"
   - Choose "Object Detection" as project type
   - Upload sample images or use pre-trained models

3. **Get your API credentials**
   - Go to your project dashboard
   - Click on "API" tab
   - Copy your API key and Project ID
   - Note the model version (usually "1")

### Step 3: Google Sheets Setup

1. **Create Google Cloud Project**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project
   - Enable Google Sheets API

2. **Create Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name it "PPE Compliance Service"
   - Create and download the JSON key file

3. **Create Google Sheet**
   - Go to [sheets.google.com](https://sheets.google.com)
   - Create a new spreadsheet
   - Name it "PPE Compliance Log"
   - Share it with your service account email
   - Copy the spreadsheet ID from the URL

4. **Set up sheet headers**
   - Add these headers in row 1:
     ```
     Timestamp | Worker ID | Worker Name | Department | Location | Shift | 
     Helmet Detected | Helmet Confidence | Mask Detected | Mask Confidence | 
     Gloves Detected | Gloves Confidence | Jacket Detected | Jacket Confidence | 
     Is Compliant | Compliance Score | Alert Sent | Alert Channels | Notes
     ```

### Step 4: Airtable Setup

1. **Create Airtable account**
   - Go to [airtable.com](https://airtable.com)
   - Sign up for a free account

2. **Create base and tables**
   - Create a new base called "PPE Compliance"
   - Create these tables:
     - **PPE_Compliance**: Main compliance records
     - **Workers**: Worker information
     - **Daily_Reports**: Daily summary reports
     - **WhatsApp_Alerts**: WhatsApp alert logs

3. **Set up PPE_Compliance table fields**
   ```
   Worker ID (Single line text)
   Worker Name (Single line text)
   Timestamp (Date)
   Department (Single line text)
   Location (Single line text)
   Shift (Single line text)
   Helmet Detected (Checkbox)
   Helmet Confidence (Number)
   Mask Detected (Checkbox)
   Mask Confidence (Number)
   Gloves Detected (Checkbox)
   Gloves Confidence (Number)
   Jacket Detected (Checkbox)
   Jacket Confidence (Number)
   Is Compliant (Checkbox)
   Compliance Score (Number)
   Alert Sent (Checkbox)
   Alert Channels (Long text)
   Notes (Long text)
   ```

4. **Get API credentials**
   - Go to [airtable.com/account](https://airtable.com/account)
   - Copy your API key
   - Get your base ID from the URL when viewing your base

### Step 5: Slack Setup

1. **Create Slack workspace** (if you don't have one)
   - Go to [slack.com](https://slack.com)
   - Create a new workspace

2. **Create Slack app**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App"
   - Choose "From scratch"
   - Name it "PPE Compliance Bot"

3. **Configure bot permissions**
   - Go to "OAuth & Permissions"
   - Add these scopes:
     - `chat:write`
     - `channels:read`
     - `groups:read`
   - Install app to workspace

4. **Get credentials**
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)
   - Create a channel for alerts (e.g., #ppe-alerts)
   - Get the channel ID (right-click channel > Copy link)

### Step 6: Twilio Setup (WhatsApp)

1. **Create Twilio account**
   - Go to [twilio.com](https://twilio.com)
   - Sign up for a free account
   - Verify your phone number

2. **Set up WhatsApp sandbox**
   - Go to Console > Develop > Messaging > Try it out > Send a WhatsApp message
   - Follow instructions to set up sandbox
   - Note your sandbox number

3. **Get credentials**
   - Go to Console Dashboard
   - Copy your Account SID and Auth Token

### Step 7: SendGrid Setup

1. **Create SendGrid account**
   - Go to [sendgrid.com](https://sendgrid.com)
   - Sign up for a free account
   - Verify your email

2. **Create API key**
   - Go to Settings > API Keys
   - Create a new API key
   - Give it "Full Access" permissions
   - Copy the API key

3. **Verify sender email**
   - Go to Settings > Sender Authentication
   - Verify your sender email address

### Step 8: Configuration

1. **Create environment file**
   ```bash
   cp config.py .env
   ```

2. **Edit the .env file** with your credentials:
   ```env
   # Roboflow API Configuration
   ROBOFLOW_API_KEY=your_roboflow_api_key_here
   ROBOFLOW_PROJECT_ID=your_project_id_here
   ROBOFLOW_MODEL_VERSION=1

   # Database Configuration
   DATABASE_URL=sqlite:///./ppe_compliance.db

   # Google Sheets Configuration
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

   # Airtable Configuration
   AIRTABLE_API_KEY=your_airtable_api_key_here
   AIRTABLE_BASE_ID=your_base_id_here
   AIRTABLE_TABLE_NAME=PPE_Compliance

   # Slack Configuration
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_CHANNEL_ID=your_channel_id_here

   # WhatsApp Configuration (Twilio)
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

   # Email Configuration (SendGrid)
   SENDGRID_API_KEY=your_sendgrid_api_key
   FROM_EMAIL=safety@yourcompany.com

   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True
   ```

3. **Place Google credentials file**
   - Rename your downloaded Google service account JSON to `credentials.json`
   - Place it in the project root directory

### Step 9: Database Initialization

1. **Initialize the database**
   ```bash
   python -c "from models import create_tables; create_tables()"
   ```

2. **Verify database creation**
   - Check that `ppe_compliance.db` file was created
   - You can use a SQLite browser to inspect the tables

### Step 10: n8n Setup

1. **Install n8n globally**
   ```bash
   npm install -g n8n
   ```

2. **Start n8n**
   ```bash
   n8n start
   ```

3. **Access n8n interface**
   - Open [http://localhost:5678](http://localhost:5678)
   - Create an admin account

4. **Import workflows**
   - Go to "Workflows" > "Import from File"
   - Import each JSON file from `n8n_workflows/` folder
   - Update the API endpoints and credentials in each workflow

### Step 11: Testing the System

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```

2. **Test the API**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs)
   - Try the health check endpoint: `GET /health`

3. **Test the frontend**
   - Open `frontend/index.html` in your browser
   - Try uploading a test image

4. **Test alerts**
   - Create a test compliance record with non-compliance
   - Verify alerts are sent to Slack, email, and WhatsApp

### Step 12: Production Deployment

1. **Set up production environment**
   - Use a production database (PostgreSQL recommended)
   - Set up proper SSL certificates
   - Configure reverse proxy (nginx)

2. **Update configuration**
   - Set `DEBUG=False`
   - Use production API keys
   - Configure proper logging

3. **Set up monitoring**
   - Monitor API health
   - Set up log aggregation
   - Configure alerting for system failures

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors
```bash
# Make sure you're in the virtual environment
source ppe-env/bin/activate  # macOS/Linux
ppe-env\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

#### 2. Database connection errors
```bash
# Check if database file exists
ls -la ppe_compliance.db

# Recreate database
rm ppe_compliance.db
python -c "from models import create_tables; create_tables()"
```

#### 3. API key errors
- Double-check all API keys in the .env file
- Verify API keys are active and have proper permissions
- Check for extra spaces or quotes in the .env file

#### 4. Roboflow detection not working
- Verify your Roboflow project is properly trained
- Check if the model version is correct
- Test with a simple image first

#### 5. Alerts not sending
- Test each alert service individually
- Check webhook URLs in n8n workflows
- Verify API credentials for each service

### Getting Help

1. **Check the logs**
   - Look at the console output for error messages
   - Check the database for failed records

2. **Test individual components**
   - Test Roboflow API directly
   - Test each alert service separately
   - Verify database operations

3. **Community support**
   - Check the GitHub issues
   - Post questions in the repository discussions
   - Contact the development team

## 📊 Next Steps

After successful setup:

1. **Train your team** on using the system
2. **Set up regular backups** of the database
3. **Monitor system performance** and usage
4. **Plan for scaling** as your organization grows
5. **Consider advanced features** like edge deployment

## 🎯 Success Metrics

Track these metrics to measure system success:

- **Compliance Rate**: Percentage of compliant checks
- **Alert Response Time**: Time from detection to alert
- **System Uptime**: API and service availability
- **User Adoption**: Number of active users
- **False Positive Rate**: Incorrect non-compliance detections

---

**Congratulations!** You've successfully set up the Smart PPE Compliance Checker system. The system is now ready to help improve workplace safety through automated PPE compliance monitoring.


