from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from api.models import TitleObject, NameObject, TitleEpisode
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
