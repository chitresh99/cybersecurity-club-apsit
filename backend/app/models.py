"""SQLAlchemy database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Integer, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class EventType(str, enum.Enum):
    """Event type enumeration."""
    WORKSHOP = "Workshop"
    HACKATHON = "Hackathon"
    SEMINAR = "Seminar"
    BOOTCAMP = "Bootcamp"
    LECTURE = "Lecture"


class ResourceLevel(str, enum.Enum):
    """Resource level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class User(Base):
    """Admin user model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<User(username={self.username})>"


class Event(Base):
    """Event model."""
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    type = Column(SQLEnum(EventType), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(title={self.title}, type={self.type})>"


class Registration(Base):
    """Event registration model."""
    __tablename__ = "registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    operative_name = Column(String(100), nullable=False)
    moodle_id = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="registrations")
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (
        UniqueConstraint('event_id', 'moodle_id', name='unique_event_moodle'),
    )
    
    def __repr__(self):
        return f"<Registration(moodle_id={self.moodle_id}, event_id={self.event_id})>"


class Resource(Base):
    """PDF resource model."""
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    level = Column(SQLEnum(ResourceLevel), nullable=False)
    file_url = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Resource(title={self.title}, level={self.level})>"


class HackathonTeam(Base):
    """Hackathon team registration model."""
    __tablename__ = "hackathon_teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = Column(String(200), nullable=False, index=True)
    team_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    
    # Unique constraint for team name per event
    __table_args__ = (
        UniqueConstraint('event_name', 'team_name', name='unique_event_team_name'),
    )
    
    def __repr__(self):
        return f"<HackathonTeam(team_name={self.team_name}, event={self.event_name})>"


class TeamMember(Base):
    """Hackathon team member model."""
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_teams.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    moodle_id = Column(String(20), nullable=False, index=True)
    roll_no = Column(String(20), nullable=False)
    division = Column(String(5), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(String(10), nullable=False)
    mobile = Column(String(15), nullable=False)
    is_leader = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    team = relationship("HackathonTeam", back_populates="members")
    
    def __repr__(self):
        return f"<TeamMember(name={self.name}, team_id={self.team_id})>"
