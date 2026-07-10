from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models import User
from app.schemas import UserCreate, UserLogin
from app.security import get_password_hash, verify_password

class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Queries database for user by email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Queries database for user by unique user ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Registers a new user after validating email uniqueness and hashes password."""
        # Check password strength first
        from app.security import validate_password_strength
        validate_password_strength(user_data.password)

        # Check if email is already registered
        existing_user = AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered"
            )

        # Hash user password
        hashed_password = get_password_hash(user_data.password)


        # Create new user record
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> User:
        """Authenticates user email and password, returning user instance if valid."""
        # Find user by email
        user = AuthService.get_user_by_email(db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate password hash
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
