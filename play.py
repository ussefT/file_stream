from fastapi import FastAPI,Request
from fastapi.responses import FileResponse,HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import te

app=FastAPI()

# app.mount('/static',StaticFiles(directory='static'),name='static')

templates=Jinja2Templates(directory='templates')


@app.get('/',response_class=HTMLResponse)
async def read(req:Request):
    files=te.getFiles()
    return templates.TemplateResponse(
        request=req,name='index.html',context={"files":files}
        )

@app.get('/play')
def play():
    return FileResponse(path="a2.mp4",filename="a2.mp4",media_type="video/mp4")
