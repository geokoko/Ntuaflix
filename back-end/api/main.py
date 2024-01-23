from fastapi import FastAPI
<<<<<<< HEAD
from .routes import routes
=======
from api.routes import routes
>>>>>>> 9551302 (Changes to back-end:)
from .database import create_db_pool, close_db_pool

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await create_db_pool()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()

<<<<<<< HEAD
app.include_router(routes.router)

=======
app.include_router(routes.router)
>>>>>>> 9551302 (Changes to back-end:)
