from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .routes import routes
from .database import create_db_pool, close_db_pool
from contextlib import asynccontextmanager
import asyncio
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

async def startup():
    await create_db_pool()

async def shutdown():
    print("Starting shutdown process...")
    await close_db_pool()
    print("Database pool closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(lifespan=lifespan)
app.add_middleware(HTTPSRedirectMiddleware)
app.include_router(routes.router, prefix=routes.BASE_URL)
# Mount static files
app.mount("/static", StaticFiles(directory="front-end/static"), name="static")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    headers = dict(request.headers)
    # Log request details
    print(f"Request body: {body}")
    print(f"Request headers: {headers}")
    response = await call_next(request)
    return response
