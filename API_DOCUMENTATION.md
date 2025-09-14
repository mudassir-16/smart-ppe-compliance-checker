# Smart PPE Compliance Checker - API Documentation

This document provides comprehensive API documentation for the Smart PPE Compliance Checker system.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication for basic operations. For production deployment, implement proper authentication and authorization.

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## Compliance Checking

### POST /api/compliance/check

Check PPE compliance from JSON data.

**Request Body:**
```json
{
  "worker_id": "string (required)",
  "worker_name": "string (optional)",
  "location": "string (optional)",
  "department": "string (optional)",
  "shift": "string (optional)",
  "image_url": "string (optional)",
  "image_base64": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Compliance check completed successfully",
  "data": {
    "helmet_detected": true,
    "mask_detected": false,
    "gloves_detected": true,
    "jacket_detected": true,
    "helmet_confidence": 0.95,
    "mask_confidence": 0.0,
    "gloves_confidence": 0.87,
    "jacket_confidence": 0.92,
    "is_compliant": false,
    "compliance_score": 75.0
  },
  "record_id": 123,
  "alert_sent": true
}
```

### POST /api/compliance/check-upload

Check PPE compliance from uploaded image file.

**Request:** Multipart form data
- `worker_id` (string, required): Worker identifier
- `worker_name` (string, optional): Worker name
- `location` (string, optional): Work location
- `department` (string, optional): Department name
- `shift` (string, optional): Work shift
- `file` (file, required): Image file

**Response:** Same as `/api/compliance/check`

---

## Worker Management

### GET /api/workers

Get list of workers.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "worker_id": "W001",
    "name": "John Doe",
    "department": "Production",
    "position": "Operator",
    "email": "john.doe@company.com",
    "phone": "+1234567890",
    "shift": "morning",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  }
]
```

### POST /api/workers

Create a new worker.

**Request Body:**
```json
{
  "worker_id": "string (required)",
  "name": "string (required)",
  "department": "string (required)",
  "position": "string (optional)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "shift": "string (optional)"
}
```

**Response:**
```json
{
  "id": 1,
  "worker_id": "W001",
  "name": "John Doe",
  "department": "Production",
  "position": "Operator",
  "email": "john.doe@company.com",
  "phone": "+1234567890",
  "shift": "morning",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00.000Z",
  "updated_at": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/workers/{worker_id}

Get specific worker by ID.

**Path Parameters:**
- `worker_id` (string, required): Worker identifier

**Response:**
```json
{
  "id": 1,
  "worker_id": "W001",
  "name": "John Doe",
  "department": "Production",
  "position": "Operator",
  "email": "john.doe@company.com",
  "phone": "+1234567890",
  "shift": "morning",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00.000Z",
  "updated_at": "2024-01-01T12:00:00.000Z"
}
```

---

## Compliance Records

### GET /api/compliance/records

Get compliance records with optional filters.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)
- `worker_id` (string, optional): Filter by worker ID
- `department` (string, optional): Filter by department
- `is_compliant` (boolean, optional): Filter by compliance status

**Response:**
```json
[
  {
    "id": 1,
    "worker_id": "W001",
    "worker_name": "John Doe",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "image_path": "/uploads/image_001.jpg",
    "helmet_detected": true,
    "mask_detected": false,
    "gloves_detected": true,
    "jacket_detected": true,
    "helmet_confidence": 0.95,
    "mask_confidence": 0.0,
    "gloves_confidence": 0.87,
    "jacket_confidence": 0.92,
    "is_compliant": false,
    "compliance_score": 75.0,
    "location": "Building A, Floor 2",
    "department": "Production",
    "shift": "morning",
    "alert_sent": true
  }
]
```

### GET /api/compliance/records/{record_id}

Get specific compliance record by ID.

**Path Parameters:**
- `record_id` (integer, required): Record identifier

**Response:**
```json
{
  "id": 1,
  "worker_id": "W001",
  "worker_name": "John Doe",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "image_path": "/uploads/image_001.jpg",
  "helmet_detected": true,
  "mask_detected": false,
  "gloves_detected": true,
  "jacket_detected": true,
  "helmet_confidence": 0.95,
  "mask_confidence": 0.0,
  "gloves_confidence": 0.87,
  "jacket_confidence": 0.92,
  "is_compliant": false,
  "compliance_score": 75.0,
  "location": "Building A, Floor 2",
  "department": "Production",
  "shift": "morning",
  "alert_sent": true
}
```

---

## Dashboard and Analytics

### GET /api/dashboard/stats

Get dashboard statistics.

**Query Parameters:**
- `days` (integer, optional): Number of days to include (default: 7)
- `department` (string, optional): Filter by department

**Response:**
```json
{
  "total_checks": 150,
  "compliant_checks": 120,
  "non_compliant_checks": 30,
  "compliance_rate": 80.0,
  "today_checks": 25,
  "today_compliant": 20,
  "today_non_compliant": 5,
  "today_compliance_rate": 80.0,
  "department_stats": {
    "Production": {
      "total": 100,
      "compliant": 80,
      "rate": 80.0
    },
    "Maintenance": {
      "total": 50,
      "compliant": 40,
      "rate": 80.0
    }
  },
  "recent_violations": [
    {
      "id": 1,
      "worker_id": "W001",
      "worker_name": "John Doe",
      "timestamp": "2024-01-01T12:00:00.000Z",
      "compliance_score": 75.0,
      "department": "Production"
    }
  ]
}
```

### GET /api/analytics/compliance

Get detailed compliance analytics.

