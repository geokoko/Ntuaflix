import os
import asyncio
from datetime import datetime
import aiomysql
from dotenv import load_dotenv
from pathlib import Path
import re

load_dotenv()

db_pool = None

# Creates a Backup of the most recent database version
async def create_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    command = f"mysqldump -u {os.environ.get('DB_USER')} -p{os.environ.get('DB_PASSWD')} {os.environ.get('DB_NAME')} > {backup_file}"

    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            return {"status": "success", "backup_file": backup_file}
        else:
            return {"status": "failed", "error": stderr.decode()}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# Picks the backup that was created first
async def pick_backup():
    backup_dir = Path(__file__).resolve().parent.parent / 'db' / 'backups'
    
    try:
        backups = [f for f in os.listdir(backup_dir) if re.match(r'backup_\d{4}-\d{2}-\d{2}_\d{6}\.sql', f)]
        return {"available_backups": backups}
    except Exception as e:
        return {"available_backups": None, "error": str(e)}

# Restores database given a backup file
async def restore():
    choices = await pick_backup()
    if not choices["available_backups"][0]:
        return {"status": "failed", "error": "No backup files available"}
    
    choices["available_backups"].sort()
    backup_file = choices["available_backups"][0]

    command = f"mysql -u {os.environ.get('DB_USER')} -p{os.environ.get('DB_PASSWD')} {os.environ.get('DB_NAME')} < {backup_file}"

    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            return {"status": "success"}
        else:
            return {"status": "failed", "error": stderr.decode()}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

async def check_connection():
    try:
        async with get_database_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "dataconnection": str(e)}

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
