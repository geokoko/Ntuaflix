import argparse, requests, os, csv

BASE_URL = "http://127.0.0.1:9876/ntuaflix_api" 


#Using try-catch for error handlind
def healthcheck():
    try:
        print("Admin performs heathcheck")
        response = requests.get(f"{BASE_URL}/admin/healthcheck")
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#Not tested yet
def resetall():
    try:
        print("Admin performs a total reset")
       # response = requests.get(f"{BASE_URL}/admin/resetall")
       # handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#Not tested yet
def newtitles(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titlebasics', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#Not tested yet
def newakas(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titleakas', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def newnames(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/namebasics', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newcrew(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titlecrew', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newepisode(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titleepisode', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newprincipals(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titleprincipals', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newratings(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titleratings', files=files)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def title(args):
    try:
        params = {"format": args.format}
        response = requests.get(f"{BASE_URL}/title/{args.titleID}", params = params)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def name(args):
    try:
        params = {"format": args.format}
        response = requests.get(f"{BASE_URL}/name/{args.nameid}", params=params)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#In order to correclty check and handle the API responses
def handle_response(response, format):
    if response.status_code == 200:
        if format == 'json':
            print(response.json())
        elif format == "csv":
            print(response.text)
        else:
            print("Unsupported format")
    elif response.status_code == 204:
        print("Status Code 204: No data returned.")
    elif response.status_code == 400:
        print("Status Code 400: Bad request. Invalid parameters provided in the call.")
    elif response.status_code == 404:
        print("Status Code 404: Not Found. The requested resource was not found.")
    elif response.status_code == 500:
        print("Status Code 500: Internal server error.")
    else:
        print(f"Unexpected status code: {response.status_code}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ntuaflix CLI")
    parser.add_argument("scope", choices=["healthcheck", "resetall", "title", "name", "newtitles", "newakas", "newnames", "newcrew", "newepisode", "newprincipals", "newratings"])
    parser.add_argument("--filename", help="Specify filename for newprincipals/newratings scope")
    
    parser.add_argument("--titleID", help="Specify titleID for title scope")
    parser.add_argument("--titlepart", help="Specify titlepart for searchtitle scope")
   
    parser.add_argument("--genre", help="Specify genre for bygenre scope")
    parser.add_argument("--min", help="Specify min for bygenre scope")
    parser.add_argument("--from", help="Specify from for bygenre scope")
    parser.add_argument("--to", help="Specify to for bygenre scope")
   
    parser.add_argument("--nameid", help="Specify nameID for name scope")
    parser.add_argument("--name", help="Specify name for searchname scope")

    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Specify output format")

    args = parser.parse_args()

    if args.scope == "healthcheck":
        healthcheck()
    elif args.scope == "resetall":
        resetall()
    elif args.scope == "name":
        if not args.nameid:
            print("Error: --nameid is a mandatory parameter for the 'name' scope.")
        else:
            name(args)
    elif args.scope == "title":
        if not args.titleID:
            print("Error: --titleID is a mandatory parameter for the 'title' scope.")
        else:
            title(args)
    elif args.scope == "newtitles":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newtitles' scope.")
        else:
            newtitles(args)  
    elif args.scope == "newnames":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newnames' scope.")
        else:
            newnames(args)  
    elif args.scope == "newcrew":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newcrew' scope.")
        else:
            newcrew(args)  
    elif args.scope == "newepisode":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newepisode' scope.")
        else:
            newepisode(args)  
    elif args.scope == "newprincipals":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newprincipals' scope.")