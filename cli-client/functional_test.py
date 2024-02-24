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
        print("Functional Test HealthCheck passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test failed: {e.stderr}")

def test_resetall(): 
    function = "resetall" #function you want to test
    try: 
        result = subprocess.run(
            ["python3", cli_script, function], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code 
        )
        print(result.stdout)
        assert result.returncode == 0
        #assert "Status Code 200" in result.stdout
        print("Functional Test ResetAll passed")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test failed: {e.stderr}")

def test_title(titleID, format_option): 
    function = "title" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--titleID", titleID, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 204" in result.stdout: 
            print("Functional Test 'Title' passed, with no titles returned")
            return
        elif "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test 'Title'  failed: {format_option} is not supported") 
            else: 
                print(f"Functional Test 'Title' failed: {result.stdout}")
            return
        print(f"Functional Test 'Title' passed, with the following titles: {result.stdout}")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test 'Title' failed: {e.stderr}")

def test_searchtitle(titlepart, format_option): 
    function = "searchtitle" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--titlepart", titlepart, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )    
        if "Status Code 204" in result.stdout: 
            print("Functional Test 'searchtitle' passed, with no titles returned")
            return
        elif "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test 'searchtitle'  failed: format option '{format_option}' is not supported") 
            else: 
                print(f"Functional Test 'searchtitle' failed: {result.stdout}")
            return
        print(f"Functional Test 'searchtitle' passed, with some titles returned")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test 'searchtitle' failed: {e.stderr}")

def test_bygenre(genre, minrating, year_from, to, format_option): 
    function = "bygenre" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--genre", genre, "--min", minrating, "--from", year_from,"--to", to, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )    
        if "Status Code 204" in result.stdout: 
            print("Functional Test 'bygenre' passed, with no titles returned")
            return
        elif "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test 'bygenre'  failed: format option '{format_option}' is not supported") 
            else: 
                print(f"Functional Test 'bygenre' failed: {result.stdout}")
            return
        print(f"Functional Test 'bygenre' passed, with some titles returned")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test 'bygenre' failed: {e.stderr}")

def test_name(nameID, format_option): 
    function = "name" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--nameid", nameID, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )
        if "Status Code 204" in result.stdout: 
            print("Functional Test 'name' passed, with no names returned")
            return
        elif "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                 print(f"Functional Test 'name'  failed: {format_option} is not supported") 
            else: 
                 print(f"Functional Test 'name' failed: {result.stdout}")
            return
        print(f"Functional Test 'name' passed, with the following names: {result.stdout}")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test 'name' failed: {e.stderr}")

def test_searchname(name, format_option): 
    function = "searchname" #function you want to test

    try: 
        result = subprocess.run(
            ["python3", cli_script, function, "--name", name, "--format", format_option], 
            capture_output=True,
            text=True, #set to true in order to return stdout as strings, not as binary
            check=False, #when check is set to true, if exit code is not 0, an exception is raised. We set it to false, in order to check exit code
        )    
        if "Status Code 204" in result.stdout: 
            print("Functional Test 'searchname' passed, with no names returned")
            return
        elif "Status Code 200" not in result.stdout: 
            if not format_option == "json" or format_option == "csv":
                print(f"Functional Test 'searchname'  failed: format option '{format_option}' is not supported") 
            else: 
                print(f"Functional Test 'searchname' failed: {result.stdout}")
            return
        print(f"Functional Test 'searchname' passed, with some names returned")
    except subprocess.CalledProcessError as e: 
        print(f"Functional Test 'searchname' failed: {e.stderr}")


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
    test_healthcheck()

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
    #Correct File
    test_newratings('./back-end/db/data/truncated_title.ratings.tsv', 'json')
    #Wrong File Name
    test_newratings('./back-end/db/data/truncated_wrong_file.tsv', 'json')
    #Wrong File Type
    test_newratings('./back-end/db/data/truncated_wrong_file.ts', 'json')
    #Wrong Format
    test_newratings('./back-end/db/data/truncated_wrong_file.ts', 'xml')
    print()

    print("----------------------------FUNCTIONAL TESTING FOR RESET ALL-----------------------------------------------------------")
    test_resetall()
    
    print("----------------------------FUNCTIONAL TESTING FOR TITLE---------------------------------------------------------------")
    test_title(titleID="", format_option="")
    print("----------------------------FUNCTIONAL TESTING FOR SEARCHING TITLES----------------------------------------------------")
    test_searchtitle(titlepart="hen", format_option="json")
    test_searchtitle(titlepart="hen", format_option="xml")
    test_searchtitle(titlepart="wrongggggg", format_option="json")
    print("----------------------------FUNCTIONAL TESTING FOR SEARCHING BY GENRE--------------------------------------------------")
    test_bygenre(genre="horror", minrating="4.0", year_from="1991", to="2005", format_option="json")
    test_bygenre(genre="comedy", minrating="3.0", year_from="2005", to="2010", format_option="xml")
    test_bygenre(genre="comedy", minrating="3.0", year_from="2005", to="2010", format_option="json")
    print("----------------------------FUNCTIONAL TESTING FOR NAME----------------------------------------------------------------")
    test_name(nameID="nm0000019", format_option="json")
    test_name(nameID="nm0000019", format_option="xml")
    test_name(nameID="nm00000", format_option="json")
    print("----------------------------FUNCTIONAL TESTING FOR SEARCHING NAMES-----------------------------------------------------")
    test_searchname(name="nale", format_option="json")
    test_searchname(name="nale", format_option="xml")
    test_searchname(name="nalll", format_option="json")

