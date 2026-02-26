"""Admin authentication endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserResponse
from app.security import verify_password, create_access_token
from app.utils.errors import UnauthorizedError, create_error_response
from app.dependencies import get_current_user
from app.middleware.rate_limit import get_rate_limiter
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = get_rate_limiter()


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login endpoint.
    
    - **username**: Admin username
    - **password**: Admin password
    
    Returns JWT access token on successful authentication.
    Rate limited to 5 attempts per 15 minutes per IP.
    """
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_seconds
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user
