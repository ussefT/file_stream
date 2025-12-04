from pathlib import Path
from urllib.parse import unquote
from fastapi import APIRouter, Request, HTTPException ,Depends
from fastapi.responses import  HTMLResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
import aiofiles
from media_type import select_media_type
import te

# init fastapi
router =APIRouter()


# init template
templates = Jinja2Templates(directory='templates')


async def permission_check(path:str='.'):
        if te.getPermissionFile(path).get('r',False):
            return  HTTPException(status_code=403,detail="No permission to read")
        elif te.getPermissionFile(path).get('w',False):
            return  HTTPException(status_code=403,detail="No permission to write")
        elif te.getPermissionFile(path).get('e',False):
            return  HTTPException(status_code=403,detail="No permission to execute")
            
@router.get("/",status_code=200)
async def welcome(req:Request):
    """
    Welcome page
    """
    pass

# home page
@router.get('/home', response_class=HTMLResponse,status_code=200)
async def home(request: Request,path:str=Depends(permission_check)):
    """
    Get item in path
    """
    files = [file for file in te.getFiles('.')][0]
    drives = te.getDisk()
    return  templates.TemplateResponse(
        request=request, name='index.html',
        context={"files": files, 'drives': drives, 'path': Path('.').absolute().as_posix()}
    )


# directory
@router.get('/dir',status_code=200)
async def dir(req: Request):
    """
    Get directory from url and return file, request, path
    """
    if req.url.query:
        path = unquote(req.url.query)

        if Path(path).exists():

            if Path(path).is_dir():
                files = [file for file in te.getFiles(path)][0]
                drives = te.getDisk()
                
                return  templates.TemplateResponse(
                    request=req, name='index.html', context={'files': files,'drives':drives, 'request': req
                        , 'path': path})
                
            else:
                # if request not directory
                return  HTTPException(status_code=406, detail="This file not dir")

        else:
            # if not exist file
            return  HTTPException(status_code=404, detail="Not found")

    else:
        # if bad url 
        return  HTTPException(status_code=400, detail="Bad Request")

# async func for download continuesly files
async def FileItera(path:str,start:int,end:int):
    """
    Iterate over files in path
    """
    chunk_size=8192
    async with aiofiles.open(path,'rb') as file:
        # seek on start
        await file.seek(start)
        # current on start
        current=start
        # loop current smaller than end
        while current <= end:
            # read size
            read_size=min(chunk_size,end-current+1)
            # chunk update
            chunk = await file.read(read_size)

            if not chunk:
                break

            yield chunk
            current+=len(chunk)

# show file
@router.get('/play')
async def play(req: Request, file: str):
    """
    Exist file, downlaod or stream 
    """
    range_header= req.headers.get('Range')
    # Check file is exist and is File
    if te.fileExists(file) and te.isFile(file):

        per_to_read= te.getPermissionFile(file).get('r',False)

        # Permission is reading
        if per_to_read:

                    file_size= te.getIntsize(file)
                    media_type= select_media_type(te.getExt(file))
                    if range_header:
                        start,end= range_header.replace("bytes=","").split("-")
                        start=int(start)
                        end=int(end) if end else file_size-1

                        headers={
                            "Content-Range": f"bytes={start}-{end}",
                            "Accept-Ranges": "bytes",
                            "Content-Length": str((end-start)+1),
                            "Content-Disposition":f"attachment; filename={te.fileName(file)}",
                        }

                        
                        print(media_type)
                        return  StreamingResponse(
                            FileItera(file,start,end),
                            status_code=206,
                            media_type=media_type,
                            headers=headers
                        )

                    
                    return  StreamingResponse(
                        FileItera(file,0,file_size-1)
                        ,media_type=media_type,
                        headers={
                            "Accept-Ranges": "bytes",
                                 "Content-Length": str(file_size),
                                 "Content-Disposition":f"attachment; filename={te.fileName(file)}"
                                 }
                        )

        else:
                    return  HTTPException(status_code=403,detail="Not Permission Read File")
    else:
        return  HTTPException(status_code=404,detail="Not Found")