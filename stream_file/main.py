from fastapi import FastAPI
from routers.app import router as templates
from routers.api import router as api
from fastapi.staticfiles import StaticFiles

# init fastapi
app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")


# template
app.include_router(templates,prefix='')

# json
app.include_router(api,prefix="/api")

