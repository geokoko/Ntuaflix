from fastapi import FastAPI
from api.routes import routes
from .database import create_db_pool, close_db_pool
from contextlib import asynccontextmanager
import asyncio

async def startup():
    cmd = ["python3", "db/data/database_init.py"]
    
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    
    stdout, stderr = await proc.communicate()
    
    if proc.returncode == 0:
        print("Database initialization script completed successfully")
        print(stdout.decode())
    else:
        print("Database initialization script failed")
        print(stderr.decode())

    await create_db_pool()

async def shutdown():
    await close_db_pool()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(routes.router)
