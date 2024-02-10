from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Response, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, JSONResponse
from typing import List, Optional
from ..models import TitleObject, NameObject, AkaTitle, PrincipalsObject, RatingObject, GenreTitle, NameTitleObject
from ..database import get_database_connection, check_connection, create_backup, restore, pick_backup
from ..utils.admin_helpers import insert_into_name, insert_into_profession, insert_into_profession_person, fetch_person_primary_key, check_existing_participation, update_title_ratings, insert_into_episode, insert_into_title, fetch_title_primary_key, insert_into_participates_in
import aiomysql
from typing import Optional
import pandas as pd
import csv
import os
from io import StringIO

router = APIRouter()
BASE_URL = "/ntuaflix_api"
templates = Jinja2Templates(directory=os.path.normpath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir), "front-end", "templates")))

# Index page
@router.get("/html", response_class=HTMLResponse)
async def browse_titles_html(request: Request):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT `Title_ID`, `Original_Title`, `Average_Rating`, `IMAGE` FROM `Title`;")
                titles = await cursor.fetchall()
                if not titles:
                    raise HTTPException(status_code=204, detail="No titles found")

                return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browse a specific Title (json, csv format)
@router.get("/title/{titleID}", response_model=TitleObject)
async def get_title_details(titleID: str, format_type: str = "json"):
    if format_type not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:

                await cursor.execute("SELECT * FROM `Title` WHERE `Title_ID` = %s;", (titleID,))
                title_data = await cursor.fetchone()
                if not title_data:
                    raise HTTPException(status_code=204, detail="Data not found")
                
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

                await cursor.execute("""SELECT DISTINCT p.`Name_ID` as `nameID`, p.`Name` as `name`, pi.`Job_Category` as `category`
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
                    rating=RatingObject(avRating=str(title_data["Average_Rating"]), nVotes=str(title_data["Votes"]))
                )

                if format_type == "json":
                    return title_object
                elif format_type == "csv":
                    title_data = [{
                            'tconst': title_object.titleID,
                            'Type': title_object.type,
                            'Original Title': title_object.originalTitle,
                            'Title Poster': title_object.titlePoster,
                            'Start Year': title_object.startYear,
                            'End Year': title_object.endYear,
                            'Genres': ", ".join(['' if g.genreTitle is None else str(g.genreTitle) for g in title_object.genres]), # Cannot perform join operation if object is None Type
                            'Title Akas': ", ".join([f"{'' if a.akaTitle is None else str(a.akaTitle)} ({'' if a.regionAbbrev is None else str(a.regionAbbrev)})" for a in title_object.titleAkas]),
                            'Principals': ", ".join([f"{'' if p.name is None else str(p.name)} ({'' if p.nameID is None else str(p.name)}) ({'' if p.category is None else str(p.category)})" for p in title_object.principals]),
                            'AvgRating': title_object.rating.avRating,
                            'nVotes': title_object.rating.nVotes
                        }]

                    df = pd.DataFrame(title_data)
                    columns_order = ['tconst', 'Type', 'Original Title', 'Title Poster', 'Start Year', 'End Year', 'Genres', 'Title Akas', 'Principals', 'AvgRating', 'nVotes']
                    df = df[columns_order]

                    output = StringIO()
                    df.to_csv(output, index=False)
                    output.seek(0)

                    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=search_results.csv"})

                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
            
    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Browse a certain title (html)
@router.get("/title_html/{title_id}", response_class=HTMLResponse)
async def title_details_html(request: Request, title_id: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `ID`, `Original_Title`, `Average_Rating`, `IMAGE`, `Start_Year`, `End_Year`, `Type`, `Votes` 
                                        FROM `Title`
                                        WHERE `Title_ID` = %s;""", (title_id))
                title = await cursor.fetchone()
                if not title:
                    raise HTTPException(status_code=204, detail="No titles found")
                ID = title["ID"]
                
                await cursor.execute("""SELECT G.`Genre` as `genreTitle`
                                        FROM `Title` T
                                        INNER JOIN `Title_Genre` tg ON T.`ID` = tg.`Title_FK`
                                        INNER JOIN `Genre` G ON tg.`Genre_FK` = G.`ID`
                                        WHERE T.`ID` = %s;""", (ID,))
            
                genres = await cursor.fetchall()
                print(genres)
                if not genres:
                    genre_titles = []
                else:
                    genre_titles = [genre['genreTitle'] for genre in genres]

             
                await cursor.execute("""SELECT alt.`Title_AKA` as akaTitle, alt.`Region` as regionAbbrev
                                        FROM `Title` T
                                        INNER JOIN `Alt_Title` alt ON T.`ID` = alt.`Title_FK`
                                        WHERE T .`ID` = %s;""", (ID,))
          
                akas_data = await cursor.fetchall()
                
                akas = []
                for entry in akas_data: 
                    aka_title = entry['akaTitle']
                    region = entry['regionAbbrev']

                    if region: 
                        aka = f"{aka_title} ({region})"
                    else: 
                        aka = f"{aka_title}"
                    akas.append(aka)
                akas_formatted = ", ".join(akas)

                
                await cursor.execute("""SELECT DISTINCT p.`Name_ID` as `nameID`, p.`Name` as `name`, pi.`Job_Category` as `category`, p.`Image`, pi.`Character` as `character`
                                        FROM `Person` p
                                        INNER JOIN `Participates_In` pi ON p.`ID` = pi.`Name_FK`
                                        WHERE p.`ID` IN (
                                            SELECT pi2.`Name_FK`
                                            FROM `Participates_In` pi2
                                            WHERE pi2.`Title_FK` = %s);""", (ID,))
                
                principals_data = await cursor.fetchall()
                if not principals_data:
                    raise HTTPException(status_code=404, detail="No principals found")
                directors = []
                writers = []
                actors = []
                actors_image = []
                actor_nameID = []
                characters = []
                principals = []
                principals_image = []
                principals_nameID = []
                credits = []
                for person in principals_data:
                    if "director" in person['category']:
                        directors.append(person['name'])
                    if "writer" in person['category']: 
                        writers.append(person['name'])
                    if "actor" in person['category']:
                        actors.append(person['name'])
                        actors_image.append(person['Image'])
                        actor_nameID.append(person['nameID'])
                        character_unformat = person['character']
                        if character_unformat is not None: 
                            character = character_unformat[2:-2]
                        else: 
                            character = character_unformat
                        characters.append(character)
                    if "actress" in person['category']:
                        actors.append(person['name'])
                        actors_image.append(person['Image'])
                        actor_nameID.append(person['nameID'])
                        character_unformat = person['character']
                        character = character_unformat[2:-2]
                        characters.append(character)
                    if "actor" not in person['category'] and "actress" not in person['category']:
                        principals.append(person['name'])
                        credits.append(person['category'])
                        principals_nameID.append(person['nameID'])
                        principals_image.append(person['Image'])

                return templates.TemplateResponse("movie.html", {"request": request, "title": title, "genres":genre_titles, "akas": akas_formatted, "directors": directors, "writers": writers, 
                                                                    "actors": actors, "actors_image":actors_image, "actor_nameID": actor_nameID, "characters": characters,
                                                                    "principals": principals, "credits": credits, "principals_nameID":principals_nameID, "principals_image":principals_image})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browse a certain person
