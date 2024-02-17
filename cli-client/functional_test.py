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
    filename_1 = "./back-end/db/data/truncated_title.basics.tsv" #add the path to the tsv file 
    filename_2 = "file"
    format_option = "json" #json or csv

    #Test Case 1: Valid file in empty database 
    try: 
        result = subprocess.run(
            ["python", cli_script, function, "--filename", filename_1, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        print(result.stdout)
        assert result.returncode == 0
        assert "Status Code 200" in result.stdout
        print("Functional Test Case 1 passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 1 failed: {e.stderr}")

    #Test Case 2: Invalid filename 
    try: 
        result = subprocess.run(
            ["python", cli_script, function, "--filename", filename_2, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        print(result.stdout)
        assert result.returncode == 0
        assert "Error: File 'file' does not exist" in result.stdout
        print("Functional Test Case 2 passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 2 failed: {e.stderr}")

if __name__ == "__main__": 
    test_newtitles()
