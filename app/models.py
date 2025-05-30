from sqlalchemy import Column, String, DateTime, Text, Index, CheckConstraint
from sqlalchemy.sql import func
from .database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    payload = Column(Text, nullable=False)  


    __table_args__ = (
        CheckConstraint(
            event_type.in_(['view', 'click', 'location']),
            name='check_event_type'
        ),
        Index('idx_events_composite', 'event_type', 'timestamp'),
        Index('idx_events_user_time', 'user_id', 'timestamp'),
    )
