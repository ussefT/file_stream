from fastapi import FastAPI
from routers.app import router as templates
from routers.api import router as api
from auth.authentication import router as auth
from fastapi.staticfiles import StaticFiles

# init fastapi
app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")

# auth
app.include_router(auth)

# template
app.include_router(templates,prefix='')

# json
app.include_router(api)

