from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web Analytics Event Service",
    description="A robust backend service to collect, store, and provide aggregated analytics for user interaction events",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a new user activity event from the client.

    - **user_id**: String identifier for the user
    - **event_type**: Type of event (view, click, location)
    - **payload**: Event-specific data based on event_type
    """
    try:
        logger.info(f"Received event: {event.event_type} for user {event.user_id}")


        db_event = crud.create_event(db=db, event=event)

        logger.info(f"Event created with ID: {db_event.event_id}")
        return {"message": "Event received successfully", "event_id": db_event.event_id}

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics/event-counts")
async def get_event_counts(
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve the total count of events with optional filtering.

    - **event_type**: Filter by specific event type (view, click, location)
    - **start_date**: Filter events on or after this date (YYYY-MM-DD)
    - **end_date**: Filter events on or before this date (YYYY-MM-DD)
    """
    try:

        if event_type and event_type not in ["view", "click", "location"]:
            raise HTTPException(status_code=400, detail="Invalid event_type. Must be 'view', 'click', or 'location'")


        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")


        total_count = crud.get_event_count(
            db=db,
            event_type=event_type,
            start_date=start_datetime,
            end_date=end_datetime
        )

        logger.info(f"Event count query: type={event_type}, start={start_date}, end={end_date}, result={total_count}")

        return {"total_events": total_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event counts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics/event-counts-by-type")
async def get_event_counts_by_type(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve the count of events grouped by event_type with optional filtering.

    - **start_date**: Start date for aggregation (YYYY-MM-DD)
    - **end_date**: End date for aggregation (YYYY-MM-DD)
    """
    try:

        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")


        counts_by_type = crud.get_event_counts_by_type(
            db=db,
            start_date=start_datetime,
            end_date=end_datetime
        )

        logger.info(f"Event counts by type query: start={start_date}, end={end_date}, result={counts_by_type}")

        return counts_by_type

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event counts by type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Web Analytics Event Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
