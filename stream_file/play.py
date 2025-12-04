from fastapi import FastAPI
from router import router as templates
from api import router as api
# init fastapi
app = FastAPI()

# template
app.include_router(templates)

# json
app.include_router(api,prefix="/api")
