from models import User_Auth 
from schemas import UserCreate
from utils.auth import get_password_hash
from sqlalchemy.orm import Session


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    
    db_user = User_Auth(  # Changed
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(User_Auth).filter(User_Auth.username == username).first()  # Changed


def get_user_by_email(db: Session, email: str):
    return db.query(User_Auth).filter(User_Auth.email == email).first()  # Changed