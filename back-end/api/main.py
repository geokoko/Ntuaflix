from fastapi import FastAPI
from api.routes import routes
from .database import create_db_pool, close_db_pool

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await create_db_pool()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()

app.include_router(routes.router)
