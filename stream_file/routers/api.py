from auth.gen_auth import get_token
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from utils import getFiles
import asyncio

router=APIRouter(tags=['API'],prefix="/api")

# show dir json
@router.get('/dir')
async def getDir(req=Depends(get_token)):
    
    # files=[i for i in getFiles('.')]
    files = await asyncio.to_thread(list, getFiles("."))
    first_file = files[0] if files else None

    return JSONResponse(
        content={"result":req,"message":first_file},
        status_code=status.HTTP_200_OK,
        headers={
            "Content-Type":"application/json",
            "X-Frame-Options":"DENY",
            "X-Content-Type-Options":"nosniff",
            "Cache-Control":"no-cache",
            "ETag":"x123456",
            "Strict-Transport-Security":"max-age=31536000; includeSubDomains"
            },
        )



