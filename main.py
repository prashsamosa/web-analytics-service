import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app, get_db
from app.database import Base

# Create a temporary database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Web Analytics Event Service API" in response.json()["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_view_event():
    """Test creating a view event"""
    event_data = {
        "user_id": "test_user_123",
        "event_type": "view",
        "payload": {
            "url": "https://example.com/test",
            "title": "Test Page"
        }
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 202
    assert "event_id" in response.json()

def test_create_click_event():
    """Test creating a click event"""
    event_data = {
        "user_id": "test_user_456",
        "event_type": "click",
        "payload": {
            "element_id": "test-button",
            "text": "Click Me",
            "xpath": "//button[@id='test-button']"
        }
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 202
    assert "event_id" in response.json()

def test_create_location_event():
    """Test creating a location event"""
    event_data = {
        "user_id": "test_user_789",
        "event_type": "location",
        "payload": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10.0
        }
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 202
    assert "event_id" in response.json()

def test_invalid_event_type():
    """Test invalid event type"""
    event_data = {
        "user_id": "test_user_123",
        "event_type": "invalid",
        "payload": {"test": "data"}
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 400

def test_invalid_view_payload():
    """Test invalid view payload (missing URL)"""
    event_data = {
        "user_id": "test_user_123",
        "event_type": "view",
        "payload": {
            "title": "Test Page"
            # Missing required 'url' field
        }
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 400

def test_invalid_location_payload():
    """Test invalid location payload (invalid coordinates)"""
    event_data = {
        "user_id": "test_user_123",
        "event_type": "location",
        "payload": {
            "latitude": 200,  # Invalid latitude (must be -90 to 90)
            "longitude": -74.0060
        }
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 400

def test_get_event_counts():
    """Test getting event counts"""
    # First create some events
    events = [
        {
            "user_id": "test_user_1",
            "event_type": "view",
            "payload": {"url": "https://example.com/1"}
        },
        {
            "user_id": "test_user_2",
            "event_type": "click",
            "payload": {"element_id": "btn-1"}
        }
    ]

    for event in events:
        client.post("/events", json=event)

    # Test getting total counts
    response = client.get("/analytics/event-counts")
    assert response.status_code == 200
    assert "total_events" in response.json()
    assert response.json()["total_events"] >= 2

def test_get_event_counts_with_filter():
    """Test getting event counts with event_type filter"""
    response = client.get("/analytics/event-counts?event_type=view")
    assert response.status_code == 200
    assert "total_events" in response.json()

def test_get_event_counts_invalid_type():
    """Test getting event counts with invalid event_type"""
    response = client.get("/analytics/event-counts?event_type=invalid")
    assert response.status_code == 400

def test_get_event_counts_by_type():
    """Test getting event counts grouped by type"""
    response = client.get("/analytics/event-counts-by-type")
    assert response.status_code == 200

    data = response.json()
    assert "view" in data
    assert "click" in data
    assert "location" in data

def test_invalid_date_format():
    """Test invalid date format in query parameters"""
    response = client.get("/analytics/event-counts?start_date=invalid-date")
    assert response.status_code == 400

# Cleanup after tests
def teardown_module():
    """Clean up test database"""
    if os.path.exists("test.db"):
        os.remove("test.db")
