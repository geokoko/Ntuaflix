from fastapi import APIRouter, Body, HTTPException, File, UploadFile, Query, Response, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, JSONResponse
from typing import List, Optional
from ..models import TitleObject, NameObject, AkaTitle, PrincipalsObject, RatingObject, GenreTitle, NameTitleObject, tqueryObject, nqueryObject, gqueryObject
from ..database import get_database_connection, create_db_pool, close_db_pool, check_connection, create_backup, restore, pick_backup, reset_database
from ..utils.admin_helpers import insert_into_name, insert_into_profession, insert_into_profession_person, fetch_person_primary_key, check_existing_participation, update_title_ratings, insert_into_episode, insert_into_title, fetch_title_primary_key, insert_into_participates_in, insert_into_participates_in_crew
from ..utils.custom_responses import get_custom_responses
from ..utils.config import Config
import aiomysql
from typing import Optional, Union
import pandas as pd
import csv
import os
from io import StringIO
import aiofiles
import logging

router = APIRouter()
BASE_URL = "/ntuaflix_api"
templates = Jinja2Templates(directory=os.path.normpath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir), "front-end", "templates")))

@router.get("/")
async def read_root(request: Request):
    scheme = request.url.scheme
    print(scheme)
    return {"scheme": scheme}

# Index page
@router.get("/html", response_class=HTMLResponse)
async def browse_titles_html(request: Request):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `Title_ID`, `Original_Title`, `Average_Rating`, `IMAGE` 
                                        FROM `Title`
                                        ORDER BY RAND();""")
                titles = await cursor.fetchall()

                return templates.TemplateResponse("home_page.html", {"request": request, "title_list": titles})
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browse a specific Title (json, csv format)
@router.get("/title/{titleID}", response_model=TitleObject, responses=get_custom_responses())
async def get_title_details(titleID: str, format: str = "json"):
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:

                await cursor.execute("SELECT * FROM `Title` WHERE `Title_ID` = %s;", (titleID,))
                title_data = await cursor.fetchone()
                if not title_data:
                    return Response(status_code=204)
                
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

                if format == "json":
                    return title_object
                elif format == "csv":
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

                    return Response(content=output.getvalue(), media_type="text/plain")

                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
            
    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Browse a certain title (html)
@router.get("/title_html/{title_id}", response_class=HTMLResponse, responses = get_custom_responses())
async def title_details_html(request: Request, title_id: str):
    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `ID`, `Original_Title`, `Average_Rating`, `IMAGE`, `Start_Year`, `End_Year`, `Type`, `Votes` 
                                        FROM `Title`
                                        WHERE `Title_ID` = %s;""", (title_id))
                title = await cursor.fetchone()
                ID = title["ID"]
                print(title)
                
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
                print(akas_data)
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
                print(principals_data)
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
@router.get("/name/{nameID}", response_model=NameObject, responses=get_custom_responses())
async def get_name_details(nameID: str, format: str = "json"):
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `ID`, `Name_ID`, `Name`, `Image`, `Birth_Year` as birthYr, `Death_Year` as deathYr 
                                        FROM `Person` 
                                        WHERE `Name_ID` = %s""", (nameID,))
                names = await cursor.fetchone()
                if not names:
                    return Response(status_code=204)

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
                
                if format == "json":
                    return name_object
                elif format == "csv":
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

                    return Response(content=output.getvalue(), media_type="text/plain")
            
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for viewing person details in HTML 
@router.get("/person_html/{name_id}", response_class=HTMLResponse, responses=get_custom_responses())
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
                
                person_ID = person["ID"]
             
                await cursor.execute("""SELECT T.`Title_ID`, T.`Original_Title`, T.`IMAGE`, T.`Average_Rating`, pi.`Job_Category`
                                        FROM `Person` P
                                        INNER JOIN `Participates_In` pi ON P.`ID` = pi.`Name_FK`
                                        INNER JOIN `Title` T ON pi.`Title_FK` = T.`ID`
                                        WHERE P.`ID` = %s;""", (person_ID,))
             
                titles = await cursor.fetchall()
                

                
                await cursor.execute("""SELECT pr.`Profession`
                                        FROM `Person` P 
                                        INNER JOIN `Profession_Person` pp ON P.`ID` = pp.`Name_FK`
                                        INNER JOIN `Profession` pr ON pp.`Profession_FK` = pr.`ID`
                                        WHERE P.`ID` = %s;""", (person_ID,))
                
                prof = await cursor.fetchall()
                profession = []
                for item in prof: 
                    dummy = item['Profession'].capitalize()
                    profession.append(dummy)

                return templates.TemplateResponse("person.html", {"request": request, "person": person, "titles": titles, "profession": profession})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       
# Title search query
@router.get("/searchtitle", response_model=List[TitleObject], responses=get_custom_responses())
async def search_titles(query: tqueryObject = Body(...), format: str = "json"):
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM `Title` WHERE `Original_Title` LIKE %s",
                    (f'%{query.titlePart}%',)
                )
                titles = await cursor.fetchall()
                if not titles:
                    return Response(status_code=204)

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

            if format == "csv":
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
                        'Principals': ", ".join([f"{'' if p.name is None else str(p.name)} ({'' if p.nameID is None else str(p.nameID)}) ({'' if p.category is None else str(p.category)})" for p in title.principals]),
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

                return Response(content=output.getvalue(), media_type="text/plain")
            
            elif format == "json":
                return full_titles
            
            else:
                raise HTTPException(status_code=400, detail="Unsupported format specifier")
            
    except HTTPException as http_ex:
        raise http_ex        
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Title Search Bar Endpoint    
@router.get("/search_titles", response_class=HTMLResponse, responses=get_custom_responses())
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
async def search_genre(query: gqueryObject = Body(...), format: str = "json"):
    # Validate parameters
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    if not (query.qgenre and query.minrating):
        raise HTTPException(status_code=400, detail="Genre and Minrating query must not be empty")
    
    try:
        query.minrating = float(query.minrating)  # assuming minrating should be a number
    except ValueError:
        raise HTTPException(status_code=400, detail="Minimum rating must be a valid number")

    if query.yrFrom is not None and query.yrTo is None:
        try:
            query.yrFrom = int(query.yrFrom)  # assuming yrFrom should be a valid year (integer)
            if query.yrFrom < 0:
                raise HTTPException(status_code=400, detail="Start year must be a positive integer")
        except ValueError:
            raise HTTPException(status_code=400, detail="Start year must be a valid year")
        
        raise HTTPException(status_code=400, detail="YearFrom and YearTo are optional but mutually mandatory if provided")


    if query.yrTo is not None and query.yrFrom is None:
        try:
            query.yrTo = int(query.yrTo)  # assuming yrTo should be a valid year (integer)
            if query.yrTo < 0:
                raise HTTPException(status_code=400, detail="End year must be a positive integer")
        except ValueError:
            raise HTTPException(status_code=400, detail="End year must be a valid year")
        
        raise HTTPException(status_code=400, detail="YearFrom and YearTo are optional but mutually mandatory if provided")
    

    if query.yrFrom is not None and query.yrTo is not None and query.yrFrom > query.yrTo:
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
                params = [f'%{query.qgenre}%', query.minrating]

                if query.yrFrom is not None and query.yrTo is None:
                    raise HTTPException(status_code=400, detail="YearFrom and YearTo are optional but mutually mandatory if provided")
                if query.yrTo is not None and query.yrFrom is None:
                    raise HTTPException(status_code=400, detail="YearFrom and YearTo are optional but mutually mandatory if provided")
                if query.yrTo is not None and query.yrFrom is not None:
                    query_parts.append("AND T. `Start_Year` BETWEEN %s AND %s")
                    params.extend([query.yrFrom, query.yrTo])

                query_parts.append("GROUP BY T.`ID`")
                final_query = " ".join(query_parts)
                await cursor.execute(final_query, params)
                titles = await cursor.fetchall()
                if not titles:
                    return Response(status_code=204)
                
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
                        genres =[GenreTitle(genreTitle=genre) for genre in title["Genres"].split(',')] if title["Genres"] else [],
                        titleAkas=[AkaTitle(**a) for a in akas_data],
                        principals=[PrincipalsObject(**p) for p in principals_data],
                        rating=RatingObject(avRating=str(title["Average_Rating"]), nVotes=str(title["Votes"]))
                    )

                    title_objects.append(title_object)
                
                if format == "csv":
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
                            'Principals': ", ".join([f"{'' if p.name is None else str(p.name)} ({'' if p.nameID is None else str(p.nameID)}) ({'' if p.category is None else str(p.category)})" for p in title.principals]),
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

                    return Response(content=output.getvalue(), media_type="text/plain")
                
                elif format == "json":
                    return title_objects
                
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format specifier")
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Genre, Rating, Production Year Endpoint 
@router.get("/search_genre_rating_pyear", response_class=HTMLResponse, responses=get_custom_responses())
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
                                             WHERE `Average_Rating` >= %s;""", (part,))
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
@router.get("/searchname", response_model=List[NameObject], responses=get_custom_responses())
async def search_name(query: nqueryObject = Body(...), format: str = "json"):
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported format specifier")

    try:
        async with await get_database_connection() as db_connection:
            async with db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""SELECT `Name_ID`, `Name`, `IMAGE`, `Birth_Year` as birthYr, `Death_Year` as deathYr, `ID`
                                        FROM `Person` 
                                        WHERE `Name` LIKE %s""", (f'%{query.namePart}%',))
                names = await cursor.fetchall()
                if not names:
                    return Response(status_code=204)

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
                
            if format == "json":
                return result
            elif format == "csv":
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

                return Response(content=output.getvalue(), media_type="text/plain")
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#First, Last Name Search Bar Endpoint
@router.get("/search_name", response_class=HTMLResponse, responses=get_custom_responses())
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
                    return Response(status_code=204)

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
async def admin_health_check(format: str = 'json'):
    try:
        async with await get_database_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1;")
                await cursor.fetchone()
        data = {"status": "OK", "dataconnection": "Connection to database is OK."}
        if format == 'csv':
            csv_data = ','.join(map(str, data.values()))
            csv_header = ','.join(data.keys())
            return PlainTextResponse(f"{csv_header}\n{csv_data}\n", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse(data, status_code=status.HTTP_200_OK)

    except Exception as e:
        data = {"status": "failed", "dataconnection": str(e)}
        if format == 'csv':
            csv_data = ','.join(map(str, data.values()))
            csv_header = ','.join(data.keys())
            return PlainTextResponse(f"{csv_header}\n{csv_data}\n", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse(data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Admin create backup
@router.post("/admin/backup")
async def initiate_backup():
    try:
        return await create_backup()    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/admin/resetall")
async def initiate_reset(format: str = 'json'):
    try:
        async with await get_database_connection() as connection, connection.cursor() as cursor:
            print("Starting reset process...")
            tables_to_drop = [
                        "Participates_In", 
                        "Title_Genre", 
                        "Profession_Person", 
                        "Alt_Title", 
                        "Episode", 
                        "Person", 
                        "Genre", 
                        "Profession", 
                        "Title"
                    ]

            # Execute DROP TABLE statements
            for table in tables_to_drop:
                try:
                    await cursor.execute(f"TRUNCATE TABLE `{table}`")
                except Exception as e:
                    print(f"Error clearing table {table}: {e}")
            
            await connection.commit()

            print("Database is now empty. Loading all the tables...")
            async def upload_data_from_tsv(file_path, upload_function):
                try:
                    async with aiofiles.open(file_path, mode='rb') as file:
                        response = await upload_function(file_path)
                        if isinstance(response, JSONResponse) and response.status_code == 500:
                            message = "Failed to upload data"
                            print(f"{message} for {file_path}")
                            return message
                except Exception as e:
                    print(f"Error uploading data from {file_path}: {e}")
                    return str(e)
                return None
    
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.realpath(__file__))

            files = {
                'title_basics': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.basics.tsv'), upload_title_basics),
                'title_akas':  (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.akas.tsv'), upload_title_akas),
                'name_basics': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_name.basics.tsv'), upload_name_basics),
                'title_crew': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.crew.tsv'), upload_title_crew),
                'title_episode': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.episode.tsv'), upload_title_episode),
                'title_principals': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.principals.tsv'), upload_title_principals),
                'title_ratings': (os.path.join(current_dir, '..', '..', 'db', 'data', 'truncated_title.ratings.tsv'), upload_title_ratings)
            }
            
            for key, (filename, upload_func) in files.items():
                error_message = await upload_data_from_tsv(filename, upload_func)
                if error_message:
                    if format == 'csv':
                        return PlainTextResponse(f"status, reason\nfailed, {error_message}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        return JSONResponse({"status": "failed", "reason": error_message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            if format == 'csv':
                return PlainTextResponse("status\nOK", status_code=status.HTTP_200_OK)
            else:
                return JSONResponse({"status": "OK"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)    
 



# endpoint 2
@router.post("/admin/upload/titlebasics")
async def upload_title_basics(file: Union[UploadFile, str], format: str = 'json'):
    try:
        # Check if 'file' is a string (filename)
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
                    ON DUPLICATE KEY UPDATE
                    Type = VALUES(Type),
                    Original_Title = VALUES(Original_Title),
                    IMAGE = VALUES(IMAGE),
                    Start_Year = VALUES(Start_Year),
                    End_Year = VALUES(End_Year),
                    Runtime = VALUES(Runtime),
                    isAdult = VALUES(isAdult)
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
                            query_insert_genre = """
                                INSERT INTO `Genre` (Genre) VALUES (%s)
                                ON DUPLICATE KEY UPDATE
                                Genre = VALUES(Genre)
                            """
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
                                query_title_genre = """
                                    INSERT INTO `Title_Genre` (Title_FK, Genre_FK) VALUES (%s, %s)
                                    ON DUPLICATE KEY UPDATE
                                    Title_FK = VALUES(Title_FK),
                                    Genre_FK = VALUES(Genre_FK)
                                """
                                await cursor.execute(query_title_genre, (title_fk, genre_fk))
                                await connection.commit()

            if format == 'csv':
                return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
            else:  # Default to JSON
                return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# endpoint 3
@router.post("/admin/upload/titleakas")
async def upload_title_akas(file: Union[UploadFile, str], format: str = 'json'):
    try:
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
                if (title_id == '\\N' or title_id =='/N'):
                    title_id = None
                if (ordering == '\\N' or ordering == '/N'):
                    ordering = None
                if (title_aka == '\\N' or title_aka == '/N'):
                    title_aka = None
                if (region == '\\N' or region == '/N'):
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
                    query_insert_alt_title = """
                        INSERT INTO `Alt_Title` (Title_FK, Ordering, Title_AKA, Region) 
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        Title_FK = VALUES(Title_FK),
                        Ordering = VALUES(Ordering),
                        Title_AKA = VALUES(Title_AKA),
                        Region = VALUES(Region)
                    """
                    await cursor.execute(query_insert_alt_title, (title_fk, ordering, title_aka, region))
                    await connection.commit()
                    
                except Exception as e:
                    errors.append(str(e))
                    continue

        if errors:
            # If there are errors, raise an HTTPException with the collected error messages
            error_message = "\n".join(errors)
            if format == 'csv':
                raise HTTPException(status_code=500, detail=f"status, reason\nfailed, {error_message}")
            else:  # Default to JSON
                raise HTTPException(status_code=500, detail={"status": "failed", "reason": error_message})

        if format == 'csv':
            return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Admin Endpoint 4
@router.post("/admin/upload/namebasics")
async def upload_name_basics(file: Union[UploadFile, str], format: str = 'json'):
    try:
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
            df = pd.read_csv(file.file, sep='\t', low_memory=False)

        # Iterate over DataFrame rows and insert data into the database
        for _, row in df.iterrows():
            name_id = row['nconst']
            primaryname = row['primaryName']
            image_url = row['img_url_asset']
            birthyear = row['birthYear']
            deathyear = row['deathYear']

            # Insert data into the 'Name' table
            name_fk = await insert_into_name((name_id, primaryname, image_url, birthyear, deathyear))

            # Handle primaryProfession column
            professions_value = row['primaryProfession']
            if isinstance(professions_value, str):

                professions = professions_value.split(',')

                for profession in professions:
                    # Insert data into the 'Profession' table and fetch its ID
                    profession_fk = await insert_into_profession((profession,))
                    # Fetch Name_FK (id) of the name just added to the 'Name' table
                    # Check if the profession_fk is not None before inserting into Profession_Person
                    if profession_fk is not None and name_fk is not None:
                        # Insert data into the 'Profession_Person' table
                        print("NOW I AM INSERTING INTO PROFESSION_PERSON")
                        await insert_into_profession_person((profession_fk, name_fk))
                    else:
                        print(f"Profession or Name_FK is None, skip insertion {profession_fk} {name_fk}")

        if format == 'csv':
            return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Admin Endpoint 5
@router.post("/admin/upload/titlecrew")
async def upload_title_crew(file: Union[UploadFile, str], format: str = 'json'):
    try:
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
                    # Check if the title_id exists in the 'Title' table
                    title_fk = await fetch_title_primary_key(title_id)
                    if title_fk is None:
                        errors.append(f"Title with Title_ID {title_id} doesn't exist in the database.")
                        raise HTTPException(status_code=500, detail=f"Title with Title_ID {title_id} doesn't exist in the database.")
                    
                    # Check if the director's name_id exists in the 'Name' table
                    director_name_fk = await fetch_person_primary_key(director_id)
                    if director_name_fk is None:
                        print(f"Person with Name_ID {director_id} doesn't exist in the database. Skip insertion")
                        continue

                    # Check if the entry already exists in the 'Participates_In' table
                    #existing_director_entry = await check_existing_participation(director_name_fk, title_fk, 'director')
                    #if existing_director_entry:
                        #print("Entry already exists, skip insertion")
                        # Entry already exists, skip insertion
                        #continue

                    # Insert data into the 'Participates_In' table for directors
                    await insert_into_participates_in_crew((title_fk, director_name_fk, 'director'))
                except Exception as e:
                    errors.append(str(e))
                    

            # Process writers
            for writer_id in writers:
                try:
                    # Check if the writer's name_id exists in the 'Name' table
                    writer_name_fk = await fetch_person_primary_key(writer_id)
                    if writer_name_fk is None:
                        print(f"Person with Name_ID {writer_id} doesn't exist in the database. Skip insertion")
                        continue

                    # Check if the title_id exists in the 'Title' table
                    title_fk = await fetch_title_primary_key(title_id)
                    if title_fk is None:
                        errors.append(f"Title with Title_ID {title_id} doesn't exist in the database.")
                        raise HTTPException(status_code=500, detail=f"Title with Title_ID {title_id} doesn't exist in the database.")

                    # Check if the entry already exists in the 'Participates_In' table
                    #existing_writer_entry = await check_existing_participation(writer_name_fk, title_fk, 'writer')
                    #if existing_writer_entry:
                        #print("Entry already exists, skip insertion")
                        # Entry already exists, skip insertion
                        #continue

                    # Insert data into the 'Participates_In' table for writers
                    await insert_into_participates_in_crew((title_fk, writer_name_fk, 'writer'))
                except Exception as e:
                    errors.append(str(e))
                    

        if errors:
            # If there are errors, raise an HTTPException with the collected error messages
            error_message = "\n".join(errors)
            if format == 'csv':
                raise HTTPException(status_code=500, detail=f"status, reason\nfailed, {error_message}")
            else:  # Default to JSON
                raise HTTPException(status_code=500, detail={"status": "failed", "reason": error_message})

        if format == 'csv':
            return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if "Title with Title_ID" in str(e) and "doesn't exist in the database." in str(e):
            error_message = "A title does not exist"
            if format == 'csv':
                return PlainTextResponse(f"status, reason\nfailed, {error_message}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:  # Default to JSON
                return JSONResponse({"status": "failed", "reason": error_message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Admin Endpoint 6
@router.post("/admin/upload/titleepisode")
async def upload_title_episode(file: Union[UploadFile, str], format: str = 'json'):
    try:
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
            if format == 'csv':
                raise HTTPException(status_code=500, detail=f"status, reason\nfailed, {error_message}")
            else:  # Default to JSON
                raise HTTPException(status_code=500, detail={"status": "failed", "reason": error_message})

        if format == 'csv':
            return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
        else:  # Default to JSON
            return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Endpoint 7
@router.post("/admin/upload/titleprincipals")
async def upload_title_principals(file: Union[UploadFile, str], format: str = 'json'):
    try:
        # Check if the uploaded file is of the correct format
        #if not file.filename.endswith(".tsv"):
            #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be in TSV format")
        
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
            if format == 'csv':
                return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
            else:  # Default to JSON
                return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)
        else:
            if format == 'csv':
                return PlainTextResponse("status, message\nfailed, No data provided in the file", status_code=status.HTTP_204_NO_CONTENT)
            else:  # Default to JSON
                return JSONResponse({"status": "failed", "message": "No data provided in the file"}, status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Admin Endpoint 8
# Function to update data in the Title table
async def update_title_ratings(title_id, average_rating, num_votes):
    query = "UPDATE `Title` SET `Average_Rating` = %s, `Votes` = %s WHERE `Title_ID` = %s"
    async with await get_database_connection() as connection, connection.cursor() as cursor:

        try:
            await cursor.execute(query, (average_rating, num_votes, title_id))
            await connection.commit()
            #print("Insert successful")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Endpoint 8 for uploading title ratings
@router.post("/admin/upload/titleratings")
async def upload_title_ratings(file: Union[UploadFile, str], format: str = 'json'):
    try:
        
        # Check if the uploaded file is of the correct format
        #if not file.filename.endswith(".tsv"):
            #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be in TSV format")
        if isinstance(file, str):
            with open(file, 'r') as f:
                df = pd.read_csv(f, sep='\t', low_memory=False)
        else:  # 'file' is an UploadFile
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
            if format == 'csv':
                return PlainTextResponse("status, message\nOK, File uploaded and data stored successfully", status_code=status.HTTP_200_OK)
            else:  # Default to JSON
                return JSONResponse({"status": "OK", "message": "File uploaded and data stored successfully"}, status_code=status.HTTP_200_OK)
        else:
            if format == 'csv':
                return PlainTextResponse("status, message\nfailed, No data provided in the file", status_code=status.HTTP_204_NO_CONTENT)
            else:  # Default to JSON
                return JSONResponse({"status": "failed", "message": "No data provided in the file"}, status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        if format == 'csv':
            return PlainTextResponse(f"status, reason\nfailed, {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # Default to JSON
            return JSONResponse({"status": "failed", "reason": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
