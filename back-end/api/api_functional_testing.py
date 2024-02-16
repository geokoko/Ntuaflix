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

# Call the function to test the endpoint
test_upload_title_basics()
test_upload_title_akas()
test_upload_name_basics()
test_upload_title_crew()
test_upload_title_episode()
test_upload_title_principals()
test_upload_title_ratings()
