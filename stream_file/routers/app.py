import shutil
from pathlib import Path
from urllib.parse import unquote
import os
import aiofiles
import utils

from logger import logger

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi import Path as fastPath
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from middleware.rate_limits import limiter


# init fastapi
router =APIRouter(tags=['template'])


BASE_DIR=Path(__file__).resolve().parent
TEMPLATES_DIR= BASE_DIR.parent / "templates"
# init template
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# PATH_HOME
_env_root = os.getenv("APP_ROOT")
if _env_root:
     PATH_HOME = Path(_env_root).resolve()
else:
    try:
        home = Path.home()
    except RuntimeError:
        home = Path(os.environ.get("HOME") or os.environ.get("USERPROFILE") or "/data")
    desktop = home / "Desktop"
    PATH_HOME = desktop if desktop.exists() else home


async def permission_check(
    path: str | Path = PATH_HOME,
    permission: dict[str,str] | None = None,
) -> Path:
    """
    Check file or directory permissions.

    permission example:
        {"r": "read", "w": "write", "e": "execute"}
    """
    permission = permission or {"r":"read"}
    path = Path(path).resolve()

    home_cmp = Path(os.path.normcase(str(PATH_HOME)))
    path_cmp = Path(os.path.normcase(str(path)))

    if not path_cmp.is_relative_to(home_cmp):
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: outside allowed root",
         )
    
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )

    # check permission 
    perms = utils.getPermissionFile(path)


    for key, label in permission.items():
        if key == "r" and path.is_dir():
            try:
                next(path.iterdir(), None)
            except (PermissionError, OSError, ValueError):

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to read"
                )

        if not perms.get(key, False):
            action = label if isinstance(label, str) else key

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permission to {action}"
            )
    return path

# welcome
@router.get("/",status_code=200)
@limiter.limit("60/minute")
async def welcome(request:Request):
    """
    Welcome page
    """
    return templates.TemplateResponse(
        request=request,
        name="welcome.html",
        media_type="text/html",
    )

# home page
@router.get('/home', response_class=HTMLResponse,status_code=status.HTTP_200_OK,tags=['Directory'])
@limiter.limit("30/minute")
async def home(request: Request):
    """
    Get item in path
    """

    path= await  permission_check(PATH_HOME,permission={"r":"read"})

    # Files in current path
    files=next(utils.getFiles(path))
    
    # Get partition
    drives = utils.getDisk()
  
    return  templates.TemplateResponse(
        request=request, name='index.html',
        context={
                "files": files,
                'drives': drives,
                'path': path.as_posix()
                },
        media_type="text/html"
    )


# directory
@router.get('/dir/{full_path:path}',status_code=status.HTTP_200_OK,tags=['Directory'])
@limiter.limit("30/minute")
async def dir(request: Request,full_path:str=fastPath(...,description="Full file path")):
    """
    Get directory from url and return file, request, path
    **path** send to url
    """
    if full_path:
        
                # clear url from %
                path=Path(unquote(full_path))

                if not path.is_absolute():
                     path = Path("/") / path

                path_result=await permission_check(
                    path=path,permission={"r":"read"}
                    )

                # iter items in dir
                files =next(utils.getFiles(path_result))
                drives = utils.getDisk()

                return  templates.TemplateResponse(
                    request=request, name='index.html',
                    context={'files': files,
                             'drives':drives,
                              'request': request,
                              'path': path})
                
          
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
@limiter.limit("10/minute")
async def play(request: Request, full_file: str=fastPath(...,description="file full path")):
    """
    Exist file, downlaod or stream 
    """
    # Check file is exist and is File
    if full_file:
        file = unquote(full_file)

        if not Path(file).is_absolute():
             file = "/" + file

        range_header= request.headers.get('Range')

        # check exist file and path is file 
        if utils.fileExists(file) and utils.isFile(file):

                        # full path permission
                        full_file=await permission_check(path=file,permission={"r":"read"})

                        file_size= utils.getIntsize(file)
                        media_type= utils.getMime(file)
                        if range_header:
                            try:
                                start,end= range_header.replace("bytes=","").split("-")
                                start=int(start)
                                end=int(end) if end else file_size-1
                            except ValueError:
                                raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                                                    detail="Bad request")

                            # ensure end does not exceed file size
                            if end >=file_size:
                                end=file_size-1

                            fname=utils.fileName(file)
                            headers={
                                "Content-Range": f"bytes={start}-{end}/{file_size}",
                                "Accept-Ranges": "bytes",
                                "Content-Length": str((end-start)+1),
                                "Content-Disposition":f"attachment; filename={fname}; filename*=UTF-8\'\'{unquote(fname)}'",
                            }

                            
                            return  StreamingResponse(
                                        FileItera(file,start,end),
                                        status_code=206,
                                        media_type=media_type,
                                        headers=headers
                                    )

                        # normal download
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
    

def file_dublicate(des:Path|str,mode:str="reanme")->Path:
    """
    Handle duplicate destination.
    mode: "overwrite", "reject", "rename"
    """

    des = Path(des)

    if not des.exists() :
        return des
    
    if mode=="overwrite":
        return des
     
    if mode=="reject":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="File already exist")
    
    stem=des.stem
    sufix=des.suffix
    parent=des.parent
    
    i = 1
    while True:
        path_dest=parent / f"{stem} ({i}){sufix}"
        if not path_dest.exists():
            return path_dest
        i +=1
        
@router.post('/uploadFile')
@limiter.limit("10/minute")
async def upload_dur(request:Request,file:UploadFile=File(...),path:str=Form(...)):
        """Upload file"""        
         
        path = (path or "").strip() or "."

        # check permission
        upload_path=await permission_check(
            path=path,
            permission={"w":"write"}
        )

        # check path is directory
        if not upload_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload path must be a directory"
            )
        
        # user_id= request.client.host if request.client else "unknown"
        SAFETY_MARGIN = 200 * 1024 * 1024   # keep 200MB free (adjust)

        # free space from path
        free_bytes = shutil.disk_usage(str(upload_path)).free

        safe_name= utils.sanitize_filename(file.filename)
        
        save_path = upload_path / safe_name
        
        # normalize file
        final_path=file_dublicate(save_path)
        
        written=0
        chunk_size=1024*1024
        
        
        # write file
        async with aiofiles.open(final_path.absolute().as_posix(),"wb") as chunk:
                while True:
                    content=await file.read(chunk_size)
                    if not content:
                        break
                    
                    written += len(content)
                    
                    # size of path larger from space
                    if written > free_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                                            detail="File to large"
                                            )
                    
                    # size of path larger from minimum space
                    if written > (free_bytes - SAFETY_MARGIN):
                        raise HTTPException(
                            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                                            detail="Quota exceeded"
                        )

                    await chunk.write(content)
                    
        return {"status": "ok", "filename": file.filename, "path": str(upload_path)}