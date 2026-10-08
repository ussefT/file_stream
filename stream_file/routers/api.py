from auth.gen_auth import get_token
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utils import getFiles

router=APIRouter(tags=['API'],prefix="/api")

# show dir json
@router.get('/dir')
async def getDir(req=Depends(get_token)):
    
    files=[i for i in getFiles('.')]
    return JSONResponse(
        {"result":req,"message":files[0]},
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



