from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import List, Optional
from ..models import TitleObject, NameObject, AkaTitle, PrincipalsObject, RatingObject, GenreTitle, NameTitleObject
from ..database import get_database_connection, check_connection, create_backup, restore, pick_backup
from ..utils.security import get_current_admin_user
import aiomysql
from typing import Optional
import pandas as pd

router = APIRouter()

# Index
@router.get("/")
async def browse_titles():
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM `Title`;")
                titles = await cursor.fetchall()

            if titles:
                return titles
            else:
                raise HTTPException(status_code=404, detail="No titles found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browse a specific Title
@router.get("/title/{titleID}", response_model=TitleObject)
async def get_title_details(titleID: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:

                await cursor.execute("SELECT * FROM `Title` WHERE `Title_ID` = %s;", (titleID,))
                title_data = await cursor.fetchone()
                if not title_data:
                    raise HTTPException(status_code=404, detail="Title not found")
                
                print(title_data)
                primary_key = title_data["ID"]

                await cursor.execute("""SELECT G.`Genre` as `genreTitle`
                                        FROM `Title` T
                                        INNER JOIN `Title_Genre` tg ON T.`ID` = tg.`Title_FK`
                                        INNER JOIN `Genre` G ON tg.`Genre_FK` = G.`ID`
                                        WHERE T.`ID` = %s;""", (primary_key,))
                genres_data = await cursor.fetchall()

                print(genres_data)
                
                await cursor.execute("""SELECT alt.`Title_AKA` as akaTitle, alt.`Region` as regionAbbrev
                                        FROM `Title` T
                                        INNER JOIN `Alt_Title` alt ON T.`ID` = alt.`Title_FK`
                                        WHERE T .`ID` = %s;""", (primary_key,))
                akas_data = await cursor.fetchall()

                print(akas_data)

                await cursor.execute("""SELECT p.`Name_ID` as `nameID`, p.`Name` as `name`, pi.`Job_Category` as `category`
                                        FROM `Person` p
                                        INNER JOIN `Participates_In` pi ON p.`ID` = pi.`Name_FK`
                                        WHERE p.`ID` IN (
                                            SELECT pi2.`Name_FK`
                                            FROM `Participates_In` pi2
                                            WHERE pi2.`Title_FK` = %s);""", (primary_key,))
                principals_data = await cursor.fetchall()

                print(principals_data)

                title_object = TitleObject(
                    titleID=title_data["Title_ID"],
                    type=title_data["Type"],
                    originalTitle=title_data["Original_Title"],
                    titlePoster=title_data["IMAGE"],
                    startYear=str(title_data["Start_Year"]),
                    endYear=str(title_data["End_Year"]) if title_data["End_Year"] else None,
                    genres=[GenreTitle(**g) for g in genres_data], # Due to this format I needed to change the names of the keys when returned by queries
                    titleAkas=[AkaTitle(**a) for a in akas_data],
                    principals=[PrincipalsObject(**p) for p in principals_data],
                    rating=RatingObject(avRating=title_data["Average_Rating"], nVotes=title_data["Votes"])
                )

                print(title_object)

                return title_object
            
    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Title search query
@router.get("/searchtitle", response_model=List[TitleObject])
async def search_titles(query: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM `Title` WHERE `Original_Title` LIKE %s",
                    (f'%{query}%',)
                )
                titles = await cursor.fetchall()

                full_titles = []

                for title_data in titles:
                    primary_key = title_data["ID"]

                    await cursor.execute("""SELECT G.`Genre` as `genreTitle`
                                            FROM `Title` T
                                            INNER JOIN `Title_Genre` tg ON T.`ID` = tg.`Title_FK`
                                            INNER JOIN `Genre` G ON tg.`Genre_FK` = G.`ID`
                                            WHERE T.`ID` = %s;""", (primary_key,))
                    genres_data = await cursor.fetchall()

                    print(genres_data)
                
                    await cursor.execute("""SELECT alt.`Title_AKA` as akaTitle, alt.`Region` as regionAbbrev
                                            FROM `Title` T
                                            INNER JOIN `Alt_Title` alt ON T.`ID` = alt.`Title_FK`
                                            WHERE T .`ID` = %s;""", (primary_key,))
                    akas_data = await cursor.fetchall()

                    print(akas_data)

                    await cursor.execute("""SELECT p.`Name_ID` as `nameID`, p.`Name` as `name`, pi.`Job_Category` as `category`
                                            FROM `Person` p
                                            INNER JOIN `Participates_In` pi ON p.`ID` = pi.`Name_FK`
                                            WHERE p.`ID` IN (
                                                SELECT pi2.`Name_FK`
                                                FROM `Participates_In` pi2
                                                WHERE pi2.`Title_FK` = %s);""", (primary_key,))
                    principals_data = await cursor.fetchall()

                    print(principals_data)

                    title_object = TitleObject(
                        titleID=title_data["Title_ID"],
                        type=title_data["Type"],
                        originalTitle=title_data["Original_Title"],
                        titlePoster=title_data["IMAGE"],
                        startYear=str(title_data["Start_Year"]),
                        endYear=str(title_data["End_Year"]) if title_data["End_Year"] else None,
                        genres=[GenreTitle(**g) for g in genres_data], # Due to this format I needed to change the names of the keys when returned by queries
                        titleAkas=[AkaTitle(**a) for a in akas_data],
                        principals=[PrincipalsObject(**p) for p in principals_data],
                        rating=RatingObject(avRating=title_data["Average_Rating"], nVotes=title_data["Votes"])
                    )

                    full_titles.append(title_object)

            if titles:
                return full_titles
            else:
                raise HTTPException(status_code=404, detail="No titles found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Genre search query
@router.get("/bygenre", response_model=List[TitleObject])
async def search_genre(qgenre: str, minrating: Optional[str] = 0, yrFrom: Optional[str] = None, yrTo: Optional[str] = None):
    #Validate parameters
    if not qgenre:
        raise HTTPException(status_code=400, detail="Genre query must not be empty")

    try:
        minrating = float(minrating)  # assuming minrating should be a number
    except ValueError:
        raise HTTPException(status_code=400, detail="Minimum rating must be a valid number")

    if yrFrom is not None:
        try:
            yrFrom = int(yrFrom)  # assuming yrFrom should be a valid year (integer)
            if yrFrom < 0:
                raise HTTPException(status_code=400, detail="Start year must be a positive integer")
        except ValueError:
            raise HTTPException(status_code=400, detail="Start year must be a valid year")

    if yrTo is not None:
        try:
            yrTo = int(yrTo)  # assuming yrTo should be a valid year (integer)
            if yrTo < 0:
                raise HTTPException(status_code=400, detail="End year must be a positive integer")
        except ValueError:
            raise HTTPException(status_code=400, detail="End year must be a valid year")

    if yrFrom is not None and yrTo is not None and yrFrom > yrTo:
        raise HTTPException(status_code=400, detail="Start year must be less than or equal to end year")
    
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                query_parts = [
                    "SELECT T.`ID`, T.`Type`, T.`IMAGE`, T.`Start_Year`, T.`End_Year`, T.`Votes`, T.`Title_ID`, T.`Original_Title`, T.`Average_Rating`, GROUP_CONCAT(G.Genre) AS Genres",
                    "FROM `Title` T",
                    "INNER JOIN `Title_Genre` TG ON T.`ID` = TG.`Title_FK`",
                    "INNER JOIN `Genre` G ON TG.`Genre_FK` = G.`ID`",
                    "WHERE G.`Genre` LIKE %s AND T.`Average_Rating` >= %s"
                ]
                params = [f'%{qgenre}%', minrating]

                if yrFrom is not None and yrTo is None:
                    query_parts.append("AND T.`Start_Year` >= %s")
                    params.append(yrFrom)
                if yrTo is not None and yrFrom is None:
                    query_parts.append("AND T.`Start_Year` <= %s")
                    params.append(yrTo)
                if yrTo is not None and yrFrom is not None:
                    query_parts.append("AND T. `Start_Year` BETWEEN %s AND %s")
                    params.extend([yrFrom, yrTo])

                query_parts.append("GROUP BY T.`ID`")
                final_query = " ".join(query_parts)
                await cursor.execute(final_query, params)
                titles = await cursor.fetchall()
                if not titles:
                    raise HTTPException(status_code=404, detail="No titles found")
                
                title_objects = []

                for title in titles:
                    primary_key = title["ID"]

                    await cursor.execute("""SELECT alt.`Title_AKA` as akaTitle, alt.`Region` as regionAbbrev
                                            FROM `Title` T
                                            INNER JOIN `Alt_Title` alt ON T.`ID` = alt.`Title_FK`
                                            WHERE T .`ID` = %s;""", (primary_key,))
                    akas_data = await cursor.fetchall()

                    await cursor.execute("""SELECT p.`Name_ID` as `nameID`, p.`Name` as `name`, pi.`Job_Category` as `category`
                                            FROM `Person` p
                                            INNER JOIN `Participates_In` pi ON p.`ID` = pi.`Name_FK`
                                            WHERE p.`ID` IN (
                                                SELECT pi2.`Name_FK`
                                                FROM `Participates_In` pi2
                                                WHERE pi2.`Title_FK` = %s);""", (primary_key,))
                    principals_data = await cursor.fetchall()

                    title_object = TitleObject(
                        titleID=title["Title_ID"],
                        type=title["Type"],
                        originalTitle=title["Original_Title"],
                        titlePoster=title["IMAGE"],
                        startYear=str(title["Start_Year"]),
                        endYear=str(title["End_Year"]) if title["End_Year"] else None,
                        genres =[{"genre": genre} for genre in title["Genres"].split(',')] if title["Genres"] else [],
                        titleAkas=[AkaTitle(**a) for a in akas_data],
                        principals=[PrincipalsObject(**p) for p in principals_data],
                        rating=RatingObject(avRating=title["Average_Rating"], nVotes=title["Votes"])
                    )

                    title_objects.append(title_object)
                
                return title_objects

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browse a certain person
@router.get("/name/{nameID}", response_model=NameObject)
async def get_name_details(nameID: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `ID`, `Name_ID`, `Name`, `Image`, `Birth_Year` as birthYr, `Death_Year` as deathYr 
                                        FROM `Person` 
                                        WHERE `Name_ID` = %s""", (nameID,))
                names = await cursor.fetchone()
                if not names:
                    raise HTTPException(status_code=404, detail="Person not found")

                await cursor.execute("""SELECT T.`Title_ID`, T.`ID`
                                        FROM `Person` p
                                        INNER JOIN `Participates_In` pi ON p.`ID`= pi.`Name_FK`
                                        INNER JOIN `Title` T ON pi.`Title_FK`= T.`ID`
                                        WHERE p.`ID` = %s""", (names["ID"],))
                name_titles_data = await cursor.fetchall()

                name_title_objects = []

                for title_data in name_titles_data:
                    await cursor.execute("""SELECT DISTINCT pi.`Job_Category`
                                            FROM `Title` T
                                            INNER JOIN `Participates_In` pi ON T.`ID`= pi.`Title_FK`
                                            WHERE pi.`Name_FK` = %s AND pi.`Title_FK` = %s""", (names["ID"], title_data["ID"]))
                    categories_data = await cursor.fetchall()
                    print(categories_data)

                    nt_object = NameTitleObject(
                        titleID = title_data["Title_ID"],
                        category = [c["Job_Category"] for c in categories_data]
                    )

                    name_title_objects.append(nt_object)
                    
                await cursor.execute("""SELECT p.`Profession`
                                        FROM `Profession` p
                                        INNER JOIN `Profession_Person` pp ON p.`ID`= pp.`Profession_FK`
                                        INNER JOIN `Person` pr ON pr.`ID`= p.`Name_FK`
                                        WHERE pr.`ID` = %s""", (names["ID"]))
                primary_professions = await cursor.fetchall()
                    
                name_object = NameObject(
                    nameID=names["Name_ID"],
                    name=names["Name"],
                    namePoster=names["Image"],
                    birthYr=str(names["birthYr"]),
                    deathYr=str(names["deathYr"]) if names["deathYr"] else None,
                    profession=[p["Profession"] for p in primary_professions],
                    nameTitles=name_title_objects
                )
                
                return name_object

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search by name
@router.get("/searchname", response_model=List[NameObject])
async def search_name(query: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `Name_ID`, `Name`, `Image`, `Birth_Year` as birthYr, `Death_Year` as deathYr, `ID`
                                        FROM `Person` 
                                        WHERE `Name` LIKE %s""", (f'%{query}%',))
                names = await cursor.fetchall()
                if not names:
                    raise HTTPException(status_code=404, detail="No people found")

                result = []
                for name in names:
                    await cursor.execute("""SELECT T.`Title_ID`, T.`ID`
                                            FROM `Person` p
                                            INNER JOIN `Participates_In` pi ON p.`ID`= pi.`Name_FK`
                                            INNER JOIN `Title` T ON pi.`Title_FK`= T.`ID`
                                            WHERE p.`ID` = %s""", (name["ID"],))
                    name_titles_data = await cursor.fetchall()

                    name_title_objects = []

                    for title_data in name_titles_data:
                        await cursor.execute("""SELECT DISTINCT pi.`Job_Category`
                                                FROM `Title` T
                                                INNER JOIN `Participates_In` pi ON T.`ID`= pi.`Title_FK`
                                                WHERE pi.`Name_FK` = %s AND pi.`Title_FK` = %s""", (name["ID"], title_data["ID"]))
                        categories_data = await cursor.fetchall()
                        print(categories_data)

                        nt_object = NameTitleObject(
                            titleID = title_data["Title_ID"],
                            category = [c["Job_Category"] for c in categories_data]
                        )

                        name_title_objects.append(nt_object)
                    
                    await cursor.execute("""SELECT p.`Profession`
                                            FROM `Profession` p
                                            INNER JOIN `Profession_Person` pp ON p.`ID`= pp.`Profession_FK`
                                            INNER JOIN `Person` pr ON pr.`ID`= p.`Name_FK`
                                            WHERE pr.`ID` = %s""", (names["ID"]))
                    primary_profession = await cursor.fetchall()
                    
                    name_object = NameObject(
                        nameID=name["Name_ID"],
                        name=name["Name"],
                        namePoster=name["Image"],
                        birthYr=str(name["birthYr"]),
                        deathYr=str(name["deathYr"]) if name["deathYr"] else None,
                        profession=[p["Profession"] for p in primary_profession],
                        nameTitles=name_title_objects
                    )
                    
                    result.append(name_object)
                
                return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Admin healthcheck
@router.get("/admin/healthcheck")
async def admin_health_check(username: str = Depends(get_current_admin_user)):
    try:
        return await check_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin create backup
@router.post("/admin/backup")
async def initiate_backup(username: str = Depends(get_current_admin_user)):
    try:
        return await create_backup()    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin restore database   
@router.post("/admin/resetall")
async def initiate_restore(username: str = Depends(get_current_admin_user)):
    try:
        return await restore()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
'''
# endpoint 4
@router.post("/admin/upload/namebasics")
async def upload_name_basics(file: UploadFile = File(...)):
    try:
        contents = file.file.read().decode("utf-8")

        for line in contents.split("\n"):
            # Χωρίζουμε τη γραμμή σε πεδία
            fields = line.split("\t")

            # Εάν υπάρχουν αρκετά πεδία, τα προσθέτουμε στον πίνακα (Person)
            if len(fields) >= 2:
                name_id = fields[0]
                name = fields[1]
                birth_year = fields[2] if fields[2] != "\\N" else None
                death_year = fields[3] if fields[3] != "\\N" else None
                primary_profession = fields[4]
                known_for_titles = fields[5]
                img_url_asset = fields[6]

                # Υπόλοιπη λογική για αποθήκευση των δεδομένων στον πίνακα Person
                db_connection = get_database_connection()
                cursor = db_connection.cursor()

                # Εισάγουμε στον πίνακα `Person`
                query = "INSERT INTO `Person` (`Name_ID`, `Name`, `Birth_Year`, `Death_Year`, `Image`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (name_id, name, birth_year, death_year, img_url_asset))

		#!!!!!!!Ίσως το επόμενο κομματι να το κάνουμε με trigger μέσα στην sql, το βλέπουμε
                # Εισάγουμε στους πίνακες profession και profession_person
                if primary_profession and primary_profession != "\\N":
                    # Εισαγωγή του primaryProfession στον πίνακα Profession (αν δεν υπάρχει ήδη)
                    query = "INSERT INTO `Profession` (`Profession`) VALUES (%s)"
                    cursor.execute(query, (primary_profession,))

                    # Λήψη του profession_id για το συγκεκριμένο επάγγελμα
                    query = "SELECT `Profession_ID` FROM `Profession` WHERE `Profession` = %s"
                    cursor.execute(query, (primary_profession,))
                    profession_id = cursor.fetchone()["Profession_ID"]

		            select_last_inserted_id_query = "SELECT LAST_INSERT_ID() as new_id"
		            cursor.execute(select_last_inserted_id_query)
		            result = cursor.fetchone()
		            profession_id = result['new_id'] if result else None

                    # Εισαγωγή στον πίνακα Profession_Person
                    query = "INSERT INTO `Profession_Person` (`Profession_ID`, `Name_ID`) VALUES (%s, %s)"
                    cursor.execute(query, (profession_id, name_id))

                db_connection.commit()
                cursor.close()
                db_connection.close()

        return {"message": "Data uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

# endpoint 5
# Επεξεργασία κάθε γραμμής του αρχείου
@router.post("/admin/upload/titlecrew")
def upload_titlecrew(file: UploadFile = File(...)):
    for line in contents.split("\n"):
        # Χωρίζουμε τη γραμμή σε πεδία
        fields = line.split("\t")

        # Εάν υπάρχουν αρκετά πεδία
        if len(fields) >= 3:
            title_id = fields[0]

            # Επεξεργασία σκηνοθετών
            directors = fields[1].split(",") if fields[1] and fields[1] != "\\N" else []
            for director in directors:
                # Έλεγχος αν το name_id υπάρχει στον πίνακα Person
                cursor.execute("SELECT * FROM Person WHERE Name_ID = %s", (director,))
                person_director = cursor.fetchone()

                if person_director:
                    # Εισαγωγή στον πίνακα Participates_In με job_category = 1 (τυχαιος αριθμος) αν εχουμε director. τι γινεται με αυτο το attribute στην sql;; γιατι ειναι integer; πως αντιστοιχιζεται με το profession; στο tsv το δινει string (πχ "actor") στο title_principals, μηπως να το κρατησουμε κι εμεις ετσι; θελει τροποποιηση αυτο!!!
                    cursor.execute(
                        "INSERT INTO Participates_In (Title_ID, Name_ID, Ordering, Job_Category) VALUES (%s, %s, NULL, 1)",
                        (title_id, director,)
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"Person with Name_ID {director} doesn't exist in the system")

            # Επεξεργασία συγγραφέων
            writers = fields[2].split(",") if fields[2] and fields[2] != "\\N" else []
            for writer in writers:
                # Έλεγχος αν το name_id υπάρχει στον πίνακα Person
                cursor.execute("SELECT * FROM Person WHERE Name_ID = %s", (writer,))
                person_writer = cursor.fetchone()

                if person_writer:
                    # Εισαγωγή στον πίνακα Participates_In
            #ιδιο με πριν, τωρα τον εισαγει με τον αριθμο 2 αν ειναι συγγραφεας, παλι τυχαιος αριθμος
                    cursor.execute(
                        "INSERT INTO Participates_In (Title_ID, Name_ID, Ordering, Job_Category) VALUES (%s, %s, NULL, 2)",
                        (title_id, writer,)
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"Person with Name_ID {writer} doesn't exist in the system")
        
        cursor.close()
        db_connection.commit()
        db_connection.close()

        return {"message": "Data uploaded successfully"}

# endpoint 6
@router.post("/admin/upload/titleepisode")
def upload_titleepisode(file: UploadFile = File(...)):
    try:
        db_connection = get_database_connection()
        cursor = db_connection.cursor()

        # Ανοίγουμε το αρχείο και διαβάζουμε τα περιεχόμενά του
        contents = file.file.read().decode("utf-8")

        for line in contents.split("\n"):
            # Χωρίζουμε τη γραμμή σε πεδία
            fields = line.split("\t")

            # Εάν υπάρχουν αρκετά πεδία, εκτελούμε την απαραίτητη λογική
            if len(fields) >= 4:
                title_id1 = fields[1]  # Το πεδίο Title_ID1
                title_id2 = fields[0]  # Το πεδίο Title_ID2
                season_number = fields[2]  # Το πεδίο Season
                episode_number = fields[3]  # Το πεδίο Episode_Num

                # Ελέγχουμε αν υπάρχει το parentTconst στον πίνακα Title
                cursor.execute("SELECT * FROM `Title` WHERE `Title_ID` = %s", (title_id1,))
                parent_series = cursor.fetchone()

                if not parent_series:
                    raise HTTPException(status_code=404, detail="Parent series doesn't exist in the database")

                # Εισάγουμε το επεισόδιο στον πίνακα Is_Episode_Of
		# μηπως πρεπει να το εισαγουμε και στον πινακα title;;;
                cursor.execute("""
                    INSERT INTO `Is_Episode_Of` (`Title_ID1`, `Title_ID2`, `Season`, `Episode_Num`)
                    VALUES (%s, %s, %s, %s)
                """, (title_id1, title_id2, season_number, episode_number))

        # Κλείνουμε τον κέρσορα και κάνουμε commit τις αλλαγές
        cursor.close()
        db_connection.commit()

        # Κλείνουμε τη σύνδεση
        db_connection.close()

        return {"message": "Data uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

#admin endpoint 7
async def insert_into_participates_in(values):
    query= "INSERT INTO `Participates_In` (Title_FK, Name_FK, Ordering, Job_Category, `Character`) VALUES (%s, %s, %s, %s, %s)"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, values)
        await connection.commit()
        
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
    
@router.post("/admin/upload/titleprincipals")
async def upload_title_principals(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
                title_fk = await fetch_title_primary_key(row['tconst'])
                name_fk = await fetch_person_primary_key(row['nconst'])
                ordering = row['ordering']
                job_category = row['category'] #+ (',' + row['job'] if row['job'] != '' and row['job'] != row['category'] else '')
                character = row['characters']

                if title_fk is not None and name_fk is not None:
                    await insert_into_participates_in((title_fk, name_fk, ordering, job_category, character))
                else:
                    print("An error occurred")

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#admin endpoint 8
# Function to update data in the Title table
async def update_title_ratings(title_id, average_rating, num_votes):
    query = "UPDATE `Title` SET `Average_Rating` = %s, `Votes` = %s WHERE `Title_ID` = %s"
    async with await get_database_connection() as connection, connection.cursor() as cursor:
        await cursor.execute(query, (average_rating, num_votes, title_id))
        await connection.commit()

# Endpoint for uploading title ratings
@router.post("/admin/upload/titleratings")
async def upload_title_ratings(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Iterate over DataFrame rows and update data in the Title table
        for _, row in df.iterrows():
            title_id = row['tconst']
            average_rating = row['averageRating']
            num_votes = row['numVotes']

            # Update the Title table
            await update_title_ratings(title_id, average_rating, num_votes)

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
