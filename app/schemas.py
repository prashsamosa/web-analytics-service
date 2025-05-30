from pydantic import BaseModel, validator, Field
from typing import Union, Optional, Dict, Any
from datetime import datetime

class ViewPayload(BaseModel):
    url: str = Field(..., min_length=1, description="The URL of the page viewed")
    title: Optional[str] = Field(None, description="The title of the page")

class ClickPayload(BaseModel):
    element_id: Optional[str] = Field(None, description="The ID of the clicked HTML element")
    text: Optional[str] = Field(None, description="The text content of the clicked element")
    xpath: Optional[str] = Field(None, description="XPath or CSS selector to locate the element")

class LocationPayload(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="User's latitude")
    longitude: float = Field(..., ge=-180, le=180, description="User's longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy of the location in meters")


class EventCreate(BaseModel):
    user_id: str = Field(..., min_length=1, description="String identifier for the user")
    event_type: str = Field(..., description="Type of event: view, click, or location")
    payload: Dict[str, Any] = Field(..., description="Event-specific data")

    @validator('event_type')
    def validate_event_type(cls, v):
        if v not in ['view', 'click', 'location']:
            raise ValueError('event_type must be one of: view, click, location')
        return v

    @validator('payload')
    def validate_payload(cls, v, values):
        if 'event_type' not in values:
            return v

        event_type = values['event_type']

        try:
            if event_type == 'view':
                ViewPayload(**v)
            elif event_type == 'click':
                ClickPayload(**v)
            elif event_type == 'location':
                LocationPayload(**v)
        except Exception as e:
            raise ValueError(f'Invalid payload for event_type "{event_type}": {str(e)}')

        return v


class EventResponse(BaseModel):
    event_id: str
    user_id: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]

    class Config:
        from_attributes = True


class EventCountResponse(BaseModel):
    total_events: int

class EventCountsByTypeResponse(BaseModel):
    view: Optional[int] = 0
    click: Optional[int] = 0
    location: Optional[int] = 0
