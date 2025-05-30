from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict
from datetime import datetime
import json
import uuid

from . import models, schemas

def create_event(db: Session, event: schemas.EventCreate):
    """Create a new event in the database"""
    # Generate UUID for event_id
    event_id = str(uuid.uuid4())

    # Create database event
    db_event = models.Event(
        event_id=event_id,
        user_id=event.user_id,
        event_type=event.event_type,
        payload=json.dumps(event.payload),
        timestamp=datetime.utcnow()
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event

def get_event_count(
    db: Session,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """Get total count of events with optional filtering"""
    query = db.query(models.Event)

    # Apply filters
    if event_type:
        query = query.filter(models.Event.event_type == event_type)

    if start_date:
        query = query.filter(models.Event.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Event.timestamp <= end_date)

    return query.count()

def get_event_counts_by_type(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, int]:
    """Get count of events grouped by event_type"""
    query = db.query(
        models.Event.event_type,
        func.count(models.Event.event_id).label('count')
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.Event.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Event.timestamp <= end_date)

    # Group by event_type
    results = query.group_by(models.Event.event_type).all()

    # Convert to dictionary with default values
    counts = {"view": 0, "click": 0, "location": 0}

    for event_type, count in results:
        counts[event_type] = count

    return counts

def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Get events with pagination and optional filtering"""
    query = db.query(models.Event)

    if user_id:
        query = query.filter(models.Event.user_id == user_id)

    if event_type:
        query = query.filter(models.Event.event_type == event_type)

    return query.offset(skip).limit(limit).all()

def get_event_by_id(db: Session, event_id: str):
    """Get a specific event by ID"""
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()
