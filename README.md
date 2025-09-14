# Smart PPE Compliance Checker

A comprehensive real-time PPE (Personal Protective Equipment) compliance detection and monitoring system using AI, automation, and no-code tools.

## 🎯 Features

### Core Features (MVP)
- **Real-Time PPE Detection**: Uses Roboflow YOLOv8 pre-trained models for helmet, mask, gloves, and safety jacket detection
- **Compliance Checking**: Automated compliance scoring and decision making
- **Multi-Channel Alerts**: Slack, WhatsApp, and Email notifications for non-compliance
- **Data Storage**: Integration with Google Sheets and Airtable for logging
- **Web Dashboard**: Real-time monitoring and analytics dashboard
- **n8n Automation**: Workflow automation for alerts and reporting

### Enhanced Features
- **Worker Management**: Complete worker database and tracking
- **Department Analytics**: Department-wise compliance statistics
- **Export Capabilities**: CSV, Excel, and JSON data export
- **API Integration**: RESTful API for third-party integrations
- **Webhook Support**: n8n webhook integration for custom workflows

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Roboflow      │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   YOLOv8 API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflows │    │   Database      │    │   External      │
│   (Automation)  │◄──►│   (SQLite)      │    │   Storage       │
└─────────────────┘    └─────────────────┘    │   (Sheets/      │
                                              │   Airtable)     │
                                              └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for n8n)
- Roboflow API key
- Google Cloud credentials (for Sheets)
- Airtable API key
- Slack Bot Token
- Twilio Account (for WhatsApp)
- SendGrid API key (for Email)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-ppe-compliance-checker
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config.py .env
   # Edit .env with your API keys and configuration
   ```

4. **Initialize the database**
   ```bash
   python -c "from models import create_tables; create_tables()"
   ```

5. **Start the FastAPI server**
   ```bash
   python main.py
   ```

6. **Access the frontend**
   Open `frontend/index.html` in your browser or serve it with a web server.

## 📋 Configuration

### Environment Variables

Create a `.env` file with the following variables:

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
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### API Keys Setup

#### 1. Roboflow Setup
1. Sign up at [Roboflow](https://roboflow.com)
2. Create a new project for PPE detection
3. Train or use a pre-trained YOLOv8 model
4. Get your API key and project ID from the dashboard

#### 2. Google Sheets Setup
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account and download credentials JSON
4. Share your spreadsheet with the service account email

#### 3. Airtable Setup
1. Create an Airtable base
2. Create tables for PPE_Compliance, Workers, Daily_Reports
3. Get your API key from account settings
4. Note your base ID from the URL

#### 4. Slack Setup
1. Create a Slack app at [api.slack.com](https://api.slack.com)
2. Add bot token scopes: `chat:write`, `channels:read`
3. Install the app to your workspace
4. Get the bot token and channel ID

#### 5. Twilio Setup (WhatsApp)
1. Sign up at [Twilio](https://twilio.com)
2. Set up WhatsApp sandbox
3. Get your Account SID and Auth Token
4. Configure WhatsApp number

#### 6. SendGrid Setup
1. Sign up at [SendGrid](https://sendgrid.com)
2. Create an API key
3. Verify your sender email

## 🔧 n8n Workflow Setup

### Installing n8n

```bash
npm install -g n8n
n8n start
```

### Importing Workflows

1. Open n8n at `http://localhost:5678`
2. Import the workflow JSON files from `n8n_workflows/`:
   - `basic_compliance_workflow.json`
   - `daily_report_workflow.json`
   - `whatsapp_alert_workflow.json`

### Configuring Workflows

1. Update webhook URLs to point to your FastAPI server
2. Configure API keys in each workflow node
3. Set up proper Slack webhooks and Twilio credentials
4. Test each workflow individually

## 📊 API Endpoints

### Compliance Checking
- `POST /api/compliance/check` - Check compliance from JSON data
- `POST /api/compliance/check-upload` - Check compliance from uploaded image

### Worker Management
- `GET /api/workers` - List all workers
- `POST /api/workers` - Create new worker
- `GET /api/workers/{worker_id}` - Get specific worker

