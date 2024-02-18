import os
import asyncio
from datetime import datetime
import aiomysql
from dotenv import load_dotenv
from pathlib import Path
import re
from fastapi import HTTPException
from sys import platform
import subprocess
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import HTTPException, status

current_script_path = os.path.abspath(__file__)
project_root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
dotenv_path = os.path.join(project_root_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

db_pool = None
BACKUP_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'db' , 'backups')
RESET_FILE = os.path.join(Path(__file__).resolve().parent.parent.parent, 'db' , 'data', 'database_init.py')

# Resets the database to its initial state
async def reset_database():
    try:
        print("Starting reset procedure...")
        result = await asyncio.create_subprocess_exec("python3", RESET_FILE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await result.communicate()

        print("Script has been executed...")

        if result.returncode == 0:
            return {"status": "OK", "details": stdout.decode()}
        else:
            return {"status": "failed", "reason": stderr.decode()}
        
    except result.CalledProcessError as e: # catching specific subprocess error
        raise HTTPException(status_code=500, detail=f"Database reset script failed: {e.stderr}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reset script failed: {str(e)}")

# Creates a Backup of the current database version
async def create_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.sql")
    command = f"mysqldump -u {os.environ.get('DB_USER')} -p{os.environ.get('DB_PASSWD')} {os.environ.get('DB_NAME')} > {backup_file}"

    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        return {"status": "success", "backup_file": backup_file}
        
    except proc.CalledProcessError as e:
        return {"status": "failed", "error": stderr.decode()}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# Returns all the available backups
async def pick_backup():
    try:
        backups = [BACKUP_DIR/f for f in os.listdir(BACKUP_DIR) if re.match(r'backup_\d{4}-\d{2}-\d{2}_\d{6}\.sql', f)]
        return {"available_backups": backups}
    except Exception as e:
        return {"available_backups": None, "error": str(e)}

# Restores database given a backup file
async def restore():
    choices = await pick_backup()
    if not choices["available_backups"][0]:
        raise HTTPException(status_code=404, detail="No backup files available")
    
    choices["available_backups"].sort()
    backup_file = choices["available_backups"][-1]

    print(backup_file)

    command = f"mysql -u {os.environ.get('DB_USER')} -p{os.environ.get('DB_PASSWD')} {os.environ.get('DB_NAME')} < {backup_file}"

    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            return {"status": "success"}
        else:
            return {"status": "failed", "error": stderr.decode()}
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        return {"status": "failed", "error": str(e)}

async def check_connection(format: str = 'json'):
    try:
        async with await get_database_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1;")
                await cursor.fetchone()
        data = {"status": "OK", "dataconnection": "Connection to database is OK."}
        if format == 'csv':
            csv_data = ','.join(map(str, data.values()))
            return PlainTextResponse(f"{csv_data}\n", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse(data, status_code=status.HTTP_200_OK)

    except Exception as e:
        data = {"status": "failed", "dataconnection": str(e)}
        if format == 'csv':
            csv_data = ','.join(map(str, data.values()))
            return PlainTextResponse(f"{csv_data}\n", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse(data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def create_db_pool():
    global db_pool
    try:
        db_pool = await aiomysql.create_pool(
            host=os.environ.get('DB_HOST'), 
            db=os.environ.get('DB_NAME'), 
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWD'),
            #unix_socket=('/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'),
            minsize=5,
            maxsize=10
        )
    except Exception as e:
        print(f"Failed to create database pool: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable, please try again later.")

async def close_db_pool():
    db_pool.close()
    await db_pool.wait_closed()

async def get_database_connection():
    try:
        return db_pool.acquire()
    except Exception as e:
        print(f"Failed to acquire database connection: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable, please try again later.")
