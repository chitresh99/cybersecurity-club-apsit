"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from app.models import EventType, ResourceLevel


# Authentication Schemas
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    username: str
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Event Schemas
class EventBase(BaseModel):
    """Base event schema."""
    title: str = Field(..., min_length=1, max_length=200)
    type: EventType
    date: date
    description: Optional[str] = None


class EventCreate(EventBase):
    """Event creation schema."""
    pass


class EventUpdate(BaseModel):
    """Event update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[EventType] = None
    date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    """Event response schema."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Registration Schemas
class RegistrationCreate(BaseModel):
    """Registration creation schema."""
    event_id: UUID
    operative_name: str = Field(..., min_length=1, max_length=100)
    moodle_id: str = Field(..., min_length=1, max_length=20)
    
    @validator('moodle_id')
    def validate_moodle_id(cls, v):
        """Validate Moodle ID format (alphanumeric, 8-12 chars)."""
        import re
        if not re.match(r'^[a-zA-Z0-9]{8,12}$', v):
            raise ValueError('Moodle ID must be 8-12 alphanumeric characters')
        return v


class RegistrationResponse(BaseModel):
    """Registration response schema."""
    id: UUID
    event_id: UUID
    operative_name: str
    moodle_id: str
    timestamp: datetime
    event: Optional[EventResponse] = None
    
    class Config:
        from_attributes = True


# Resource Schemas
class ResourceBase(BaseModel):
    """Base resource schema."""
    title: str = Field(..., min_length=1, max_length=200)
    level: ResourceLevel


class ResourceCreate(ResourceBase):
    """Resource creation schema."""
    pass


class ResourceUpdate(BaseModel):
    """Resource update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    level: Optional[ResourceLevel] = None


class ResourceResponse(ResourceBase):
    """Resource response schema."""
    id: UUID
    file_url: str
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Error Schemas
class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: ErrorDetail


# Hackathon Team Registration Schemas
class TeamMemberBase(BaseModel):
    """Base schema for team member."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    moodle_id: str = Field(..., min_length=1, max_length=20)
    roll_no: str = Field(..., min_length=1, max_length=20)
    division: str = Field(..., min_length=1, max_length=5)
    department: str = Field(..., min_length=1, max_length=100)
    year: str = Field(..., min_length=1, max_length=10)
    mobile: str = Field(..., pattern=r'^[0-9]{10}$')
    is_leader: bool = False
    
    @validator('mobile')
    def validate_mobile(cls, v):
        """Validate mobile number is exactly 10 digits."""
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        return v


class HackathonTeamCreate(BaseModel):
    """Schema for creating a hackathon team."""
    event_name: str = Field(..., min_length=1, max_length=200)
    team_name: str = Field(..., min_length=1, max_length=100)
    team_members: List[TeamMemberBase] = Field(..., min_items=4, max_items=4)
    
    @validator('team_members')
    def validate_team_members(cls, v):
        """Validate exactly 4 members and exactly 1 team leader."""
        if len(v) != 4:
            raise ValueError('Team must have exactly 4 members')
        
        leaders = [m for m in v if m.is_leader]
        if len(leaders) != 1:
            raise ValueError('Team must have exactly 1 leader')
        
        return v


class TeamMemberResponse(BaseModel):
    """Response schema for team member."""
    id: UUID
    name: str
    email: str
    moodle_id: str
    roll_no: str
    division: str
    department: str
    year: str
    mobile: str
    is_leader: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class HackathonTeamResponse(BaseModel):
    """Response schema for hackathon team."""
    id: UUID
    event_name: str
    team_name: str
    created_at: datetime
    members: List[TeamMemberResponse] = []
    
    class Config:
        from_attributes = True
