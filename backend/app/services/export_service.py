"""CSV export service for registrations."""
import csv
import io
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Registration, Event
from uuid import UUID


def export_registrations_to_csv(
    db: Session,
    event_id: Optional[UUID] = None,
    registrations: Optional[List[Registration]] = None
) -> str:
    """Export registrations to CSV format.
    
    Args:
        db: Database session
        event_id: Optional event ID to filter by
        registrations: Optional pre-fetched registrations list
    
    Returns:
        CSV content as string
    """
    # Get registrations if not provided
    if registrations is None:
        query = db.query(Registration)
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        registrations = query.order_by(Registration.timestamp.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Registration ID",
        "Event Title",
        "Event Type",
        "Event Date",
        "Operative Name",
        "Moodle ID",
        "Registration Timestamp"
    ])
    
    # Write data rows
    for reg in registrations:
        event = reg.event if reg.event else db.query(Event).filter(Event.id == reg.event_id).first()
        writer.writerow([
            str(reg.id),
            event.title if event else "N/A",
            event.type.value if event else "N/A",
            event.date.isoformat() if event else "N/A",
            reg.operative_name,
            reg.moodle_id,
            reg.timestamp.isoformat()
        ])
    
    return output.getvalue()
