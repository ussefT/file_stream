from fastapi import FastAPI
from router import router

# init fastapi
app = FastAPI()

# template
app.include_router(router)


