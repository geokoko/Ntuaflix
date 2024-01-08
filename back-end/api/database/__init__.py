import os
import aiomysql
from dotenv import load_dotenv

load_dotenv()

db_pool = None

async def check_connection():
    async with get_database_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            await cursor.fetchone()
            return "Successfully connected to the database"

async def create_db_pool():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=os.environ.get('DB_HOST'), 
        db=os.environ.get('DB_NAME'), 
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWD'),
        minsize=5,
        maxsize=10
    )

async def close_db_pool():
    db_pool.close()
    await db_pool.wait_closed()

async def get_database_connection():
    return db_pool.acquire()
