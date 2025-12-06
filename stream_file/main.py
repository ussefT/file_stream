from fastapi import FastAPI
from routers.app import router as templates
from routers.api import router as api
# init fastapi
app = FastAPI()

# template
app.include_router(templates,prefix='')

# json
app.include_router(api,prefix="/api")
