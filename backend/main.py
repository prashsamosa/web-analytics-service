from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date
import json
import logging
from typing import Optional

from database import get_db, create_tables, Event
from models import EventRequest, EventCountResponse, EventCountByTypeResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web Analytics Event Service",
    description="A robust backend service to collect, store, and provide aggregated analytics for user interaction events",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

@app.post("/events", status_code=202)
async def create_event(event: EventRequest, db: Session = Depends(get_db)):
    """
    Ingest a new user activity event from the client.
    """
    try:
        # Create new event record
        db_event = Event(
            user_id=event.user_id,
            event_type=event.event_type,
            payload=json.dumps(event.payload)
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        logger.info(f"Event created: {db_event.event_id} - Type: {event.event_type} - User: {event.user_id}")

        return {"message": "Event received successfully", "event_id": db_event.event_id}

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing event")

@app.get("/analytics/event-counts", response_model=EventCountResponse)
async def get_event_counts(
    db: Session = Depends(get_db),
    event_type: Optional[str] = Query(None, description="Filter by event type (view, click, location)"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)")
):
    """
    Retrieve the total count of events with optional filtering.
    """
    try:
        # Validate event_type if provided
        if event_type and event_type not in {'view', 'click', 'location'}:
            raise HTTPException(status_code=400, detail="Invalid event_type. Must be one of: view, click, location")

        # Build query
        query = db.query(func.count(Event.event_id))

        # Apply filters
        conditions = []
        if event_type:
            conditions.append(Event.event_type == event_type)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            conditions.append(Event.timestamp >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            conditions.append(Event.timestamp <= end_datetime)

        if conditions:
            query = query.filter(and_(*conditions))

        total_count = query.scalar()

        logger.info(f"Event count query executed - Total: {total_count}, Filters: event_type={event_type}, start_date={start_date}, end_date={end_date}")

        return EventCountResponse(total_events=total_count)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event counts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while retrieving event counts")

@app.get("/analytics/event-counts-by-type", response_model=EventCountByTypeResponse)
async def get_event_counts_by_type(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)")
):
    """
    Retrieve the count of events grouped by event_type with optional filtering.
    """
    try:
        # Build query
        query = db.query(Event.event_type, func.count(Event.event_id))

        # Apply date filters
        conditions = []
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            conditions.append(Event.timestamp >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            conditions.append(Event.timestamp <= end_datetime)

        if conditions:
            query = query.filter(and_(*conditions))

        # Group by event_type
        results = query.group_by(Event.event_type).all()

        # Convert to dictionary
        counts_dict = {event_type: count for event_type, count in results}

        logger.info(f"Event counts by type query executed - Results: {counts_dict}, Filters: start_date={start_date}, end_date={end_date}")

        return EventCountByTypeResponse.from_counts(counts_dict)

    except Exception as e:
        logger.error(f"Error getting event counts by type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while retrieving event counts by type")

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {"message": "Web Analytics Event Service is running", "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
