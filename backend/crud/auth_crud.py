from models import User_Auth 
from schemas import UserCreate
from utils.auth import get_password_hash
from sqlalchemy.orm import Session
from sqlalchemy import func


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    
    db_user = User_Auth(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        # is_active=True  
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_by_username(db: Session, username: str):
    clean_username = username.strip()
    return db.query(User_Auth).filter(func.lower(User_Auth.username) == clean_username.lower()).first()


def get_user_by_email(db: Session, email: str):
    clean_email = email.strip()
    return db.query(User_Auth).filter(func.lower(User_Auth.email) == clean_email.lower()).first()


def reset_password(db: Session, identifier: str, new_password: str):
    clean_id = identifier.strip()
    db_user = db.query(User_Auth).filter(
        (func.lower(User_Auth.email) == clean_id.lower()) |
        (func.lower(User_Auth.username) == clean_id.lower())
    ).first()
    if not db_user:
        return None
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user