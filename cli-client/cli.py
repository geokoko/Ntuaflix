import argparse, requests, os, csv, json
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://0.0.0.0:9876/ntuaflix_api" 


#Using try-catch for error handlind
def healthcheck(args):
    try:
        response = requests.get(f"{BASE_URL}/admin/healthcheck", params={'format': args.format}, verify = False)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def resetall(args):
    try:
        response = requests.post(f"{BASE_URL}/admin/resetall", params={'format': args.format}, verify = False)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newtitles(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titlebasics', files=files, params={'format': args.format}, verify = False)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def newakas(args):
    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    try:
        with open(args.filename, 'rb') as file:
            files = {'file': (args.filename, file, 'application/octet-stream')}
            response = requests.post(f'{BASE_URL}/admin/upload/titleakas', files=files, params={'format': args.format}, verify = False)
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
            response = requests.post(f'{BASE_URL}/admin/upload/namebasics', files=files, params={'format': args.format}, verify = False)
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
            response = requests.post(f'{BASE_URL}/admin/upload/titlecrew', files=files, params={'format': args.format}, verify = False)
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
            response = requests.post(f'{BASE_URL}/admin/upload/titleepisode', files=files, params={'format': args.format}, verify = False)
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
            response = requests.post(f'{BASE_URL}/admin/upload/titleprincipals', files=files, params={'format': args.format}, verify = False)
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
            response = requests.post(f'{BASE_URL}/admin/upload/titleratings', files=files, params={'format': args.format}, verify = False)
            handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def title(args):
    try:
        params = {"format": args.format}
        response = requests.get(f"{BASE_URL}/title/{args.titleID}", params = params, verify = False)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def searchtitle(args):
    try:
        query = {"titlePart": args.titlepart}
        headers = {'Content-Type': 'application/json'}

        response = requests.get(f"{BASE_URL}/searchtitle", data=json.dumps(query), headers=headers, params={"format": args.format}, verify = False )
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def bygenre(args):
    try:
        year_from = str(getattr(args, 'from')) if getattr(args, 'from') is not None else None
        year_to = str(args.to) if args.to is not None else None
        
        if year_from is not None and year_to is None:
            print("--from and --to are optional but mutually mandatory if provided")
        
        if year_to is not None and year_from is None:
            print("--from and -to are optional but mutually mandatory if provided")

        query = {"qgenre": args.genre, "minrating": args.min, "yrFrom": year_from, "yrTo": year_to}
        headers = {'Content-Type': 'application/json'}

        response = requests.get(f"{BASE_URL}/bygenre", data=json.dumps(query), headers=headers, params={"format": args.format}, verify = False )
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def name(args):
    try:
        params = {"format": args.format}
        response = requests.get(f"{BASE_URL}/name/{args.nameid}", params=params, verify = False)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def searchname(args):
    try:
        query = {"namePart": args.name}
        headers = {'Content-Type': 'application/json'}

        response = requests.get(f"{BASE_URL}/searchname", data=json.dumps(query), headers=headers, params={"format": args.format}, verify = False )
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#In order to correclty check and handle the API responses
def handle_response(response, format):
    if response.status_code == 200:
        print("Status Code 200")
        if format == 'json':
            try:
                print(response.json())
            except UnicodeEncodeError:
                print(response.text.encode('utf-8', errors='ignore').decode('utf-8'))
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
        print("The function returned:")
        if format == 'json':
            try:
                print(response.json())
            except UnicodeEncodeError:
                print(response.text.encode('utf-8', errors='ignore').decode('utf-8'))
        elif format == "csv":
            print(response.text)
        else:
            print("Unsupported format")
    else:
        print(f"Unexpected status code: {response.status_code}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ntuaflix CLI")
    parser.add_argument("scope", choices=["healthcheck", "resetall", "title", "searchtitle", 
                                          "bygenre", "name", "searchname","newtitles", "newakas", 
                                          "newnames", "newcrew", "newepisode", "newprincipals", "newratings"])
    parser.add_argument("--filename", help="Specify filename for the uploads")
    
    parser.add_argument("--titleID", help="Specify titleID for title scope")
    parser.add_argument("--titlepart", help="Specify titlepart for searchtitle scope")
   
    parser.add_argument("--genre", help="Specify genre for bygenre scope")
    parser.add_argument("--min", help="Specify minrating for bygenre scope")
    parser.add_argument("--from", help="Specify yrFrom for bygenre scope")
    parser.add_argument("--to", help="Specify yrTo for bygenre scope")
   
    parser.add_argument("--nameid", help="Specify nameID for name scope")
    parser.add_argument("--name", help="Specify name for searchname scope")

    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Specify output format")

    args = parser.parse_args()

    if args.scope == "healthcheck":
        healthcheck(args)
    elif args.scope == "resetall":
        resetall(args)
    elif args.scope == "name":
        if not args.nameid:
            print("Error: --nameid is a mandatory parameter for the 'name' scope.")
        else:
            name(args)
    elif args.scope == "searchname":
        if not args.name:
            print("Error: --name is a mandatory parameter for the 'searchname' scope.")
        else:
            searchname(args)
    elif args.scope == "title":
        if not args.titleID:
            print("Error: --titleID is a mandatory parameter for the 'title' scope.")
        else:
            title(args)
    elif args.scope == "searchtitle":
        if not args.titlepart:
            print("Error: --titlepart is a mandatory parameter for the 'searchtitle' scope.")
        else:
            searchtitle(args)
    elif args.scope == "bygenre":
        if not (args.genre and args.min):
            print("Error: --genre is a mandatory parameter for the 'bygenre' scope.")
            print("Error: --min is a mandatory parameter for the 'bygenre' scope.")
        else:
            bygenre(args)
    elif args.scope == "newtitles":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newtitles' scope.")
        else:
            newtitles(args)  
    elif args.scope == "newakas":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newakas' scope.")
        else:
            newakas(args)  
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
        else:
            newprincipals(args)
    elif args.scope == "newratings":
        if not args.filename:
            print("Error: --filename is a mandatory parameter for the 'newratings' scope.")
        else:
            newratings(args)
