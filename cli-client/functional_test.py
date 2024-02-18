import subprocess 

cli_script = "./cli-client/cli.py"

def test_healthcheck(): 
    function = "healthcheck" #function you want to test
    filename = "" #add the path to the tsv file 
    format_option = "json" #json or csv
    try: 
        result = subprocess.run(
            ["python3", cli_script, function], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        assert result.returncode == 0
        assert "Status Code 200" in result.stdout
        print("Functional Test passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test failed: {e.stderr}")


def test_newtitles(filename, format_option): 
    function = "newtitles" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newtitles' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newtitles' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newtitles' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newtitles' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newtitles' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newtitles' failed: {result.stdout}")
            return
        print("Functional Test Case 'newtitles' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newtitles' failed: {e.stderr}")


def test_newakas(filename, format_option): 
    function = "newakas" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newakas' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newakas' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newakas' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newakas' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newakas' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newakas' failed: {result.stdout}")
            return
        print("Functional Test Case 'newakas' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newakas' failed: {e.stderr}")


def test_newnames(filename, format_option): 
    function = "newnames" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newnames' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newnames' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newnames' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newnames' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newnames' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newnames' failed: {result.stdout}")
            return
        print("Functional Test Case 'newnames' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newnames' failed: {e.stderr}")


def test_newcrew(filename, format_option): 
    function = "newcrew" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newcrew' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newcrew' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newcrew' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newcrew' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newcrew' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newcrew' failed: {result.stdout}")
            return
        print("Functional Test Case 'newcrew' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newcrew' failed: {e.stderr}")


def test_newepisode(filename, format_option): 
    function = "newepisode" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newepisode' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newepisode' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newepisode' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newepisode' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newepisode' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newepisode' failed: {result.stdout}")
            return
        print("Functional Test Case 'newepisode' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newepisode' failed: {e.stderr}")


def test_newprincipals(filename, format_option): 
    function = "newprincipals" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newprincipals' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newprincipals' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newprincipals' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newprincipals' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newprincipals' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newprincipals' failed: {result.stdout}")
            return
        print("Functional Test Case 'newprincipals' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newprincipals' failed: {e.stderr}")


def test_newratings(filename, format_option): 
    function = "newratings" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--filename", filename, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test Case 'newratings' failed: {format_option} is not supported")
            elif filename == "" :
                if "expected one argument" not in result.stderr: 
                    print("Functional Test Case for parameters in 'newratings' passed")
                else:
                    print(f"Functional Test Case for parameters in 'newratings' failed: {e.stderr}")
            elif not filename.lower().endswith(".tsv"): 
                print(f"Functional Test Case 'newratings' failed: File '{filename}' is wrong")
            elif f"Error: File '{filename}' does not exist" in result.stdout: 
                print(f"Functional Test Case 'newratings' failed: File '{filename}' does not exist")
            else: 
                print(f"Functional Test Case 'newratings' failed: {result.stdout}")
            return
        print("Functional Test Case 'newratings' passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test Case 'newratings' failed: {e.stderr}")


if __name__ == "__main__": 
    #test_healthcheck()

    print("------------Functional Testing for 'newtitles' scope------------\n")
    #Correct File For the First Time
    test_newtitles('./back-end/db/data/truncated_title.basics.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newtitles('./back-end/db/data/truncated_title.basics.tsv', 'json')
    #Wrong File Name
    test_newtitles('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newtitles('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newtitles('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newakas' scope------------\n")
    #Correct File For the First Time
    test_newakas('./back-end/db/data/truncated_title.akas.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newakas('./back-end/db/data/truncated_title.akas.tsv', 'json')
    #Wrong File Name
    test_newakas('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newakas('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newakas('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newnames' scope------------\n")
    #Correct File For the First Time
    test_newnames('./back-end/db/data/truncated_name.basics.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newnames('./back-end/db/data/truncated_name.basics.tsv', 'json')
    #Wrong File Name
    test_newnames('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newnames('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newnames('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newcrew' scope------------\n")
    #Correct File For the First Time
    test_newcrew('./back-end/db/data/truncated_title.crew.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newcrew('./back-end/db/data/truncated_title.crew.tsv', 'json')
    #Wrong File Name
    test_newcrew('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newcrew('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newcrew('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newepisode' scope------------\n")
    #Correct File For the First Time
    test_newepisode('./back-end/db/data/truncated_title.episode.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newepisode('./back-end/db/data/truncated_title.episode.tsv', 'json')
    #Wrong File Name
    test_newepisode('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newepisode('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newepisode('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newprincipals' scope------------\n")
    #Correct File For the First Time
    test_newprincipals('./back-end/db/data/truncated_title.principals.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newprincipals('./back-end/db/data/truncated_title.principals.tsv', 'json')
    #Wrong File Name
    test_newprincipals('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newprincipals('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newprincipals('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("------------Functional Testing for 'newratings' scope------------\n")
    #Correct File For the First Time
    test_newratings('./back-end/db/data/truncated_title.ratings.tsv', 'json')
    #Correct File For the Second Time - Duplicate Entries
    test_newratings('./back-end/db/data/truncated_title.ratings.tsv', 'json')
    #Wrong File Name
    test_newratings('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newratings('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newratings('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

