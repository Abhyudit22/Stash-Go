from fastapi import APIRouter , Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import  timedelta
from database import get_db
from crud import auth_crud
from schemas import UserCreate,UserResponse,Token
from utils.auth import authenticate_user, create_access_token, get_current_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register",response_model = UserResponse)
def register(user_auth: UserCreate,db:Session = Depends(get_db)):
    existing_user = auth_crud.get_user_by_username(db, user_auth.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username registered already "
        )
    existing_email = auth_crud.get_user_by_email(db, user_auth.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email registered already"
        )
    new_user = auth_crud.create_user(db, user_auth)
    return new_user

@router.post("/login", response_model = Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session=Depends(get_db)):
    user = authenticate_user(db , form_data.username,form_data.password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail ="incorrect password",
            headers = {"www-authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta = access_token_expires
    )
    return{"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user_auth: UserResponse= Depends(get_current_user)):
    return current_user_auth
