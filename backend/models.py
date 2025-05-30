from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, Any

class ViewPayload(BaseModel):
    url: str
    title: Optional[str] = None

class ClickPayload(BaseModel):
    element_id: Optional[str] = None
    text: Optional[str] = None
    xpath: Optional[str] = None

class LocationPayload(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, gt=0)

class EventRequest(BaseModel):
    user_id: str
    event_type: str
    payload: Dict[str, Any]

    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = {'view', 'click', 'location'}
        if v not in allowed_types:
            raise ValueError(f'event_type must be one of {allowed_types}')
        return v

    @validator('payload')
    def validate_payload(cls, v, values):
        event_type = values.get('event_type')

        if event_type == 'view':
            ViewPayload(**v)
        elif event_type == 'click':
            ClickPayload(**v)
        elif event_type == 'location':
            LocationPayload(**v)

        return v

class EventCountResponse(BaseModel):
    total_events: int

class EventCountByTypeResponse(BaseModel):
    view: Optional[int] = 0
    click: Optional[int] = 0
    location: Optional[int] = 0

    @classmethod
    def from_counts(cls, counts_dict: Dict[str, int]):
        return cls(
            view=counts_dict.get('view', 0),
            click=counts_dict.get('click', 0),
            location=counts_dict.get('location', 0)
        )

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
