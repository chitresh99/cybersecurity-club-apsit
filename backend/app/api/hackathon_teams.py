"""Hackathon team registration endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.database import get_db
from app.models import HackathonTeam, TeamMember
from app.schemas import HackathonTeamCreate, HackathonTeamResponse
from app.utils.errors import ConflictError
from app.utils.validation import sanitize_string

router = APIRouter(prefix="/api/hackathon-teams", tags=["Hackathon Teams"])


@router.post("", response_model=HackathonTeamResponse, status_code=status.HTTP_201_CREATED)
def create_hackathon_team(
    team_data: HackathonTeamCreate,
    db: Session = Depends(get_db)
):
    """Register a hackathon team (Public).
    
    - **event_name**: Name of the hackathon event
    - **team_name**: Unique team name
    - **team_members**: List of exactly 4 team members (1 must be leader)
    
    Each team member must have:
    - name, email, moodle_id, roll_no, division,department, year, mobile
- is_leader (exactly 1 member must be the leader)
    
    Prevents duplicate team names for the same event.
    """
    # Sanitize team name
    team_name = sanitize_string(team_data.team_name, max_length=100)
    
    # Create team
    team = HackathonTeam(
        event_name=team_data.event_name,
        team_name=team_name
    )
    
    try:
        db.add(team)
        db.flush()  # Get team ID before adding members
        
        # Create team members
        for member_data in team_data.team_members:
            member = TeamMember(
                team_id=team.id,
                name=sanitize_string(member_data.name, max_length=100),
                email=member_data.email.lower(),
                moodle_id=member_data.moodle_id,
                roll_no=member_data.roll_no,
                division=member_data.division.upper(),
                department=member_data.department,
                year=member_data.year,
                mobile=member_data.mobile,
                is_leader=member_data.is_leader
            )
            db.add(member)
        
        db.commit()
        db.refresh(team)
        
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"Team name '{team_name}' already exists for {team_data.event_name}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team: {str(e)}"
        )
    
    return team


@router.get("", response_model=List[HackathonTeamResponse], status_code=status.HTTP_200_OK)
def get_hackathon_teams(
    event_name: str = None,
    db: Session = Depends(get_db)
):
    """Get all hackathon teams (Public for now).
    
    - **event_name**: Optional filter by event name
    """
    query = db.query(HackathonTeam)
    
    if event_name:
        query = query.filter(HackathonTeam.event_name == event_name)
    
    teams = query.order_by(HackathonTeam.created_at.desc()).all()
    return teams


@router.get("/{team_id}", response_model=HackathonTeamResponse, status_code=status.HTTP_200_OK)
def get_hackathon_team(
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single hackathon team by ID (Public for now).
    
    - **team_id**: UUID of the team
    """
    team = db.query(HackathonTeam).filter(HackathonTeam.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )
    
    return team
