from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import List
from ..models import TitleObject, NameObject, AkaTitle, PrincipalsObject, RatingObject, GenreTitle, gqueryObject
from ..database import get_database_connection, check_connection, create_backup, restore, pick_backup
from ..utils.security import get_current_admin_user
import aiomysql

router = APIRouter()

@router.get("/test")
async def test():
    async with await get_database_connection() as db_connection:
        async with db_connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM `Profession`;")
            profession = await cursor.fetchall()

        if profession:
            return profession
    
    return {'this': 'that'}

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
                
                await cursor.execute("""SELECT alt.`Title_AKA` as `akatitle`, alt.`Region` as `regionAbbrev`
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
                    primary_key = titles["ID"]

                    await cursor.execute("""SELECT G.`Genre` as `genreTitle`
                                            FROM `Title` T
                                            INNER JOIN `Title_Genre` tg ON T.`ID` = tg.`Title_FK`
                                            INNER JOIN `Genre` G ON tg.`Genre_FK` = G.`ID`
                                            WHERE T.`ID` = %s;""", (primary_key,))
                    genres_data = await cursor.fetchall()

                    print(genres_data)
                
                    await cursor.execute("""SELECT alt.`Title_AKA` as `akatitle`, alt.`Region` as `regionAbbrev`
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
async def search_genre(query: gqueryObject):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT T.`Title_ID`, T.`Original_Title` 
                                    FROM `Title` T 
                                    INNER JOIN `Title_Genre` TG ON T.`Title_ID` = TG.`Title_ID` 
                                    INNER JOIN `Genre` G ON TG.`Genre_ID` = G.`Genre_ID`
                                    WHERE G.`Genre` LIKE %s""", (f'%{query.qgenre}%',))
                titles = await cursor.fetchall()

            if titles:
                return titles
            else:
                raise HTTPException(status_code=404, detail="No titles found")
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
                
                await cursor.execute("""SELECT DISTINCT `Job_Category`
                                        FROM `Participates_In`
                                        WHERE `Name_FK` = %s""", (names['Name_ID'],))
                professions_data = await cursor.fetchall()
                professions = [p['Job_Category'] for p in professions_data]

                await cursor.execute("""SELECT T.`Title_ID`
                                        FROM `Person` p
                                        INNER JOIN `Participates_In` pi ON p.`ID`= pi.`Name_FK`
                                        INNER JOIN `Title` t ON pi.`Title_FK`= t.`ID`
                                        WHERE p.`ID` = %s""", (names["ID"],))
                name_titles_data = await cursor.fetchall()
                
                name_object = NameObject(
                    nameID=names["Name_ID"],
                    name=names["Name"],
                    namePoster=names["Image"],
                    birthYr=str(names["birthYr"]),
                    deathYr=str(names["deathYr"]) if names["deathYr"] else None,
                    profession=", ".join(professions)
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
                await cursor.execute("""SELECT `Name_ID`, `Name`, `Image`, `Birth_Year`, `Death_Year`
                                        FROM `Person` 
                                        WHERE `Name` LIKE %s""", (f'%{query}%',))
                names = await cursor.fetchall()
            
        if not names:
            raise HTTPException(status_code=404, detail="No people found")

        result = []
        for name in names:
            await cursor.execute("""SELECT DISTINCT `Job_Category`
                                    FROM `Participates_In`
                                    WHERE `Name_FK` = %s""", (name['Name_ID'],))
            professions_data = await cursor.fetchall()
            professions = [p['Job_Category'] for p in professions_data]

            name_object = NameObject(
                nameID=name["Name_ID"],
                name=name["Name"],
                namePoster=name["Image"],
                birthYr=str(name["Birth_Year"]),
                deathYr=str(name["Death_Year"]) if name["Death_Year"] else None,
                profession=", ".join(professions)
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
@router.post("admin/resetall")
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