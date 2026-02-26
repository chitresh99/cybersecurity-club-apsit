"""PDF resource management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from pathlib import Path
import os
from app.database import get_db
from app.models import Resource, User, ResourceLevel
from app.schemas import ResourceCreate, ResourceUpdate, ResourceResponse
from app.dependencies import get_current_user
from app.utils.errors import NotFoundError
from app.utils.validation import sanitize_string
from app.services.file_service import (
    save_pdf_file,
    delete_file,
    file_exists,
    validate_pdf_file
)
from app.config import settings

router = APIRouter(prefix="/api/resources", tags=["Resources"])


@router.get("", response_model=List[ResourceResponse], status_code=status.HTTP_200_OK)
def get_resources(
    level: Optional[ResourceLevel] = Query(None, description="Filter by resource level"),
    db: Session = Depends(get_db)
):
    """Get all resources.
    
    - **level**: Optional filter by resource level (beginner, intermediate, advanced)
    
    Returns list of resources matching the filters.
    """
    query = db.query(Resource)
    
    if level is not None:
        query = query.filter(Resource.level == level)
    
    resources = query.order_by(Resource.created_at.desc()).all()
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse, status_code=status.HTTP_200_OK)
def get_resource(
    resource_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single resource by ID.
    
    - **resource_id**: UUID of the resource
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise NotFoundError("Resource", str(resource_id))
    
    return resource


@router.get("/{resource_id}/download", status_code=status.HTTP_200_OK)
def download_resource(
    resource_id: UUID,
    db: Session = Depends(get_db)
):
    """Download a PDF resource file.
    
    - **resource_id**: UUID of the resource
    
    Returns the PDF file for download.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise NotFoundError("Resource", str(resource_id))
    
    # Get full file path
    file_path = Path(resource.file_url)
    
    if not file_exists(str(file_path)):
        raise NotFoundError("Resource file", str(resource_id))
    
    # Return file for download
    return FileResponse(
        path=str(file_path),
        filename=f"{resource.title.replace(' ', '_')}.pdf",
        media_type="application/pdf"
    )


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    title: str = Form(..., description="Resource title"),
    level: ResourceLevel = Form(..., description="Resource level"),
    file: UploadFile = File(..., description="PDF file to upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new PDF resource (Admin only).
    
    - **title**: Resource title
    - **level**: Resource level (beginner, intermediate, advanced)
    - **file**: PDF file to upload (max 10MB)
    
    Requires admin authentication.
    """
    # Validate file
    is_valid, error_msg = validate_pdf_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Sanitize title
    sanitized_title = sanitize_string(title, max_length=200)
    
    # Save file
    file_url, file_size = save_pdf_file(file)
    
    # Create resource record
    resource = Resource(
        title=sanitized_title,
        level=level,
        file_url=file_url,
        file_size=file_size
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse, status_code=status.HTTP_200_OK)
def update_resource(
    resource_id: UUID,
    title: Optional[str] = Form(None, description="Resource title"),
    level: Optional[ResourceLevel] = Form(None, description="Resource level"),
    file: Optional[UploadFile] = File(None, description="New PDF file to replace existing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a resource (Admin only).
    
    - **resource_id**: UUID of the resource to update
    - **title**: Optional new title
    - **level**: Optional new level
    - **file**: Optional new PDF file to replace existing
    
    Requires admin authentication.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise NotFoundError("Resource", str(resource_id))
    
    # Update title if provided
    if title is not None:
        resource.title = sanitize_string(title, max_length=200)
    
    # Update level if provided
    if level is not None:
        resource.level = level
    
    # Replace file if provided
    if file is not None:
        # Validate new file
        is_valid, error_msg = validate_pdf_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Delete old file
        old_file_path = Path(resource.file_url)
        if old_file_path.exists():
            delete_file(str(old_file_path))
        
        # Save new file
        file_url, file_size = save_pdf_file(file)
        resource.file_url = file_url
        resource.file_size = file_size
    
    db.commit()
    db.refresh(resource)
    
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resource (Admin only).
    
    - **resource_id**: UUID of the resource to delete
    
    Deletes both the database record and the file.
    Requires admin authentication.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise NotFoundError("Resource", str(resource_id))
    
    # Delete file
    file_path = Path(resource.file_url)
    if file_path.exists():
        delete_file(str(file_path))
    
    # Delete database record
    db.delete(resource)
    db.commit()
    
    return None
