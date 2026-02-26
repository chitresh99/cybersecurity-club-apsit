"""Event management endpoints."""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.database import get_db
from app.models import Event, User, EventType
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.dependencies import get_current_user
from app.utils.errors import NotFoundError, ValidationError
from app.utils.validation import sanitize_string, sanitize_text

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=List[EventResponse], status_code=status.HTTP_200_OK)
def get_events(
    type: Optional[EventType] = Query(None, description="Filter by event type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get all events.
    
    - **type**: Optional filter by event type
    - **is_active**: Optional filter by active status
    
    Returns list of events matching the filters.
    """
    query = db.query(Event)
    
    if type is not None:
        query = query.filter(Event.type == type)
    
    if is_active is not None:
        query = query.filter(Event.is_active == is_active)
    
    events = query.order_by(Event.date.desc()).all()
    return events


@router.get("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single event by ID.
    
    - **event_id**: UUID of the event
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new event (Admin only).
    
    - **title**: Event title (required)
    - **type**: Event type enum (required)
    - **date**: Event date (required)
    - **description**: Event description (optional)
    
    Requires admin authentication.
    """
    # Sanitize inputs
    title = sanitize_string(event_data.title, max_length=200)
    description = sanitize_text(event_data.description) if event_data.description else None
    
    # Validate date is not in the past (optional business rule)
    if event_data.date < date.today():
        raise ValidationError("Event date cannot be in the past")
    
    # Create event
    event = Event(
        title=title,
        type=event_data.type,
        date=event_data.date,
        description=description,
        is_active=True
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.put("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing event (Admin only).
    
    - **event_id**: UUID of the event to update
    - All fields are optional in the request body
    
    Requires admin authentication.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    # Update fields if provided
    if event_data.title is not None:
        event.title = sanitize_string(event_data.title, max_length=200)
    
    if event_data.type is not None:
        event.type = event_data.type
    
    if event_data.date is not None:
        if event_data.date < date.today():
            raise ValidationError("Event date cannot be in the past")
        event.date = event_data.date
    
    if event_data.description is not None:
        event.description = sanitize_text(event_data.description)
    
    if event_data.is_active is not None:
        event.is_active = event_data.is_active
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an event (Admin only - soft delete).
    
    - **event_id**: UUID of the event to delete
    
    Sets is_active=false instead of hard deletion.
    Requires admin authentication.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    # Soft delete
    event.is_active = False
    db.commit()
    
    return None