@router.get("/name/{nameID}", response_model=NameObject)
async def get_name_details(nameID: str, format_type: str = "json"):
    if format_type not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

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

                    nt_object = NameTitleObject(
                        titleID = title_data["Title_ID"],
                        category = [c["Job_Category"] for c in categories_data]
                    )

                    name_title_objects.append(nt_object)
                    
                await cursor.execute("""SELECT p.`Profession`
                                        FROM `Profession` p
                                        INNER JOIN `Profession_Person` pp ON p.`ID`= pp.`Profession_FK`
                                        INNER JOIN `Person` pr ON pr.`ID`= pp.`Name_FK`
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
                
                if format_type == "json":
                    return name_object
                elif format_type == "csv":
                    name_data = [{
                        'nconst': name_object.nameID,
                        'Name': name_object.name,
                        'Name Poster': name_object.namePoster,
                        'Birth Year': name_object.birthYr,
                        'Death Year': name_object.deathYr,
                        'Profession': ", ".join([p["Profession"] for p in primary_professions]),
                        'Name Titles': ", ".join([f"{nt.titleID} ({', '.join(nt.category)})" for nt in name_object.nameTitles])
                    }]

                    df = pd.DataFrame(name_data)
                    columns_order = ['nconst', 'Name', 'Name Poster', 'Birth Year', 'Death Year', 'Profession', 'Name Titles']
                    df = df[columns_order]

                    output = StringIO()
                    df.to_csv(output, index=False)
                    output.seek(0)

                    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=search_results.csv"})
            
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for viewing person details in HTML 
@router.get("/person_html/{name_id}", response_class=HTMLResponse)
async def person_details_html(request: Request, name_id: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute("""SELECT `ID`, `Name`, `Image`, `Birth_Year`, `Death_Year` 
                                        FROM `Person`
                                        WHERE `Name_ID` = %s;""", (name_id))
                except Exception as e: 
                    print(f"Error: {e}")
                person = await cursor.fetchone()
                if not person: 
                    raise HTTPException(status_code=404, detail="No person found")
                
                person_ID = person["ID"]
                try:
                    await cursor.execute("""SELECT T.`Title_ID`, T.`Original_Title`, T.`IMAGE`, T.`Average_Rating`, pi.`Job_Category`
                                        FROM `person` P
                                        INNER JOIN `participates_in` pi ON P.`ID` = pi.`Name_FK`
                                        INNER JOIN `title` T ON pi.`Title_FK` = T.`ID`
                                        WHERE P.`ID` = %s;""", (person_ID,))
                except Exception as e: 
                    print(f"Error: {e}")
                titles = await cursor.fetchall()
                if not titles: 
                    raise HTTPException(status_code=404, detail="No movies found")

                try:
                    await cursor.execute("""SELECT pr.`Profession`
                                        FROM `person` P 
                                        INNER JOIN `profession_person` pp ON P.`ID` = pp.`Name_FK`
                                        INNER JOIN `profession` pr ON pp.`Profession_FK` = pr.`ID`
                                        WHERE P.`ID` = %s;""", (person_ID,))
                except Exception as e: 
                    print(f"Error: {e}")
                prof = await cursor.fetchall()
                if not prof: 
                    raise HTTPException(status_code=404, detail="No professions found")
                profession = []
                for item in prof: 
                    dummy = item['Profession'].capitalize()
                    profession.append(dummy)

                return templates.TemplateResponse("person.html", {"request": request, "person": person, "titles": titles, "profession": profession})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       
# Title search query
@router.get("/searchtitle", response_model=List[TitleObject])
async def search_titles(query: str, format_type: str = "json"):
    if format_type not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM `Title` WHERE `Original_Title` LIKE %s",
                    (f'%{query}%',)
                )
                titles = await cursor.fetchall()
                if not titles:
                    raise HTTPException(status_code=204, detail="No data found")

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
                        rating=RatingObject(avRating=str(title_data["Average_Rating"]), nVotes=str(title_data["Votes"]))
                    )

                    print(title_data["Average_Rating"], title_data["Votes"])

                    full_titles.append(title_object)

            if format_type == "csv":
                titles_data = []
                for title in full_titles:
                    title_dict = {
                        'tconst': title.titleID,
                        'Type': title.type,
                        'Original Title': title.originalTitle,
                        'Title Poster': title.titlePoster,
                        'Start Year': title.startYear,
                        'End Year': title.endYear,
                        'Genres': ", ".join(['' if g.genreTitle is None else str(g.genreTitle) for g in title.genres]),
                        'Title Akas': ", ".join([f"{'' if a.akaTitle is None else str(a.akaTitle)} ({'' if a.regionAbbrev is None else str(a.regionAbbrev)})" for a in title.titleAkas]),
                        'Principals': ", ".join([f"{'' if p.name is None else str(p.name)} ({'' if p.nameID is None else str(p.name)}) ({'' if p.category is None else str(p.category)})" for p in title.principals]),
                        'AvgRating': title.rating.avRating,
                        'nVotes': title.rating.nVotes
                    }
                    titles_data.append(title_dict)

                df = pd.DataFrame(titles_data)
                columns_order = ['tconst', 'Type', 'Original Title', 'Title Poster', 'Start Year', 'End Year', 'Genres', 'Title Akas', 'Principals', 'AvgRating', 'nVotes']
                df = df[columns_order]
                    

                output = StringIO()
                df.to_csv(output, index=False)
                output.seek(0)

                return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=search_results.csv"})
            
            elif format_type == "json":
                return full_titles
            
            else:
                raise HTTPException(status_code=400, detail="Unsupported format specifier")
            
    except HTTPException as http_ex:
        raise http_ex        
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Title Search Bar Endpoint    
@router.get("/search_titles", response_class=HTMLResponse)
async def search_movies_html(request: Request, query: str = Query(...)):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                
                query = f"%{query}%"
                await cursor.execute("SELECT `Title_ID`, `Original_Title`, `Average_Rating`, `IMAGE` FROM `Title` WHERE `Original_Title` LIKE %s;", (query,))
                titles = await cursor.fetchall()
                if not titles:
                    return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})

                return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Genre search query
@router.get("/bygenre", response_model=List[TitleObject])
async def search_genre(qgenre: str, minrating: Optional[str] = 0, yrFrom: Optional[str] = None, yrTo: Optional[str] = None, format_type: str = "json"):
    # Validate parameters
    if format_type not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

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
                    raise HTTPException(status_code=204, detail="No data found")
                
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
                        rating=RatingObject(avRating=str(title["Average_Rating"]), nVotes=str(title["Votes"]))
                    )

                    title_objects.append(title_object)
                
                if format_type == "csv":
                    titles_data = []
                    for title in title_objects:
                        title_dict = {
                            'tconst': title.titleID,
                            'Type': title.type,
                            'Original Title': title.originalTitle,
                            'Title Poster': title.titlePoster,
                            'Start Year': title.startYear,
                            'End Year': title.endYear,
                            'Genres': ", ".join(['' if g.genreTitle is None else str(g.genreTitle) for g in title.genres]),
                            'Title Akas': ", ".join([f"{'' if a.akaTitle is None else str(a.akaTitle)} ({'' if a.regionAbbrev is None else str(a.regionAbbrev)})" for a in title.titleAkas]),
                            'Principals': ", ".join([f"{'' if p.name is None else str(p.name)} ({'' if p.nameID is None else str(p.name)}) ({'' if p.category is None else str(p.category)})" for p in title.principals]),
                            'AvgRating': title.rating.avRating,
                            'nVotes': title.rating.nVotes
                        }
                        titles_data.append(title_dict)

                    df = pd.DataFrame(titles_data)
                    columns_order = ['tconst', 'Type', 'Original Title', 'Title Poster', 'Start Year', 'End Year', 'Genres', 'Title Akas', 'Principals', 'AvgRating', 'nVotes']
                    df = df[columns_order]
                        

                    output = StringIO()
                    df.to_csv(output, index=False)
                    output.seek(0)

                    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=search_results.csv"})
                
                elif format_type == "json":
                    return title_objects
                
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Genre, Rating, Production Year Endpoint 
@router.get("/search_genre_rating_pyear", response_class=HTMLResponse)
async def search_movies_html(request: Request, query: str = Query(...)):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                # Split the query string by commas
                query_parts = query.split(',')
                titles = None  # Initialize with None
                for part in query_parts:
                    part = part.strip() 
                    # Check if the part represents a decimal without a fractional part
                    if part.isdigit() and '.' not in part:
                        part = int(part)
                        await cursor.execute("""SELECT t.`Title_ID`, t.`Original_Title`, t.`Average_Rating`, t.`IMAGE` 
                                             FROM `Title` t
                                             WHERE `Start_Year` = %s;""", (part,))
                    # Check if the part represents a decimal
                    elif part.replace('.', '').isdigit():
                        part = float(part)
                        await cursor.execute("""SELECT t.`Title_ID`, t.`Original_Title`, t.`Average_Rating`, t.`IMAGE` 
                                             FROM `Title` t
                                             WHERE `Average_Rating` = %s;""", (part,))
                    # Otherwise, assume it's a string
                    else:
                        part = f"%{part}%"
                        await cursor.execute("""SELECT t.`Title_ID`, t.`Original_Title`, t.`Average_Rating`, t.`IMAGE` 
                                             FROM `Title` t
                                             INNER JOIN Title_Genre tg ON t.`ID`=tg.`Title_FK`
                                             INNER JOIN Genre g ON tg.`Genre_FK`=g.`ID`
                                             WHERE g.`Genre` LIKE %s;""", (part,))
                    
                    part_titles = await cursor.fetchall()
                    if titles is None:
                        titles = part_titles  # Initialize titles with the first query results
                    else:
                        # Filter titles to keep only the movies present in both titles and part_titles
                        titles = [movie for movie in titles if movie in part_titles]

                if not titles:
                    return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})

                return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search by name
@router.get("/searchname", response_model=List[NameObject])
async def search_name(query: str, format_type: str = "json"):
    if format_type not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `Name_ID`, `Name`, `IMAGE`, `Birth_Year` as birthYr, `Death_Year` as deathYr, `ID`
                                        FROM `Person` 
                                        WHERE `Name` LIKE %s""", (f'%{query}%',))
                names = await cursor.fetchall()
                if not names:
                    raise HTTPException(status_code=204, detail="No people found")

                result = []
                for name in names:
                    await cursor.execute("""SELECT T.`Title_ID`, T.`ID`
                                            FROM `Person` p
                                            INNER JOIN `Participates_In` pi ON p.`ID`= pi.`Name_FK`
                                            INNER JOIN `Title` T ON pi.`Title_FK`= T.`ID`
                                            WHERE p.`ID` = %s""", (name["ID"],))
                    name_titles_data = await cursor.fetchall()
                    print(name_titles_data)

                    name_title_objects = []

                    for title_data in name_titles_data:
                        await cursor.execute("""SELECT DISTINCT pi.`Job_Category`
                                                FROM `Title` T
                                                INNER JOIN `Participates_In` pi ON T.`ID`= pi.`Title_FK`
                                                WHERE pi.`Name_FK` = %s AND pi.`Title_FK` = %s""", (name["ID"], title_data["ID"]))
                        categories_data = await cursor.fetchall()

                        nt_object = NameTitleObject(
                            titleID = title_data["Title_ID"],
                            category = [c["Job_Category"] for c in categories_data]
                        )

                        name_title_objects.append(nt_object)
                    
                    print("sth")
                    await cursor.execute("""SELECT p.`Profession`
                                            FROM `Profession` p
                                            INNER JOIN `Profession_Person` pp ON p.`ID`= pp.`Profession_FK`
                                            INNER JOIN `Person` pr ON pr.`ID`= pp.`Name_FK`
                                            WHERE pr.`ID` = %s""", (name["ID"]))
                    primary_profession = await cursor.fetchall()
                    
                    name_object = NameObject(
                        nameID=name["Name_ID"],
                        name=name["Name"],
                        namePoster=name["IMAGE"],
                        birthYr=str(name["birthYr"]),
                        deathYr=str(name["deathYr"]) if name["deathYr"] else None,
                        profession=[p["Profession"] for p in primary_profession],
                        nameTitles=name_title_objects
                    )
                    
                    result.append(name_object)
                
            if format_type == "json":
                return result
            elif format_type == "csv":
                name_data = [{
                    'nconst': name_object.nameID,
                    'Name': name_object.name,
                    'Name Poster': name_object.namePoster,
                    'Birth Year': name_object.birthYr,
                    'Death Year': name_object.deathYr,
                    'Profession': ", ".join([p["Profession"] for p in primary_profession]),
                    'Name Titles': ", ".join([f"{nt.titleID} ({', '.join(nt.category)})" for nt in name_object.nameTitles])
                } for name_object in result]

                df = pd.DataFrame(name_data)
                columns_order = ['nconst', 'Name', 'Name Poster', 'Birth Year', 'Death Year', 'Profession', 'Name Titles']
                df = df[columns_order]

                output = StringIO()
                df.to_csv(output, index=False)
                output.seek(0)

                return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=search_results.csv"})
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#First, Last Name Search Bar Endpoint
@router.get("/search_name", response_class=HTMLResponse)
async def search_name(request: Request, query: str = Query(...)):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                # Split the query string by commas
                query_parts = query.split(',')
                names = None  
                for part in query_parts:
                    part = part.strip() 
                    await cursor.execute("""SELECT `Name`, `Image`, `Name_ID`
                                             FROM `Person` 
                                             WHERE `Name` LIKE %s;""", (f"%{part}%",))
                    
                    part_names = await cursor.fetchall()
                    if names is None:
                        names = part_names  
                    else:
                        # Filter names to keep only the people present in both names and part_names
                        names = [person for person in names if person in part_names]

                if not names:
                    return templates.TemplateResponse("home_page.html", {"request": request, "name_list": names})

                return templates.TemplateResponse("home_page_people.html", {"request": request, "name_list": names})
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for HTML page concerning uploads of TSV files 
@router.get("/uploads_html", response_class=HTMLResponse)
async def uploads_html(request: Request): 
    try:
        return templates.TemplateResponse("uploads.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Admin healthcheck
@router.get("/admin/healthcheck")
async def admin_health_check():
    try:
        return await check_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin create backup
@router.post("/admin/backup")
async def initiate_backup():
    try:
        return await create_backup()    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin restore database   
@router.post("/admin/resetall")
async def initiate_restore():
    try:
        return await restore()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# endpoint 2
@router.post("/admin/upload/titlebasics")
async def upload_title_basics(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Iterate over DataFrame rows and insert data into the database
        async with await get_database_connection() as connection, connection.cursor() as cursor:
            for _, row in df.iterrows():
                tconst = row['tconst']
                title_type = row['titleType']
                original_title = row['originalTitle']
                is_adult = row['isAdult']
                start_year = row['startYear'] if row['startYear'] != '\\N' else None
                end_year = row['endYear'] if row['endYear'] != '\\N' else None
                runtime_minutes = row['runtimeMinutes'] if row['runtimeMinutes'] != '\\N' else None
                genres = row['genres'] if row['genres'] != '\\N' else None
                image_url = row['img_url_asset'] if row['img_url_asset'] != '\\N' else None

                # Insert data into the 'Title' table
                query_title = """
                    INSERT INTO `Title` (Title_ID, Type, Original_Title, IMAGE, Start_Year, End_Year, Runtime, isAdult)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                await cursor.execute(query_title, (tconst, title_type, original_title, image_url,
                                                   start_year, end_year, runtime_minutes, is_adult))

                if genres is not None:  # Ensure genres column is not null
                    genres_list = genres.split(',')
                    for genre in genres_list:
                        # Check if the genre exists in the 'Genre' table
                        query_genre_check = "SELECT `ID` FROM `Genre` WHERE `Genre` = %s LIMIT 1"
                        await cursor.execute(query_genre_check, (genre,))
                        result_genre = await cursor.fetchone()

                        if not result_genre:
                            # If the genre doesn't exist, insert it into the 'Genre' table
                            query_insert_genre = "INSERT INTO `Genre` (Genre) VALUES (%s)"
                            await cursor.execute(query_insert_genre, (genre,))
                            await connection.commit()
                            # Fetch the primary key of the newly inserted genre
                            query_fetch_genre_pk = "SELECT `ID` FROM `Genre` WHERE `Genre` = %s LIMIT 1"
                            await cursor.execute(query_fetch_genre_pk, (genre,))
                            genre_fk = await cursor.fetchone()
                            if genre_fk:
                                genre_fk = genre_fk[0]
                        else:
                            genre_fk = result_genre[0]

                        if genre_fk:
                            # Fetch the primary key of the title
                            query_fetch_title_pk = "SELECT `ID` FROM `Title` WHERE `Title_ID` = %s LIMIT 1"
                            await cursor.execute(query_fetch_title_pk, (tconst,))
                            title_fk = await cursor.fetchone()
                            if title_fk:
                                title_fk = title_fk[0]
                                # Insert data into the 'Title_Genre' table
                                query_title_genre = "INSERT INTO `Title_Genre` (Title_FK, Genre_FK) VALUES (%s, %s)"
                                await cursor.execute(query_title_genre, (title_fk, genre_fk))
                                await connection.commit()

            return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# endpoint 3
@router.post("/admin/upload/titleakas")
async def upload_title_akas(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Collect errors to include in the final response
        errors = []

        # Iterate over DataFrame rows and insert data into the database
        async with await get_database_connection() as connection, connection.cursor() as cursor:
            for _, row in df.iterrows():
                title_id = row['titleId']
                ordering = row['ordering']
                title_aka = row['title']
                region = row['region']

                # Replace '\N' values with None
                if title_id == '\\N':
                    title_id = None
                if ordering == '\\N':
                    ordering = None
                if title_aka == '\\N':
                    title_aka = None
                if region == '\\N':
                    region = None

                try:
                    # Fetch the primary key of the title
                    query_fetch_title_pk = "SELECT `ID` FROM `Title` WHERE `Title_ID` = %s LIMIT 1"
                    await cursor.execute(query_fetch_title_pk, (title_id,))
                    title_fk = await cursor.fetchone()
                    if title_fk:
                        title_fk = title_fk[0]
                    else:
                        raise ValueError(f"Title with Title_ID {title_id} doesn't exist in the database.")

                    # Insert data into the 'Alt_Title' table
                    query_insert_alt_title = "INSERT INTO `Alt_Title` (Title_FK, Ordering, Title_AKA, Region) VALUES (%s, %s, %s, %s)"
                    await cursor.execute(query_insert_alt_title, (title_fk, ordering, title_aka, region))
                    await connection.commit()
                    
                except Exception as e:
                    errors.append(str(e))
                    continue

        if errors:
            # If there are errors, raise an HTTPException with the collected error messages
            error_message = "\n".join(errors)
            raise HTTPException(status_code=500, detail=error_message)

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Admin Endpoint 4
@router.post("/admin/upload/namebasics")
async def upload_name_basics(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
            name_id = row['nconst']
            primaryname = row['primaryName']
            image_url = row['img_url_asset']
            birthyear = row['birthYear']
            deathyear = row['deathYear']

            # Insert data into the 'Name' table
            await insert_into_name((name_id, primaryname, image_url, birthyear, deathyear))

            # Handle primaryProfession column
            professions_value = row['primaryProfession']
            if isinstance(professions_value, str):
                professions = professions_value.split(',')
                for profession in professions:
                    # Insert data into the 'Profession' table and fetch its ID
                    profession_fk = await insert_into_profession((profession,))

                    # Fetch Name_FK (id) of the name just added to the 'Name' table
                    name_fk = await fetch_person_primary_key(name_id)

                    # Check if the profession_fk is not None before inserting into Profession_Person
                    if profession_fk is not None and name_fk is not None:
                        # Insert data into the 'Profession_Person' table
                        await insert_into_profession_person((profession_fk, name_fk))

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Admin Endpoint 5

@router.post("/admin/upload/titlecrew")
async def upload_title_crew(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Collect errors to include in the final response
        errors = []

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
            title_id = row['tconst']
            directors = row['directors'].split(',') if row['directors'] and (row['directors'] != '\\N' or row['directors'] != '/N') else []
            writers = row['writers'].split(',') if row['writers'] and (row['writers'] != '\\N' or row["writers"] != '/N') else []

            # Process directors
            for director_id in directors:
                try:
                    # Check if the director's name_id exists in the 'Name' table
                    director_name_fk = await fetch_person_primary_key(director_id)
                    if director_name_fk is None:
                        raise ValueError(f"Person with Name_ID {director_id} doesn't exist in the database.")

                    # Check if the title_id exists in the 'Title' table
                    title_fk = await fetch_title_primary_key(title_id)
                    if title_fk is None:
                        raise ValueError(f"Title with Title_ID {title_id} doesn't exist in the database.")

                    # Check if the entry already exists in the 'Participates_In' table
                    existing_director_entry = await check_existing_participation(director_name_fk, title_fk, 'director')
                    if existing_director_entry:
                        print("Entry already exists, skip insertion")
                        # Entry already exists, skip insertion
                        continue

                    # Insert data into the 'Participates_In' table for directors
                    await insert_into_participates_in((title_fk, director_name_fk, None, 'director', None))
                except Exception as e:
                    errors.append(str(e))
                    continue

            # Process writers
            for writer_id in writers:
                try:
                    # Check if the writer's name_id exists in the 'Name' table
                    writer_name_fk = await fetch_person_primary_key(writer_id)
                    if writer_name_fk is None:
                        raise ValueError(f"Person with Name_ID {writer_id} doesn't exist in the database.")

                    # Check if the title_id exists in the 'Title' table
                    title_fk = await fetch_title_primary_key(title_id)
                    if title_fk is None:
                        raise ValueError(f"Title with Title_ID {title_id} doesn't exist in the database.")

                    # Check if the entry already exists in the 'Participates_In' table
                    existing_writer_entry = await check_existing_participation(writer_name_fk, title_fk, 'writer')
                    if existing_writer_entry:
                        print("Entry already exists, skip insertion")
                        # Entry already exists, skip insertion
                        continue

                    # Insert data into the 'Participates_In' table for writers
                    await insert_into_participates_in((title_fk, writer_name_fk, None, 'writer', None))
                except Exception as e:
                    errors.append(str(e))
                    continue

        if errors:
            # If there are errors, raise an HTTPException with the collected error messages
            error_message = "\n".join(errors)
            print(error_message)
            raise HTTPException(status_code=500, detail=error_message)

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Admin Endpoint 6
@router.post("/admin/upload/titleepisode")
async def upload_title_episode(file: UploadFile = File(...)):
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Collect errors to include in the final response
        errors = []

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
            title_id = row['tconst']
            parent_title_id = row['parentTconst']
            season_number = row['seasonNumber']
            episode_number = row['episodeNumber']

            try:
                # Add episode to the Title table
                await insert_into_title((title_id, '','tvEpisode'))

                # Add episode to the Episode table
                title_fk = await fetch_title_primary_key(title_id)

                if title_fk is None:
                    raise ValueError(f"Title with Title_ID {title_id} doesn't exist in the database.")

                # Insert data into the 'Episode' table
                await insert_into_episode((title_fk, parent_title_id, season_number, episode_number))
            except Exception as e:
                errors.append(str(e))
                continue

        if errors:
            # If there are errors, raise an HTTPException with the collected error messages
            error_message = "\n".join(errors)
            raise HTTPException(status_code=500, detail=error_message)

        return {"message": "File uploaded and data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/upload/titleprincipals")
async def upload_title_principals(file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is of the correct format
        if not file.filename.endswith(".tsv"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be in TSV format")
        
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)
        
        expected_columns = ['tconst', 'nconst', 'ordering', 'category', 'characters']

        # Check if the DataFrame contains all the expected columns
        if not all(column in df.columns for column in expected_columns):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must contain columns: tconst, nconst, ordering, category, characters")

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
                title_fk = await fetch_title_primary_key(row['tconst'])
                name_fk = await fetch_person_primary_key(row['nconst'])
                ordering = row['ordering']
                job_category = row['category'] 
                character = row['characters']

                if title_fk is not None and name_fk is not None:
                    values = (title_fk, name_fk, ordering, job_category, character)
                    await insert_into_participates_in((title_fk, name_fk, ordering, job_category, character))
                else:
                    print("An error occurred")

        # Check if any data was inserted
        if len(df) > 0:
            return {"message": "File uploaded and data stored successfully"}, status.HTTP_200_OK
        else:
            return {"message": "No data provided in the file"}, status.HTTP_204_NO_CONTENT

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")    

#Admin Endpoint 8
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


# Endpoint for uploading title ratings
@router.post("/admin/upload/titleratings")
async def upload_title_ratings(file: UploadFile = File(...)):
    try:
        
        # Check if the uploaded file is of the correct format
        if not file.filename.endswith(".tsv"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be in TSV format")
        
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file.file, sep='\t', low_memory=False)
        
        expected_columns = ['tconst', 'averageRating', 'numVotes']

        # Check if the DataFrame contains all the expected columns
        if not all(column in df.columns for column in expected_columns):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must contain columns: tconst, nconst, ordering, category, characters")

        # Iterate over DataFrame rows and update data in the Title table
        for _, row in df.iterrows():
            title_id = row['tconst']
            average_rating = row['averageRating']
            num_votes = row['numVotes']
            
            # Check and replace null values with None
            if average_rating == '/N' or average_rating == '\\N':
                average_rating = None  
            if num_votes == '/N' or num_votes == '\\N':
                num_votes = None

            # Update the Title table
            await update_title_ratings(title_id, average_rating, num_votes)

        if len(df) > 0:
            return {"message": "File uploaded and data stored successfully"}, status.HTTP_200_OK
        else:
            return {"message": "No data provided in the file"}, status.HTTP_204_NO_CONTENT

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
