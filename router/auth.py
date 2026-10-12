from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta,timezone
from passlib.context import CryptContext
from database import Sessionlocal
from models import User
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt,JWTError



router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl = "/auth/login")

SECRET_KEY = '4a43eebfcb7d954046736a0a60c3e16cb8e2bb89fc6b3a169b8fd0dcd529abd6'
ALGORITHM = 'HS256'

class CreateUsers(BaseModel):
    user_name : str
    email : str
    password : str
    
def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username,password,db):
    user = db.query(User).filter(User.user_name == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password, user.hash_password):
        return user
    return False


def  create_access_token(usename : str, user_id : int, expires_date : timedelta):
    encode = {'sub': usename,'id': user_id }
    expires = datetime.now(timezone.utc) + expires_date
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY,algorithm= ALGORITHM)


def  get_current_user(token : Annotated[str, Depends(OAuth2_bearer)], db : db_dependency):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= ALGORITHM)
        username = str = payload.get('sub')
        user_id = int = payload.get('id')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail='User not found')
        return {'username': username , 'id': user_id}
    except:
        raise HTTPException(status_code=404, detail='User not found')
    


@router.post("/auth/register")
def register_user(new_user : CreateUsers, db : db_dependency):
    user = db.query(User).filter(User.user_name == new_user.user_name).first()
    if user :
        raise HTTPException(status_code = 400, detail='Username already exists')
    user_model = User(
        user_name = new_user.user_name,
        email  = new_user.email,
        hash_password = bcrypt_context.hash(new_user.password)
    )
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    
    return{
        "id": user_model.id,
        "user_name": user_model.user_name,
        "email": user_model.email
    }

@router.post("/auth/login")
def user_login(db: db_dependency,from_data : Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(from_data.username, from_data.password,db)
    if not  user:
        raise HTTPException(status_code=401 , detail='Incorrect username or password')
    token = create_access_token(user.user_name, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}