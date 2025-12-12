from pathlib import Path
from urllib.parse import unquote
from fastapi import APIRouter, Request, HTTPException ,Depends,status
from fastapi import Path as fastPath
from fastapi.responses import  HTMLResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
import aiofiles
from media_type import select_media_type
import utils


# init fastapi
router =APIRouter()


# init template
templates = Jinja2Templates(directory='templates')


async def permission_check(permission:dict={"r":"read","w":"write","e":"execution"},path:str='.'):
        for key,value in permission.items():
            if utils.getPermissionFile(path).get(key,False) is False:
                raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"No permission to {value}")
        return path

# welcome
@router.get("/",status_code=200)
async def welcome(req:Request):
    """
    Welcome page
    """
    return templates.TemplateResponse(
        request=req,
        name="welcome.html",
        media_type="text/html",
    )

# home page
@router.get('/home', response_class=HTMLResponse,status_code=status.HTTP_200_OK,tags=['Directory'])
async def home(request: Request,path:str=Depends(permission_check)):
    """
    Get item in path
    """
    files = [file for file in utils.getFiles(path)][0]
    drives = utils.getDisk()
    return  templates.TemplateResponse(
        request=request, name='index.html',
        context={"files": files, 'drives': drives, 'path': Path('.').absolute().as_posix()},
        media_type="text/html"
    )


# directory
@router.get('/dir/{full_path:path}',status_code=status.HTTP_200_OK,tags=['Directory'])
async def dir(req: Request,full_path:str=fastPath(...,description="Full file path")):
    """
    Get directory from url and return file, request, path
    **path** send to url
    """
    if full_path:
        path = unquote(full_path)

        if Path(path).exists():
            
            
            if Path(path).is_dir():
                # Check permission
                path=await permission_check(path=path,permission={"r":"read"})
                
                # iter items in dir
                files = [file for file in utils.getFiles(path)][0]
                
                
                drives = utils.getDisk()
                
                return  templates.TemplateResponse(
                    request=req, name='index.html', context={'files': files,'drives':drives, 'request': req
                        , 'path': path})
                
            else:
                # if request not directory
                raise  HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This file not dir")

        else:
            # if not exist file
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    else:
        # if bad url 
        raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")



# async func for download continuesly files
async def FileItera(path:str,start:int,end:int):
    """
    Iterate over files in path
    """
    
    # 64 KB  best for concurrency
    # 128 KB  best for speed
    
    chunk_size=128 * 1024
    async with aiofiles.open(path,'rb') as file:
        # seek on start
        await file.seek(start)
        # current on start
        byte_remaining=end-start+1
        # loop current smaller than end
        while byte_remaining>0:
            # read size
            read_size=min(chunk_size,byte_remaining)
            # chunk update
            chunk = await file.read(read_size)

            if not chunk:
                break

            yield chunk
            
            # Decrease counter
            byte_remaining-=len(chunk)
        

# show file
@router.get('/file/{full_file:path}'
            ,tags=['file'],
            status_code=status.HTTP_200_OK,
            summary="Download file with Full path"
            )
async def play(req: Request, full_file: str=fastPath(...,description="file full path")):
    """
    Exist file, downlaod or stream 
    """
    # Check file is exist and is File
    if full_file:
        file=unquote(full_file)
        range_header= req.headers.get('Range')

        # check exist file and path is file 
        if utils.fileExists(file) and utils.isFile(file):

                        # full path permission
                        full_file=await permission_check(path=full_file,permission={"r":"read"})

                        file_size= utils.getIntsize(file)
                        media_type= select_media_type(utils.getExt(file))
                        if range_header:
                            start,end= range_header.replace("bytes=","").split("-")
                            start=int(start)
                            end=int(end) if end else file_size-1

                            # ensure end does not exceed file size
                            if end >=file_size:
                                end=file_size-1
                                
                            headers={
                                "Content-Range": f"bytes={start}-{end}/{file_size}",
                                "Accept-Ranges": "bytes",
                                "Content-Length": str((end-start)+1),
                                "Content-Disposition":f"attachment; filename={utils.fileName(file)}",
                            }

                            
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
                                    "Content-Disposition":f"attachment; filename={utils.fileName(file)}"
                                    }
                            )

        else:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not found")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Bad request")