**Query Parameters:**
- `days` (integer, optional): Number of days to include (default: 30)
- `department` (string, optional): Filter by department

**Response:**
```json
{
  "summary": {
    "total_records": 500,
    "compliant_records": 400,
    "non_compliant_records": 100,
    "compliance_rate": 80.0
  },
  "ppe_statistics": {
    "helmet": {
      "detected": 450,
      "rate": 90.0
    },
    "mask": {
      "detected": 380,
      "rate": 76.0
    },
    "gloves": {
      "detected": 420,
      "rate": 84.0
    },
    "jacket": {
      "detected": 410,
      "rate": 82.0
    }
  },
  "department_statistics": {
    "Production": {
      "total": 300,
      "compliant": 240,
      "rate": 80.0
    },
    "Maintenance": {
      "total": 200,
      "compliant": 160,
      "rate": 80.0
    }
  },
  "hourly_statistics": {
    "8": {
      "total": 50,
      "compliant": 40,
      "rate": 80.0
    },
    "9": {
      "total": 45,
      "compliant": 36,
      "rate": 80.0
    }
  },
  "generated_at": "2024-01-01T12:00:00.000Z"
}
```

---

## Alert Management

### POST /api/alerts/send

Send manual alert.

**Request Body:**
```json
{
  "record_id": 123,
  "worker_id": "W001",
  "alert_type": "non_compliance",
  "message": "Custom alert message",
  "channels": ["slack", "email", "whatsapp"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "slack": true,
    "email": true,
    "whatsapp": false
  }
}
```

---

## Data Export

### GET /api/export/compliance

Export compliance data.

**Query Parameters:**
- `format` (string, optional): Export format - "csv", "excel", or "json" (default: "csv")
- `days` (integer, optional): Number of days to include (default: 30)
- `department` (string, optional): Filter by department

**Response:** File download

---

## Data Sync

### POST /api/sync/workers

Sync workers to external storage systems.

**Response:**
```json
{
  "success": true,
  "results": {
    "google_sheets": true,
    "airtable": true
  }
}
```

---

## Webhooks

### POST /api/webhooks/compliance

Webhook endpoint for n8n integration.

**Request Body:**
```json
{
  "event_type": "compliance_check",
  "data": {
    "worker_id": "W001",
    "worker_name": "John Doe",
    "location": "Building A",
    "department": "Production",
    "shift": "morning",
    "image_url": "https://example.com/image.jpg"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "data": {
    "helmet_detected": true,
    "mask_detected": false,
    "gloves_detected": true,
    "jacket_detected": true,
    "is_compliant": false,
    "compliance_score": 75.0
  },
  "record_id": 123,
  "alert_sent": true
}
```

---

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Common Error Responses

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "worker_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Not Found Error (404)
```json
{
  "detail": "Worker not found"
}
```

#### Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, implement rate limiting to prevent abuse.

## CORS

CORS is enabled for all origins in development. For production, configure specific allowed origins.

## Examples

### Python Example

```python
import requests
import json

# Check compliance
url = "http://localhost:8000/api/compliance/check"
data = {
    "worker_id": "W001",
    "worker_name": "John Doe",
    "department": "Production",
    "image_url": "https://example.com/worker.jpg"
}

response = requests.post(url, json=data)
result = response.json()

if result["success"]:
    print(f"Compliance: {result['data']['is_compliant']}")
    print(f"Score: {result['data']['compliance_score']}%")
else:
    print(f"Error: {result['message']}")
```

### JavaScript Example

```javascript
// Check compliance
async function checkCompliance(workerData) {
    const response = await fetch('http://localhost:8000/api/compliance/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(workerData)
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('Compliance:', result.data.is_compliant);
        console.log('Score:', result.data.compliance_score + '%');
    } else {
        console.error('Error:', result.message);
    }
}

// Usage
checkCompliance({
    worker_id: 'W001',
    worker_name: 'John Doe',
    department: 'Production',
    image_url: 'https://example.com/worker.jpg'
});
```

### cURL Example

```bash
# Check compliance
curl -X POST "http://localhost:8000/api/compliance/check" \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "W001",
    "worker_name": "John Doe",
    "department": "Production",
    "image_url": "https://example.com/worker.jpg"
  }'

# Get dashboard stats
curl -X GET "http://localhost:8000/api/dashboard/stats?days=7"

# Get workers
curl -X GET "http://localhost:8000/api/workers?limit=10"
```

---

## SDKs and Libraries

### Python SDK

```python
from ppe_compliance_client import PPEComplianceClient

client = PPEComplianceClient(base_url="http://localhost:8000")

# Check compliance
result = client.check_compliance(
    worker_id="W001",
    worker_name="John Doe",
    department="Production",
    image_url="https://example.com/worker.jpg"
)

print(f"Compliance: {result.is_compliant}")
print(f"Score: {result.compliance_score}%")
```

### JavaScript SDK

```javascript
import { PPEComplianceClient } from 'ppe-compliance-client';

const client = new PPEComplianceClient('http://localhost:8000');

// Check compliance
const result = await client.checkCompliance({
    worker_id: 'W001',
    worker_name: 'John Doe',
    department: 'Production',
    image_url: 'https://example.com/worker.jpg'
});

console.log('Compliance:', result.is_compliant);
console.log('Score:', result.compliance_score + '%');
```

---

## Changelog

### Version 1.0.0
- Initial API release
- Basic compliance checking
- Worker management
- Dashboard and analytics
- Alert system
- Data export
- Webhook support

---

## Support

For API support and questions:
- Check the troubleshooting section in the main README
- Review the error messages and status codes
- Test with the provided examples
- Contact the development team for assistance


