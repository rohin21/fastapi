from jose import jwt, JWTError
from datetime import datetime, timedelta
import models
from schema import Token, TokenData, settings
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import get_db

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')
#Secret Key
#Algo
#Expire Time
# SECRET_KEY = 'HELLO'
# ALGORITHM = 'HS256'
# TOKEN_EXPIRATION_TIME = 60


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_token


def verify_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exceptions
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exceptions
    return token_data


def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    token = verify_token(token, credential_exception)
    user = db.query(models.Users).filter(models.Users.id == token.id).first()
    return user
