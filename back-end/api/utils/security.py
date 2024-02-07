import os
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = secrets.compare_digest(credentials.username, os.environ.get("ADMIN_USERNAME"))
    password = secrets.compare_digest(credentials.password, os.environ.get("ADMIN_PASSWORD"))
    if not (username and password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Basic"},)
    return credentials.username
