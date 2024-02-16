import requests

def test_upload_title_basics():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titlebasics"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.basics.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_title_akas():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titleakas"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.akas.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_name_basics():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/namebasics"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_name.basics.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_title_crew():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titlecrew"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.crew.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_title_episode():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titleepisode"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.episode.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_title_principals():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titleprincipals"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.principals.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def test_upload_title_ratings():
    # Set the endpoint URL
    endpoint = "http://localhost:9876/ntuaflix_api/admin/upload/titleratings"
    
    # Set the file path of the TSV file
    file_path = "/home/ariadni/Documents/softeng23-42/back-end/db/data/truncated_title.ratings.tsv"  # Update with your file path
    
    try:
        # Open and read the TSV file
        with open(file_path, 'rb') as file:
            # Set up the request payload
            files = {'file': file}
            
            # Send the POST request
            response = requests.post(endpoint, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")


def test_title_endpoint(title_id, format_type):
    url = f"http://localhost:9876/ntuaflix_api/title/{title_id}?format_type={format_type}"
    response = requests.get(url)
    
    if response.status_code == 200:
        if format_type == "json":
            if response.text:  # Check if response body is not empty
                print("Title Object:")
                print(response.json())
            else:
                print("Empty response body.")
        elif format_type == "csv":
            if response.text:  # Check if response body is not empty
                print("CSV Response:")
                print(response.text)
                
                # You can also convert the CSV response to a DataFrame if needed
                df = pd.read_csv(io.StringIO(response.text))
                print("DataFrame from CSV:")
                print(df)
            else:
                print("Empty response body.")
        else:
            print("Unsupported format type.")
    elif response.status_code == 204:
        print("No content found for the provided title ID.")
    else:
        print(f"Failed to fetch title details. Status Code: {response.status_code}")
        print(response.text)

def test_search_titles(query, format_type):
    url = f"http://localhost:9876/ntuaflix_api/searchtitle?query={query}&format_type={format_type}"
    response = requests.get(url)
    if response.status_code == 200:
        if format_type == "json":
            print("Title Objects:")
            print(response.json())
        elif format_type == "csv":
            csv_content = response.text
            if csv_content:
                print("CSV Content:")
                print(csv_content)
            else:
                print("Empty CSV content received.")
    elif response.status_code == 204:
        print("No titles found matching the query.")
    else:
        print(f"Failed to fetch titles. Status Code: {response.status_code}")
        print(response.text)

def test_genre_search(qgenre, minrating, yrFrom=None, yrTo=None, format_type="json"):
    url = "http://localhost:9876/ntuaflix_api/bygenre"
    params = {
        "qgenre": qgenre,
        "minrating": minrating,
        "yrFrom": yrFrom,
        "yrTo": yrTo,
        "format_type": format_type
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        if format_type == "json":
            print("Title Objects:")
            print(response.json())
        elif format_type == "csv":
            csv_content = response.text
            if csv_content:
                print("CSV Content:")
                print(csv_content)
            else:
                print("Empty CSV content received.")
        else:
            print("Unsupported format type.")
    elif response.status_code == 204:
        print("No titles found matching the query.")
    else:
        print(f"Failed to fetch titles. Status Code: {response.status_code}")
        print(response.text)

def test_search_name(namePart: str, format_type: str = "json"):
    url = "http://localhost:9876/ntuaflix_api/searchname"
    params = {
        "query": namePart,
        "format_type": format_type
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        if format_type == "json":
            print("Name Objects:")
            print(response.json())
        elif format_type == "csv":
            csv_content = response.text
            if csv_content:
                print("CSV Content:")
                print(csv_content)
            else:
                print("Empty CSV content received.")
        else:
            print("Unsupported format type.")
    elif response.status_code == 204:
        print("No names found matching the query.")
    else:
        print(f"Failed to fetch names. Status Code: {response.status_code}")
        print(response.text)

def test_get_name_details(nameID: str, format_type: str = "json"):
    url = f"http://localhost:9876/ntuaflix_api/name/{nameID}"
    params = {"format_type": format_type}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        if format_type == "json":
            name_object = response.json()
            print("Name Object:")
            print(name_object)
        elif format_type == "csv":
            csv_content = response.text
            if csv_content:
                print("CSV Content:")
                print(csv_content)
            else:
                print("Empty CSV content received.")
        else:
            print("Unsupported format type.")
    elif response.status_code == 204:
        print("No name found matching the query.")
    else:
        print(f"Failed to fetch name details. Status Code: {response.status_code}")
        print(response.text)

# Call the functions to test the admin upload endpoints
test_upload_title_basics()
test_upload_title_akas()
test_upload_name_basics()
test_upload_title_crew()
test_upload_title_episode()
test_upload_title_principals()
test_upload_title_ratings()

# Replace the parameters with your desired values for testing
test_title_endpoint("tt0103145", "json")
test_search_titles("Baby", "csv")
test_genre_search("Drama", "7.0", "1990", "2000", "json")
test_search_name("Smith", format_type="csv")
test_get_name_details("nm9928038", format_type="csv")
