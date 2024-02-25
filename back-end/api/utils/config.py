from dotenv import load_dotenv
import os

current_script_path = os.path.abspath(__file__)
project_root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
dotenv_path = os.path.join(project_root_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWD = os.getenv('DB_PASSWD')
