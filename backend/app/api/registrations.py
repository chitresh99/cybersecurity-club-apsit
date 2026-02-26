"""Event registration endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.database import get_db
from app.models import Registration, User
from app.schemas import RegistrationCreate, RegistrationResponse
from app.dependencies import get_current_user
from app.utils.errors import NotFoundError, ConflictError
from app.utils.validation import sanitize_string
from app.services.export_service import export_registrations_to_csv

router = APIRouter(prefix="/api/registrations", tags=["Registrations"])


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_registration(
    registration_data: RegistrationCreate,
    db: Session = Depends(get_db)
):
    """Register for an event (Public).
    
    - **event_id**: UUID of the event
    - **operative_name**: Name of the registrant
    - **moodle_id**: Moodle ID (8-12 alphanumeric characters)
    
    Prevents duplicate registrations for the same event by the same Moodle ID.
    """
    # Sanitize inputs
    operative_name = sanitize_string(registration_data.operative_name, max_length=100)
    moodle_id = registration_data.moodle_id  # Already validated in schema
    
    # Check if event exists and is active
    from app.models import Event
    event = db.query(Event).filter(
        Event.id == registration_data.event_id,
        Event.is_active == True
    ).first()
    
    if not event:
        raise NotFoundError("Event", str(registration_data.event_id))
    
    # Create registration
    registration = Registration(
        event_id=registration_data.event_id,
        operative_name=operative_name,
        moodle_id=moodle_id
    )
    
    try:
        db.add(registration)
        db.commit()
        db.refresh(registration)
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"Registration already exists for Moodle ID {moodle_id} and event {event.title}"
        )
    
    # Load event relationship
    db.refresh(registration)
    
    return registration


@router.get("", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
def get_registrations(
    event_id: Optional[UUID] = Query(None, description="Filter by event ID"),
    moodle_id: Optional[str] = Query(None, description="Filter by Moodle ID"),
    export: Optional[str] = Query(None, description="Export format (csv)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all registrations (Admin only).
    
    - **event_id**: Optional filter by event ID
    - **moodle_id**: Optional filter by Moodle ID
    - **export**: Set to 'csv' to export as CSV file
    
    Requires admin authentication.
    """
    query = db.query(Registration)
    
    if event_id:
        query = query.filter(Registration.event_id == event_id)
    
    if moodle_id:
        query = query.filter(Registration.moodle_id == moodle_id)
    
    registrations = query.order_by(Registration.timestamp.desc()).all()
    
    # Handle CSV export
    if export and export.lower() == "csv":
        csv_content = export_registrations_to_csv(db, event_id, registrations)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=registrations.csv"}
        )
    
    return registrations


@router.get("/{registration_id}", response_model=RegistrationResponse, status_code=status.HTTP_200_OK)
def get_registration(
    registration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single registration by ID (Admin only).
    
    - **registration_id**: UUID of the registration
    
    Requires admin authentication.
    """
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    
    if not registration:
        raise NotFoundError("Registration", str(registration_id))
    
    return registration


@router.get("/export/csv", status_code=status.HTTP_200_OK)
def export_registrations_csv(
    event_id: Optional[UUID] = Query(None, description="Filter by event ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export registrations as CSV file (Admin only).
    
    - **event_id**: Optional filter by event ID
    
    Returns CSV file download.
    Requires admin authentication.
    """
    csv_content = export_registrations_to_csv(db, event_id)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"}
    )
