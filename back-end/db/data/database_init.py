import pandas as pd
import numpy as np
import pymysql
import os
from dotenv import load_dotenv
import platform
from subprocess import call
import time

load_dotenv()

host = os.environ.get('DB_HOST')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWD')
db = os.environ.get('DB_NAME')
print("Current Working Directory:", os.getcwd())
script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ntuaflix_ddl.sql'))

def run_ddl_script(host, user, password, script_path):
    if platform.system() == "Windows":
        try:
            command = f'mysql -h {host} -u {user} -p{password} < "{script_path}"'
            os.system(f'cmd /c "{command}"')
        except Exception as e:
            raise str(e)
    else:
        try:
            os.system(f"mysql -h {host} -u {user} -p{password} < {script_path}")
        except Exception as e:
            raise str(e)

def populate_database():
    files = {
        'name_basics': os.path.join(os.path.dirname(__file__), 'truncated_name.basics.tsv'),
        'title_akas':  os.path.join(os.path.dirname(__file__), 'truncated_title.akas.tsv'),
        'title_basics': os.path.join(os.path.dirname(__file__), 'truncated_title.basics.tsv'),
        'title_crew': os.path.join(os.path.dirname(__file__), 'truncated_title.crew.tsv'),
        'title_episode': os.path.join(os.path.dirname(__file__), 'truncated_title.episode.tsv'),
        'title_principals': os.path.join(os.path.dirname(__file__), 'truncated_title.principals.tsv'),
        'title_ratings': os.path.join(os.path.dirname(__file__), 'truncated_title.ratings.tsv')
    }

    replacement_dict = {
        '\\N': None
    }

    dataframes = {key: pd.read_csv(files[key], sep = '\t', low_memory=False) for key in files}
    import random

    ####################################TITLE_DF##########################################################
    title_df = pd.merge(dataframes['title_basics'], dataframes['title_ratings'], how='left', on='tconst')
    title_df = title_df[['tconst', 'primaryTitle', 'titleType', 'startYear', 'endYear', 'runtimeMinutes', 'averageRating', 'numVotes', 'isAdult', 'img_url_asset']]
    title_df.columns = ['Title_ID', 'Original_Title', 'Type', 'Start_Year', 'End_Year', 'Runtime', 'Average_Rating', 'Votes', 'isAdult', 'IMAGE']
    title_df.fillna(random.randint(1, 10), inplace=True)
    title_df.replace('\\N', None, inplace=True)

    ###################################ALT_TITLE#########################################################
    alt_title_df = dataframes['title_akas'][['titleId', 'ordering', 'title', 'region']]
    alt_title_df.columns = ['Title_FK', 'Ordering', 'Title_AKA', 'Region']
    alt_title_df.fillna(random.randint(1, 100), inplace=True)
    alt_title_df.replace('\\N', None, inplace=True)

    ####################################EPISODE_DF######################################################
    episode_df = dataframes['title_episode'][['tconst', 'parentTconst', 'seasonNumber', 'episodeNumber']]
    episode_df.columns = ['Title_ID', 'parentTitle_ID', 'Season', 'Episode_Num']
    episode_df.fillna(random.randint(1, 100), inplace= True)
    episode_df.replace('\\N', None, inplace=True)

    #####################################PERSON_DF#########################################################
    person_df = dataframes['name_basics'][['nconst', 'primaryName', 'birthYear', 'deathYear', 'img_url_asset']]
    person_df.columns = ['Name_ID', 'Name', 'Birth_Year', 'Death_Year', 'Image']
    person_df.fillna(random.randint(1, 100), inplace=True)
    person_df.replace('\\N', None, inplace=True)

    #################################PRINCIPALS_DATAFRAMES#################################################
    dataframes['title_principals']['category'] = dataframes['title_principals']['category'].replace('\\N', '')
    dataframes['title_principals']['job'] = dataframes['title_principals']['job'].replace('\\N', '')
    dataframes['title_principals']['movie_job'] = dataframes['title_principals'].apply(lambda row: row['category'] + (',' + row['job'] if row['job'] != '' and row['job'] != row['category'] else ''), axis=1)

    participates_in_df = dataframes['title_principals'][['tconst', 'nconst', 'ordering', 'movie_job', 'characters']]
    participates_in_df.columns = ['Title_FK', 'Name_FK', 'Ordering', 'Job_Category', 'Character']
    participates_in_df.fillna(random.randint(1, 100), inplace=True)
    participates_in_df.replace('\\N', None, inplace=True)

    ############################GENRES_DATAFRAMES#######################################################

    unique_genres = set()
    for genre_list in dataframes['title_basics']['genres'].dropna().str.split(','):
        unique_genres.update([genre.strip() for genre in genre_list])

    genres_df = pd.DataFrame({'Genre': list(unique_genres)})
    genres_df.replace('\\N', None, inplace=True)
    genres_df.dropna(how='all', inplace=True)

    title_genre_df = dataframes['title_basics'][['tconst', 'genres']]
    title_genre_df.columns = ['Title_FK', 'Genre']
    title_genre_df['Genre'] = title_genre_df['Genre'].str.split(',')
    title_genre_df = title_genre_df.explode('Genre')
    title_genre_df.fillna(random.randint(1, 100), inplace=True)
    title_genre_df.replace('\\N', None, inplace=True)

    ###################################################Profession_DataFrame#####################################################
    profession_df = dataframes['name_basics'][['nconst', 'primaryProfession']]
    profession_df.columns = ['Name_ID', 'Profession']
    profession_df['Profession'] = profession_df['Profession'].str.split(',')
    profession_df = profession_df.explode('Profession')
    profession_df.fillna(random.randint(1, 100), inplace=True)
    profession_df.replace('\\N', None, inplace=True)

    print(profession_df.head())

    ###################################################TITLE###########################################################
    title_primary_keys = {}
    start_time = time.time()
    success = True

    try:
        with connection.cursor() as cursor:
            # Dealing with Titles first
            q = "INSERT INTO `Title` (Title_ID, Original_Title, Type, Start_Year, End_Year, Runtime, Average_Rating, Votes, isAdult, IMAGE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            
            for index, row in title_df.iterrows():
                try:
                    tconst = row['Title_ID']
                    original_title = row['Original_Title']
                    type = row['Type']
                    start_year = row['Start_Year']
                    end_year = row['End_Year']
                    runtime = row['Runtime']
                    average_rating = row['Average_Rating']
                    votes = row['Votes']
                    is_adult = row['isAdult']
                    image = row['IMAGE']

                    cursor.execute(q, (tconst, original_title, type, start_year, end_year, runtime, average_rating, votes, is_adult, image))
                    connection.commit()
                
                    # Saving the primary key
                    title_primary_keys[tconst] = cursor.lastrowid

                except Exception as e:
                    success = False
                    print(f"Error inserting title ID {tconst}: {e}")
                    raise

            if success:
                print("All titles inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

    ######################################################PERSON###############################################################
    person_primary_keys = {}
    start_time = time.time()
    success = True

    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO `Person` (Name_ID, Name, Image, Birth_Year, Death_Year) VALUES (%s, %s, %s, %s, %s)"
            
            for index, row in person_df.iterrows():
                name_id = row['Name_ID']
                name = row['Name']
                image = row['Image']
                birth_year = row['Birth_Year']
                death_year = row['Death_Year']

                try:
                    cursor.execute(query, (name_id, name, image, birth_year, death_year))
                    connection.commit()
                
                    # Saving the auto-generated primary key
                    person_primary_keys[name_id] = cursor.lastrowid
                except Exception as e:
                    success = False
                    connection.rollback()  # Rollback in case of error
            
            if success:
                print("All people inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

    #####################################################PARTICIPATES_IN#########################################################
    success = True
    start_time = time.time()

    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO `Participates_In` (Title_FK, Name_FK, Ordering, Job_Category, `Character`) VALUES (%s, %s, %s, %s, %s)"
            
            for index, row in participates_in_df.iterrows():
                title_fk = title_primary_keys.get(row['Title_FK'])
                name_fk = person_primary_keys.get(row['Name_FK'])
                ordering = row['Ordering']
                job_category = row['Job_Category']
                character = row['Character']

                try:
                    cursor.execute(query, (title_fk, name_fk, ordering, job_category, character))
                    connection.commit()
                except Exception as e:
                    success = False
                    print(f"an error occured with {title_fk} and {name_fk}: {e}")
                    raise
            
            if success:
                print("All principals inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

    #######################################################GENRES###########################################################
    success = True
    start_time = time.time()

    try:
        with connection.cursor() as cursor:
            genre_query = "INSERT INTO `Genre` (Genre) VALUES (%s)"
            genre_primary_keys = {}

            for index, row in genres_df.iterrows():
                genre = row['Genre']
                try:
                    cursor.execute(genre_query, (genre,))
                    connection.commit()
                except Exception as e:
                    success = False
                    print(f"{genre} failed: {e}")
                    raise
                # Saving the primary key
                genre_primary_keys[genre] = cursor.lastrowid

            title_genre_query = "INSERT INTO `Title_Genre` (Title_FK, Genre_FK) VALUES (%s, %s)"

            for index, row in title_genre_df.iterrows():
                title_fk = title_primary_keys.get(row['Title_FK'])
                if title_fk == None:
                    continue
                genre_fk = genre_primary_keys.get(row['Genre'])

                try:
                    if title_fk is not None and genre_fk is not None:
                        cursor.execute(title_genre_query, (title_fk, genre_fk))
                        connection.commit()
                    else:
                        connection.rollback()
                except Exception as e:
                    success = False
                    print(str(e))
            
            if success:
                print("All genre and title_genre fields inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")
    ##################################EPISODES####################################################################
    success = True
    start_time = time.time()
    episode_query = "INSERT INTO `Episode` (Title_FK, Parent_Title_FK, Season, Episode_Num) VALUES (%s, %s, %s, %s)"

    try:
        with connection.cursor() as cursor:
            for index, row in episode_df.iterrows():
                title_fk = title_primary_keys.get(row['Title_ID'])
                parentTconst = row['parentTitle_ID']
                season = row['Season']
                episode_num = row['Episode_Num']

                # Ensure both foreign keys are found
                try:
                    cursor.execute(episode_query, (title_fk, parentTconst, season, episode_num))
                    connection.commit()
                except Exception as e:
                    success = False
                    print(f"Error inserting episode: {e}")
                    connection.rollback()
                
            if success:
                print("All episodes inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

    ##########################################ALT_TITLE########################################################
    alt_title_primary_keys = {}
    start_time = time.time()
    success = True

    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO `Alt_Title` (Title_FK, Ordering, Title_AKA, Region) VALUES (%s, %s, %s, %s)"
            
            for index, row in alt_title_df.iterrows():
                title_fk = title_primary_keys.get(row['Title_FK'])
                ordering = row['Ordering']
                title_aka = row['Title_AKA']
                region = row['Region']

                try:
                    cursor.execute(query, (title_fk, ordering, title_aka, region))
                    connection.commit()
                
                    # Saving the auto-generated primary key
                    alt_title_primary_keys[(title_fk, title_aka)] = cursor.lastrowid
                except Exception as e:
                    success = False
                    print(f"Error inserting Title_FK: {title_fk}, Title_AKA: {title_aka}: {e}")
                    connection.rollback()  # Rollback in case of error

            if success:
                print("All title_akas inserted")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

    #################################PROFESSION AND PROFESSION_PERSON################################################
    profession_primary_keys = {}
    start_time = time.time()
    success = True

    try:
        with connection.cursor() as cursor:
            profession_query = "INSERT INTO `Profession` (Profession) VALUES (%s)"

            for index, row in profession_df.iterrows():
                profession = row['Profession']
                try:
                    cursor.execute(profession_query, (profession,))
                    connection.commit()
                except Exception as e:
                    success = False
                    print(f"{profession} failed: {e}")
                    raise
                # Saving the primary key
                profession_primary_keys[profession] = cursor.lastrowid

            profession_person_query = "INSERT INTO `Profession_Person` (Name_FK, Profession_FK) VALUES (%s, %s)"

            for index, row in profession_df.iterrows():
                name_fk = person_primary_keys.get(row['Name_ID'])
                profession_fk = profession_primary_keys.get(row['Profession'])

                try:
                    if name_fk is not None and profession_fk is not None:
                        cursor.execute(profession_person_query, (name_fk, profession_fk))
                        connection.commit()
                    else:
                        connection.rollback()
                except Exception as e:
                    success = False
                    print(str(e))
            
            if success:
                print("All profession and profession_person inserted")       
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} sec")

connection = pymysql.connect(host=host, user=user, password=password, db=db)
print("Connection to the database successful")
with connection.cursor() as cursor:
    cursor.execute("""SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'tl'
                    AND table_name IN (
                        "Title",
                        "Person", 
                        "Participates_In", 
                        "Genre", 
                        "Title_Genre", 
                        "Episode", 
                        "Alt_Title", 
                        "Profession",
                        "Profession_Person"
                    );""")
    res = cursor.fetchall()

if not res:
    print("Initializing database...")
    run_ddl_script(host, user, password, script_path)
    populate_database()
else:
    print("Database already initialized")