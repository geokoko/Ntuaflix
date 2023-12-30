import argparse, requests, os

#Using try-catch for error handlind
def healthcheck(args):
    try:
        #response = requests.get("/admin/healthcheck")
        #handle_response(response, args.format)
        print("Admin performs heathcheck")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


#In order to correclty check and handle the API responses
def handle_response(response, format):
    if response.status_code == 200:
        print("Success!")
        print(response.json() if format == 'json' else response.text)
    elif response.status_code == 204:
        print("No data returned.")
    elif response.status_code == 400:
        print("Bad request. Invalid parameters provided in the call.")
    elif response.status_code == 500:
        print("Internal server error.")
    else:
        print(f"Unexpected status code: {response.status_code}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ntuaflix CLI")
    parser.add_argument("scope", choices=["healthcheck"])
   # parser.add_argument("--filename", help="Specify filename for newtitles scope")
   # parser.add_argument("--titleID", help="Specify titleID for title scope")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Specify output format")

    args = parser.parse_args()

    if args.scope == "healthcheck":
        healthcheck(args)