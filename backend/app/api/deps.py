"""Shared API dependencies."""
from sqlalchemy.orm import Session
from app.database import get_db

# Re-export common dependencies
__all__ = ["get_db"]
