import subprocess 

cli_script = "./cli-client/cli.py"


def test_healthcheck(): 
    function = "healthcheck" #function you want to test
    filename = "" #add the path to the tsv file 
    format_option = "json" #json or csv
    try: 
        result = subprocess.run(
            ["python", cli_script, function], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        assert result.returncode == 0
        assert "Status Code 200" in result.stdout
        print("Functional Test passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test failed: {e.stderr}")

def test_newtitles(): 
    function = "newtitles" #function you want to test
    filename = "./back-end/db/data/truncated_title.basics.tsv" #add the path to the tsv file 
    format_option = "json"

    try: 
        result = subprocess.run(
            ["python", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case  failed: {format_option} is not supported")
            elif not filename.lower().endswith(".tsv"): 
                print(f"File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Error: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case failed: {result.stdout}")
            return
        print("Functional Test Case passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case  failed: {e.stderr}")

def test_newakas(): 
    function = "newakas" #function you want to test
    filename = "./back-end/db/data/truncated_title.akas.tsv" #add the path to the tsv file 
    format_option = "json"

    try: 
        result = subprocess.run(
            ["python", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case  failed: {format_option} is not supported")
            elif not filename.lower().endswith(".tsv"): 
                print(f"File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Error: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case failed: {result.stdout}")
            return
        print("Functional Test Case passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case failed: {e.stderr}")


if __name__ == "__main__": 
    test_healthcheck()
    test_newtitles()
    test_newakas()
