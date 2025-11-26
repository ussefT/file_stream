from pathlib import Path
from urllib.parse import unquote
from fastapi import FastAPI, Request, HTTPException ,Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from functools import wraps
import te

# init fastapi
app = FastAPI()

# init template
templates = Jinja2Templates(directory='templates')

def permission_check(path:str='.'):
        if te.getPermissionFile(path).get('r',False):
            return HTTPException(status_code=403,detail="No permission to read")
        elif te.getPermissionFile(path).get('w',False):
            return HTTPException(status_code=403,detail="No permission to write")
        elif te.getPermissionFile(path).get('e',False):
            return HTTPException(status_code=403,detail="No permission to execute")
            

# main page
@app.get('/', response_class=HTMLResponse)
async def read(request: Request,path:str=Depends(permission_check)):
    """
    Get item in path
    """
    files = [file for file in te.getFiles('.')][0]
    drives = te.getDisk()
    return templates.TemplateResponse(
        request=request, name='index.html',
        context={"files": files, 'drives': drives, 'path': Path('.').absolute().as_posix()}
    )


# directory
@app.get('/dir')
def dir(req: Request):
    """
    Get directory from url and return file, request, path
    """
    if req.url.query:
        path = unquote(req.url.query)

        if Path(path).exists():

            if Path(path).is_dir():
                files = [file for file in te.getFiles(path)][0]
                drives = te.getDisk()
                
                return templates.TemplateResponse(
                    request=req, name='index.html', context={'files': files,'drives':drives, 'request': req
                        , 'path': path})
                
            else:
                # if request not directory
                return HTTPException(status_code=406, detail="This file not dir")

        else:
            # if not exist file
            return HTTPException(status_code=404, detail="Not found")

    else:
        # if bad url 
        return HTTPException(status_code=400, detail="Bad Request")


# show file
@app.get('/play')
def play(req: Request, file: str):
    """
    Exist file, downlaod or stream 
    """

    per_to_read=te.getPermissionFile(file).get('r',False)
    
    if per_to_read:
        if file.endswith('.mp4') and file.endswith('.mkv'):
            
                return FileResponse(path=file, filename=file.split('/')[-1], media_type="video/mp4")
                  
        elif file.endswith('.png') and file.endswith('.png'):
            
            pass
        
        else:
            
            return FileResponse(path=file, filename=file.split('/')[-1])
        
    else:
                return HTTPException(status_code=403,detail="Not Permission Read File")
