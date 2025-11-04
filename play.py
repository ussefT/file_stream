from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import FileResponse,HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import te
from urllib.parse import unquote
app=FastAPI()

# app.mount('/static',StaticFiles(directory='static'),name='static')

templates=Jinja2Templates(directory='templates')


@app.get('/',response_class=HTMLResponse)
async def read(req:Request):
    """Get item in path"""
    files=[file for file in te.getFiles('/home')][0]
    return templates.TemplateResponse(
        request=req,name='index.html',context={"files":files,'path':Path('/home').absolute().as_posix()}
        )



@app.get('/dir')
def dir(req:Request):
    if req.url.query:
        path=req.url.query
        if Path(path).exists():
            if Path(path).is_dir():
                files=[file for file in te.getFiles(path)][0]
                return templates.TemplateResponse(
                        request=req,name='index.html',context={'files':files,'request':req
                        ,'path':path})
            else:
                return HTTPException(status_code=406,detail="This file not dir")
        else:
            return HTTPException(status_code=404,detail="Not found")
    else:
        return HTTPException(status_code=400,detail="Bad Request")
    
@app.get('/play')
def play(req:Request,file:str):
    """"""
    # path=req.url.query
    print(repr(file))
    # if file.endswith('.mp4') and file.endswith('.mkv'):
    #
    #     return FileResponse(path=file,filename=file.split('/')[-1],media_type="video/mp4")
    # elif file.endswith('.png') and file.endswith('.png'):
    #     pass
    # else:
    #     return FileResponse(path=file,filename=file.split('/')[-1])




