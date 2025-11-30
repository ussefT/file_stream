from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
from te import getFiles

router=APIRouter()


@router.get('/dir')
async def getDir(req:Request):
    files=[i for i in getFiles('.')]
    return JSONResponse(
        files[0],
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

