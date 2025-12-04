from datetime import timedelta, datetime
from typing import Union, Any


from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request,Header
from fastapi.responses import JSONResponse,RedirectResponse
from fastapi.security import HTTPBearer
from jose import JWTError,jwt

from te import getFiles

router=APIRouter()


SECRET_KEY = "00"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


    
def create_token(pyalod:dict,expires_minute:int=ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = pyalod.copy()
    expire=datetime.utcnow() + timedelta(minutes=expires_minute)
    to_encode.update({"expipre":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


def verify_token(authorization:str=Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401,detail="Token is missing")

    try:
        scheme,token=authorization.split()
        
        if scheme.lower() !="bearer":
            raise HTTPException(status_code=401,detail="Invalid auth scheme")
        
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        return payload
    except JWTError:
        raise HTTPException(status_code=401,detail="Token is expired or invalid")


@router.get('/dir')
async def getDir(req:Request,payload=Depends(verify_token)):

    files=[i for i in getFiles('.')]
    return JSONResponse(
        {"message":files[0],"payload":payload},
        status_code=200,
        headers={
            "Content-Type":"application/json",
            "X-Frame-Options":"Deny",
            "X-Content-Type-Options":"nosniff",
            "Cache-Control":"no-cache",
            "ETag":"x123456",
            "Strict-Transport-Security":"max-age=31536000; includeSubDomains"
            },
        )



@router.get('/token')
async def token(req: Request):
    return JSONResponse(
                        content={"token":create_token({"service": "internal"})},
                        status_code=200
                        )
