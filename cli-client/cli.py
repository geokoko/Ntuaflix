import argparse, requests, os, csv

BASE_URL = "http://127.0.0.1:8000" 

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

    with open(args.filename, 'r') as file:
        data = file.read()
    try:
        response = requests.post('/admin/upload/titlebasics', data=data)
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")




def name(args):
    try:
        response = requests.get(f"{BASE_URL}/name/{args.nameid}")
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#endpoint not working
def title(args):
    try:
        response = requests.get(f"{BASE_URL}/title/{args.titleid}")
        handle_response(response, args.format)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#In order to correclty check and handle the API responses
def handle_response(response, format):
    if response.status_code == 200:
        if format == 'json':
            print(response.json())
        elif format == 'csv':
            # To DO: Implement CSV handling
            pass
        else:
            print(response.text)
    elif response.status_code == 204:
        print("No data returned.")
    elif response.status_code == 400:
        print("Bad request. Invalid parameters provided in the call.")
    elif response.status_code == 404:
        print("Not Found. The requested resource was not found.")
    elif response.status_code == 500:
        print("Internal server error.")
    else:
        print(f"Unexpected status code: {response.status_code}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ntuaflix CLI")
    parser.add_argument("scope", choices=["healthcheck", "resetall", "title","name"])
    parser.add_argument("--filename", help="Specify filename for newtitles scope")
    parser.add_argument("--nameid", help="Specify nameID for name scope")
    parser.add_argument("--titleid", help="Specify titleID for title scope")
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
        if not args.titleid:
            print("Error: --titleid is a mandatory parameter for the 'title' scope.")
        else:
            title(args)
    else:
        print("Invalid scope. Supported scopes are 'healthcheck', 'name', and 'resetall'.")
