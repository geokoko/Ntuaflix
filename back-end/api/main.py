from fastapi import FastAPI
from api.routes import routes
from .database import create_db_pool, close_db_pool
from contextlib import asynccontextmanager

async def startup():
    await create_db_pool()

async def shutdown():
    await close_db_pool()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(lifespan=lifespan)
app.include_router(routes.router, prefix=routes.BASE_URL)
