import mysql.connector as sql
from mysql.connector import Error

def get_database_connection():
    try:
        connection = sql.connect(
            host='localhost', 
            database='tl', 
            user='geokoko', 
            password=''
        )
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
