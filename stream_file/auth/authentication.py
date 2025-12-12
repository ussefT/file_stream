from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from auth.gen_auth import create_access_token
from utils import random_digit

router=APIRouter(prefix="/token",tags=["token"])
# create token
@router.get('/')
async def token():
    access_token=create_access_token({"id":random_digit(5)})
    return JSONResponse(
                        content={"token":access_token},
                        status_code=200
                        )