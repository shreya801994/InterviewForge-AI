from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.security import create_access_token, decode_access_token
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# OAuth2 scheme for extracting token from header (bearer token authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form", auto_error=False)

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Dependency to validate JWT token and return active current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("user_id")
    email: str = payload.get("sub")
    if user_id is None or email is None:
        raise credentials_exception
        
    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
        
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user and returns their profile details."""
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns JWT bearer token."""
    user = AuthService.authenticate_user(db, login_data)
    
    # Create token payload
    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "name": user.name
    }
    
    access_token = create_access_token(data=token_payload)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieves current user details based on authenticated session."""
    return current_user


# Swagger-friendly login route using standard OAuth2 Form parameters (optional convenience)
from fastapi.security import OAuth2PasswordRequestForm
@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_swagger(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    user = AuthService.authenticate_user(db, login_data)
    
    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "name": user.name
    }
    
    access_token = create_access_token(data=token_payload)
    return Token(access_token=access_token, token_type="bearer")
