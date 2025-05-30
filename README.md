## 📋 Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/prashsamosa/web-analytics-service.git
cd web-analytics-service
```

### 2. Initialize Project Environment

```bash

# Create virtual environment
uv venv

# Activate virtual environment
.venv/bin/activate

# Install Packages

uv sync


```

### 3. Generate Sample Data

```bash
python scripts/generate_events.py
```

### 4. Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://127.0.0.1:8000

**API Documentation**: http://127.0.0.1:8000/docs

### 5. Start the Frontend UI (Optional)

```bash
cd ui
python -m http.server 8001
```

The UI will be available at: http://localhost:8001/index.html

## 📡 API Endpoints

### POST /events

**Purpose**: Ingest a new user activity event from the client.

**Request Body**:
```json
{
  "user_id": "user_123",
  "event_type": "view",
  "payload": {
    "url": "https://example.com/page1",
    "title": "Page Title"
  }
}
```

**Success Response (202 Accepted)**:
```json
{
  "message": "Event received successfully",
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body or validation errors
- `500 Internal Server Error`: Server-side processing errors

### GET /analytics/event-counts

**Purpose**: Retrieve total count of events with optional filtering.

**Query Parameters**:
- `event_type` (optional): Filter by event type ("view", "click", "location")
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Success Response (200 OK)**:
```json
{
  "total_events": 12345
}
```

**Example Requests**:
```bash
# Get all events
curl "http://localhost:8000/analytics/event-counts"

# Filter by event type
curl "http://localhost:8000/analytics/event-counts?event_type=view"

# Filter by date range
curl "http://localhost:8000/analytics/event-counts?start_date=2025-05-01&end_date=2025-05-15"
```

### GET /analytics/event-counts-by-type

**Purpose**: Retrieve count of events grouped by event_type.

**Query Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Success Response (200 OK)**:
```json
{
  "view": 8000,
  "click": 3000,
  "location": 1345
}
```

## 📊 Event Types and Payload Formats

### View Events
Track page views and navigation events.

```json
{
  "user_id": "user_123",
  "event_type": "view",
  "payload": {
    "url": "https://example.com/page",
    "title": "Page Title (optional)"
  }
}
```

### Click Events
Track user interactions with page elements.

```json
{
  "user_id": "user_123",
  "event_type": "click",
  "payload": {
    "element_id": "button-id (optional)",
    "text": "Button Text (optional)",
    "xpath": "//button[@id='btn'] (optional)"
  }
}
```

### Location Events
Track user geographic location data.

```json
{
  "user_id": "user_123",
  "event_type": "location",
  "payload": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 10.5
  }
}
```

## 📈 Sample Data

The `generate_events.py` script creates 3,000 realistic sample events for testing and development:


## 🏗️ Project Structure

```
web-analytics-service/
├── app/
│   ├── main.py              # FastAPI application entry point
│   └── ...                  # Additional app modules
├── scripts/
│   └── generate_events.py   # Sample data generation script
├── ui/
│   ├── index.html          # Web interface
│   └── ...                 # Additional UI files
├── .venv/                  # Virtual environment
└── README.md
```

## 🚦 Usage Examples

### Sending Events via cURL

```bash
# Track a page view
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_456",
    "event_type": "view",
    "payload": {
      "url": "https://mysite.com/products",
      "title": "Products Page"
    }
  }'

# Track a button click
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_456",
    "event_type": "click",
    "payload": {
      "element_id": "buy-now-btn",
      "text": "Buy Now"
    }
  }'
```

### Querying Analytics

```bash
# Get total event count
curl "http://localhost:8000/analytics/event-counts"

# Get events by type for a specific date range
curl "http://localhost:8000/analytics/event-counts-by-type?start_date=2025-05-01&end_date=2025-05-15"
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://127.0.0.1:8000/docs


