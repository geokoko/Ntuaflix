from fastapi import HTTPException, status
from ..database import get_database_connection

#Admin Endpoint 4
async def insert_into_name(values):
    # Replace '\\N' with None for nullable columns
    values = [None if (val == '\\N' or val == '/N') else val for val in values]

    query = "INSERT INTO Person (Name_ID, Name, Image, Birth_Year, Death_Year) VALUES (%s, %s, %s, %s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        try:
            await cursor.execute(query, values)
            await connection.commit()
            print("Insert into 'Person' successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise  # Re-raise the exception to see the full traceback

async def insert_into_profession(values):
    values = [None if (val == '\\N' or val == '/N') else val for val in values]
    profession_name = values[0]

    # Check if the profession already exists in the 'Profession' table
    query_check = "SELECT `ID` FROM `Profession` WHERE `Profession` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query_check, (profession_name,))
        result = await cursor.fetchone()

        if result:
            # If the profession already exists, return its ID
            return result[0]
        
        else:
            # If the profession doesn't exist, insert it into the 'Profession' table
            query_insert = "INSERT INTO `Profession` (Profession) VALUES (%s)"
            await cursor.execute(query_insert, (profession_name,))
            await connection.commit()
            print("Insert into 'Profession' successful")

            # Return the ID of the profession (existing or newly inserted)
            return await fetch_profession_primary_key(profession_name)


async def insert_into_profession_person(values):
    values = [None if (val == '\\N' or val == '/N') else val for val in values]
    
    query = "INSERT INTO `Profession_Person` (Profession_FK, Name_FK) VALUES (%s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:

        try:
            await cursor.execute(query, values)
            await connection.commit()
            print("Insert into 'Profession_Person' successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise  # Re-raise the exception to see the full traceback
        

async def fetch_profession_primary_key(profession_name):
    query = "SELECT `ID` FROM `Profession` WHERE `Profession` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (profession_name,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
#Admin Endpoint 5
async def check_existing_participation(name_fk, title_fk, job_category):
    values = [None if (val == '\\N' or val == '/N') else val for val in values]

    query = "SELECT 1 FROM `Participates_In` WHERE `Name_FK` = %s AND `Title_FK` = %s AND `Job_Category` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (name_fk, title_fk, job_category))
        result = await cursor.fetchone()
        return result is not None

async def insert_into_title(values):

    query_select = "SELECT * FROM `Title` WHERE Title_ID = %s"
    query_insert = "INSERT INTO `Title` (Title_ID, Original_Title,Type) VALUES (%s, %s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
    
        # Start a transaction
        await connection.begin()
        
        try:
            values = [None if (v == '\\N' or v == '/N') else v for v in values]
            # Check if the Title_ID already exists
            await cursor.execute(query_select, (values[0],))
            existing_row = await cursor.fetchone()

            # If the Title_ID already exists, roll back the transaction
            if existing_row:
                print(f"Duplicate entry for Title_ID: {values[0]}")
                await connection.rollback()
                return

            # If the Title_ID doesn't exist, proceed with insertion
            await cursor.execute(query_insert, values)
            await connection.commit()
        except Exception as e:
            # If any error occurs during insertion, roll back the transaction
            await connection.rollback()
            raise e


async def insert_into_episode(values):
    query = "INSERT INTO `Episode` (Title_FK, Parent_Title_FK, Season, Episode_Num) VALUES (%s, %s, %s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        try:
            values = [None if (v == '\\N' or v == '/N') else v for v in values]
            await cursor.execute(query, values)
            await connection.commit()
            print("Insert successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise  # Re-raise the exception to see the full traceback

#Admin Endpoint 7
async def insert_into_participates_in(values):
    query = "INSERT INTO `Participates_In` (Title_FK, Name_FK, Ordering, Job_Category, `Character`) VALUES (%s, %s, %s, %s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        try:
            values = [None if (v == '\\N' or v == '/N') else v for v in values]
            await cursor.execute(query, values)
            await connection.commit()
            print("Insert successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        
async def fetch_title_primary_key(tconst):
    query = "SELECT `ID` FROM `Title` WHERE `Title_ID` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (tconst,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

async def fetch_person_primary_key(nconst):
    query = "SELECT `ID` FROM `Person` WHERE `Name_ID` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (nconst,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        

# Function to update data in the Title table
async def update_title_ratings(title_id, average_rating, num_votes):
    query = "UPDATE `Title` SET `Average_Rating` = %s, `Votes` = %s WHERE `Title_ID` = %s"
    async with await get_database_connection() as connection, connection.cursor() as cursor:

        try:
            await cursor.execute(query, (average_rating, num_votes, title_id))
            await connection.commit()
            print("Insert successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
