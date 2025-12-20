from fastapi import FastAPI
from routers.app import router as templates
from routers.api import router as api
from auth.authentication import router as auth
from fastapi.staticfiles import StaticFiles
from middleware.rate_limits import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


# init fastapi
app = FastAPI()

# init static files
app.mount("/static",StaticFiles(directory="static"),name="static")


# limiter for request user
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


# auth
app.include_router(auth)

# template
app.include_router(templates,prefix='')

# json
app.include_router(api)

