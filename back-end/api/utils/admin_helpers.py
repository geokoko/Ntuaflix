from fastapi import HTTPException, status
from ..database import get_database_connection
import asyncio

#Admin Endpoint 4
async def insert_into_name(values):
    # Replace '\\N' with None for nullable columns
    values = [None if (val == '\\N' or val == '/N') else val for val in values]

    query = """
        INSERT INTO `Person` (Name_ID, Name, Image, Birth_Year, Death_Year) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Name_ID = VALUES(Name_ID),
        Image = VALUES(Image)
    """

    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, values)
        await connection.commit()
        person_id = cursor.lastrowid
        if person_id:
            print(f"Insert into 'Person' successful with PK = {person_id}")
        else:
            person_id = await fetch_person_primary_key(values[0])

        return person_id

async def insert_into_profession(values):
    values = [None if (val == '\\N' or val == '/N') else val for val in values]
    profession_name = values[0]

    # Check if the profession already exists in the 'Profession' table
    query_check = "SELECT `ID` FROM `Profession` WHERE `Profession` = %s LIMIT 1"
    query_insert = """
                INSERT INTO `Profession` (Profession) 
                VALUES (%s)
                ON DUPLICATE KEY UPDATE
                Profession = VALUES(Profession)
            """
    async with await get_database_connection() as connection, connection.cursor() as cursor:
         # If the profession doesn't exist, insert it into the 'Profession' table
        await cursor.execute(query_insert, (profession_name,))
        await connection.commit()
        profession_id = cursor.lastrowid
        if profession_id:
            print(f"Insert into 'Profession' successful with ID {profession_id}")
        else:
            profession_id = await fetch_profession_primary_key(profession_name)
        # Return the ID of the profession (existing or newly inserted)
        return profession_id

count = 0
async def insert_into_profession_person(values):
    values = [None if (val == '\\N' or val == '/N') else val for val in values]
    
    query = """
        INSERT INTO `Profession_Person` (Profession_FK, Name_FK) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
        Profession_FK = VALUES(Profession_FK),
        Name_FK = VALUES(Name_FK)
    """
    global count
    async with await get_database_connection() as connection, connection.cursor() as cursor:

        try:
            await cursor.execute(query, values)
            await connection.commit()
            count += 1

            print(f"Insert into 'Profession_Person' successful{count}")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise  # Re-raise the exception to see the full traceback
        

async def fetch_profession_primary_key(profession_name, retry=3, delay=0.1):
    try:
        while retry > 0:
            query = "SELECT `ID` FROM `Profession` WHERE `Profession` = %s LIMIT 1"
            async with await get_database_connection() as connection, connection.cursor() as cursor:
                await cursor.execute(query, (profession_name,))
                result = await cursor.fetchall()
                print(f"Just fetched PROFESSION primary key: {result}")

                if result:
                    return result[0][0]
                retry -= 1
                await asyncio.sleep(delay)
                print("Retrying...")

        return None
    except Exception as e:
        print(f"Error executing query at person primary key: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
#Admin Endpoint 5
async def check_existing_participation(name_fk, title_fk, job_category):
    #values = [None if (val == '\\N' or val == '/N') else val for val in values]

    query = "SELECT 1 FROM `Participates_In` WHERE `Name_FK` = %s AND `Title_FK` = %s AND `Job_Category` = %s LIMIT 1"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (name_fk, title_fk, job_category))
        result = await cursor.fetchone()
        return result is not None

async def insert_into_title(values):

    query_select = "SELECT * FROM `Title` WHERE Title_ID = %s"
    query_insert = """
        INSERT INTO `Title` (Title_ID, Original_Title, Type) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Title_ID = VALUES(Title_ID),
        Original_Title = VALUES(Original_Title),
        Type = VALUES(Type)
    """

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
    query = """
        INSERT INTO `Episode` (Title_FK, Parent_Title_FK, Season, Episode_Num) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Title_FK = VALUES(Title_FK),
        Parent_Title_FK = VALUES(Parent_Title_FK),
        Season = VALUES(Season),
        Episode_Num = VALUES(Episode_Num)
    """

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
    query = """
        INSERT INTO `Participates_In` (Title_FK, Name_FK, Ordering, Job_Category, `Character`) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Title_FK = VALUES(Title_FK),
        Name_FK = VALUES(Name_FK),
        Ordering = VALUES(Ordering),
        Job_Category = VALUES(Job_Category),
        `Character` = VALUES(`Character`)
    """

    #check_query = """
        #SELECT Ordering FROM `Participates_In` WHERE Title_FK = %s AND Name_FK = %s AND Job_Category = %s
    #"""
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        try:
            values = [None if (v == '\\N' or v == '/N') else v for v in values]
            #await cursor.execute(check_query, (values[0], values[1], values[3]))
            #result = await cursor.fetchone()
            #if result is not None and result[0] is not None:
                #raise HTTPException(status_code=500, detail="Duplicate entry encountered: Ordering is not NULL")
            await cursor.execute(query, values)
            await connection.commit()
            #print("Insert successful")
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

async def fetch_person_primary_key(nconst, retry=3, delay=0.1):
    query = "SELECT `ID` FROM `Person` WHERE `Name_ID` = %s LIMIT 1"
    try:
        while retry > 0:
            async with await get_database_connection() as connection, connection.cursor() as cursor:
                await cursor.execute("SELECT `ID` FROM `Person` WHERE `Name_ID` = %s LIMIT 1", (nconst,))
                result = await cursor.fetchone()
                if result:
                    return result[0]
                retry -= 1
                await asyncio.sleep(delay)  # Wait before retry
        return None
    except Exception as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
            

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

async def insert_into_participates_in_crew(values):
    query = """
        INSERT INTO `Participates_In` (Title_FK, Name_FK, Job_Category) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Title_FK = VALUES(Title_FK),
        Name_FK = VALUES(Name_FK),
        Job_Category = VALUES(Job_Category)
    """

    async with await get_database_connection() as connection, connection.cursor() as cursor:
        try:
            values = [None if (v == '\\N' or v == '/N') else v for v in values]
            await cursor.execute(query, values)
            await connection.commit()
            print("Insert successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

