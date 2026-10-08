from datetime import datetime, time, timedelta, timezone

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from utils import random_char

SECRECT_KEY=random_char(10)
ALGORITHM="HS256"

oauth2_schema=APIKeyHeader(
    name="token"
)

def create_access_token(data:dict,expire_delta:time | None=None):
    to_encode=data.copy()
    if expire_delta:
        expire=datetime.datatime.now(timezone.utc) + (expire_delta or timedelta(minutes=15))
    else:
        expire=datetime.datatime.now(timezone.utc) + (expire_delta or timedelta(minutes=15))
    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode,SECRECT_KEY,algorithm=ALGORITHM)
    return encode_jwt

def get_token(token:str=Security(oauth2_schema)):
    http_except=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate":"Bearer"}
        )
    print(token)
    if  token:
        try:
            payload=jwt.decode(token,SECRECT_KEY,algorithms=[ALGORITHM])
        except JWTError:
            raise http_except
        return payload
    else:
        raise http_except