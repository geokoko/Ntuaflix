from fastapi import APIRouter, HTTPException
from typing import List
from api.models import TitleObject, NameObject
from api.database import get_database_connection

router = APIRouter()

# Index
@router.get("/")
def browse_titles():
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `Title`")
        titles = cursor.fetchall()
        cursor.close()
        db_connection.close()
        if titles:
            return titles
        else:
            raise HTTPException(status_code=404, detail="No titles found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search by title
@router.get("/title/{titleID}", response_model=TitleObject)
def get_title_details(titleID: str):
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM 'Title' WHERE 'Title_ID' = %s", (titleID,))
        title = cursor.fetchone()
        cursor.close()
        db_connection.close()
        if title:
            return title
        else:
            raise HTTPException(status_code=404, detail="Title not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Title search query
@router.get("/searchtitle", response_model=List[TitleObject])
def search_titles(query: str):
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `Title` WHERE `Original_Title` LIKE %s", (f'%{query}%',))
        titles = cursor.fetchall()
        cursor.close()
        db_connection.close()
        if titles:
            return titles
        else:
            raise HTTPException(status_code=404, detail="No titles found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Genre search query
@router.get("/bygenre", response_model=List[TitleObject])
def search_genre(query: str):
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("""SELECT T.`Title_ID`, T.`Original_Title` 
                       FROM `Title` T 
                       INNER JOIN `Title_Genre` TG ON T.`Title_ID` = TG.`Title_ID` 
                       INNER JOIN `Genre` G ON TG.`Genre_ID` = G.`Genre_ID`
                       WHERE G.`Genre` LIKE %s""", (f'%{query}%',))
        titles = cursor.fetchall()
        cursor.close()
        db_connection.close()
        if titles:
            return titles
        else:
            raise HTTPException(status_code=404, detail="No titles found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/name/{nameID}", response_model=NameObject)
def get_name_details(nameID: str):
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("""SELECT * FROM `Person` WHERE 'Name' = %s""", (nameID,))
        names = cursor.fetchall()
        cursor.close()
        db_connection.close()
        if names:
            return names
        else:
            raise HTTPException(status_code=404, detail="No people found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/searchname")
def search_name(query: str):
    ### Implementation here
    pass