### Compliance Records
- `GET /api/compliance/records` - List compliance records
- `GET /api/compliance/records/{record_id}` - Get specific record

### Dashboard & Analytics
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/analytics/compliance` - Get detailed analytics

### Data Export
- `GET /api/export/compliance` - Export compliance data

### Webhooks
- `POST /api/webhooks/compliance` - n8n webhook endpoint

## 🎨 Frontend Usage

### Upload Interface
1. Enter worker information (ID, name, department, shift, location)
2. Drag and drop or select an image file
3. Click "Check Compliance" to analyze the image
4. View real-time results with PPE detection details

### Dashboard
- View overall compliance statistics
- Monitor department performance
- Check recent violations
- Track compliance trends

### History
- Browse past compliance records
- Filter by worker, department, or compliance status
- Export data for further analysis

## 🔄 Workflow Automation

### Basic Compliance Workflow
1. Receives webhook with worker data and image
2. Calls PPE detection API
3. Sends alerts if non-compliant
4. Logs results to external storage

### Daily Report Workflow
1. Runs daily at 8 AM
2. Gathers compliance statistics
3. Generates comprehensive report
4. Sends to managers via Slack and Email

### WhatsApp Alert Workflow
1. Handles critical compliance alerts
2. Sends formatted WhatsApp messages
3. Includes safety recommendations
4. Logs all communications

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

#### Using Docker Compose
```yaml
version: '3.8'
services:
  ppe-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./ppe_compliance.db
    volumes:
      - ./data:/app/data
  
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
```

### Cloud Deployment

#### AWS Deployment
1. Use AWS Lambda for serverless API
2. Store data in RDS or DynamoDB
3. Use S3 for image storage
4. Set up CloudWatch for monitoring

#### Google Cloud Deployment
1. Deploy to Cloud Run
2. Use Cloud SQL for database
3. Use Cloud Storage for images
4. Set up Cloud Monitoring

## 🔍 Monitoring & Maintenance

### Health Checks
- `GET /health` - API health status
- Monitor database connections
- Check external API availability

### Logging
- Application logs in `logs/` directory
- Error tracking and debugging
- Performance monitoring

### Backup
- Regular database backups
- Export compliance data
- Backup configuration files

## 🛠️ Troubleshooting

### Common Issues

#### 1. Roboflow API Errors
- Check API key validity
- Verify project ID and model version
- Ensure image format is supported

#### 2. Database Connection Issues
- Check database file permissions
- Verify SQLite installation
- Check connection string format

#### 3. Alert Delivery Failures
- Verify API keys for each service
- Check webhook URLs
- Test individual alert channels

#### 4. n8n Workflow Issues
- Check webhook endpoints
- Verify API credentials in nodes
- Test workflow execution manually

### Debug Mode
Set `DEBUG=True` in environment variables for detailed error messages.

## 📈 Performance Optimization

### API Performance
- Use connection pooling for database
- Implement caching for frequent queries
- Optimize image processing

### Database Optimization
- Add indexes for frequently queried fields
- Implement data archiving
- Use database migrations

### Frontend Optimization
- Implement lazy loading
- Use CDN for static assets
- Optimize image compression

## 🔒 Security Considerations

### API Security
- Implement authentication and authorization
- Use HTTPS in production
- Validate all input data
- Rate limiting for API endpoints

### Data Privacy
- Encrypt sensitive data
- Implement data retention policies
- GDPR compliance considerations
- Secure API key storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Contact the development team

## 🔮 Future Enhancements

### Planned Features
- **Edge AI Deployment**: Raspberry Pi/Jetson Nano support
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Machine learning insights
- **IoT Integration**: Sensor data integration
- **AR/VR Training**: Virtual reality safety training
- **Blockchain**: Immutable compliance records
- **Voice Commands**: Voice-activated compliance checks

### Integration Opportunities
- **ERP Systems**: SAP, Oracle integration
- **HR Systems**: Workday, BambooHR integration
- **Safety Management**: EHS software integration
- **IoT Platforms**: AWS IoT, Azure IoT integration

---

**Note**: This system is designed for industrial safety compliance. Always ensure proper testing and validation before deploying in production environments.


