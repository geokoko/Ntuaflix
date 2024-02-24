import unittest, requests, argparse, json
from unittest.mock import patch
import cli 
BASE_URL = "https://0.0.0.0:9876/ntuaflix_api"

#the basis of the unit test is that we are mocking the HTTP requests made (both get and post) and they are not really executed

#testing the upload endpoint for new titles
class TestHealthcheck (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.get")
    def test_healthcheck(self, mock_get): 

        #pass the corresponding arguments
        args = argparse.Namespace(format="json")

        #call the function
        cli.healthcheck(args)

        #verify that the correct URL was called
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/admin/healthcheck",
           params={"format": args.format},
           verify = False
        )

class TestResetAll (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_resetall(self, mock_post): 

        #pass the corresponding arguments
        args = argparse.Namespace(format="json")

        #call the function
        cli.resetall(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/resetall",
            params={"format": args.format},
            verify = False
        )

#testing the upload endpoint for akas titles
class TestNewAkas (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newakas(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.akas.tsv"

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newakas(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titleakas",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
           verify = False
        )

#testing the upload endpoint for new people
class TestNewNames (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newnames(self, mock_post): 
        filename = "./back-end/db/data/truncated_name.basics.tsv"

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newnames(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/namebasics",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
              verify = False
        )

#testing the upload endpoint for new crew (directors, writers)
class TestNewCrew (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newcrew(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.crew.tsv"        

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newcrew(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titlecrew",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
                verify = False
        )

#testing the upload endpoint for new episodes
class TestNewEpisodes (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newepisodes(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.episode.tsv"
        #determine the status code and the output text that we are expecting here
        

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newepisode(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titleepisode",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
                verify = False
        )

#testing the upload endpoint for new principals
class TestNewNames (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newprincipals(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.principals.tsv"
        #determine the status code and the output text that we are expecting here
        

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newprincipals(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titleprincipals",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
                verify = False
        )

#testing the upload endpoint for new ratings
class TestNewRatings (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_newratings(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.ratings.tsv"
        #determine the status code and the output text that we are expecting here
        

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newratings(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titleratings",
           files=mock_post.mock_calls[0][2]['files'],
           params=mock_post.mock_calls[0][2]['params'],
                verify = False
        )

#testing the endpoint for returning a title
class TestTitle (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.get")
    def test_title(self, mock_get): 
        #pass the corresponding arguments
        title_ID = input("Enter titleID: ")
        args = argparse.Namespace(titleID = title_ID, format="json")

        #call the function
        cli.title(args)


        #verify that the correct URL was called
        mock_get.assert_called_once_with(
           f"{cli.BASE_URL}/title/{args.titleID}",
           params={"format": args.format},
              verify = False
        )

#testing the endpoint for searching a title
class TestSearchTitle (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.get")
    def test_search_title(self, mock_get): 
        #pass the corresponding arguments
        title = input("Enter title: ")
        args = argparse.Namespace(titlepart = title, format="csv")

        #call the function
        cli.searchtitle(args)


        #verify that the correct URL was called
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/searchtitle",
            data=json.dumps({"titlePart": title}),
            headers={'Content-Type': 'application/json'},
            params={"format": args.format},
                verify = False
        )


#test the endpoint for returning specific name
class TestName (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.get")
    def test_bygenre(self, mock_get): 
        #pass the corresponding arguments
        name_id = ""
        args = argparse.Namespace(nameid = name_id, format="csv")

        #call the function
        cli.name(args)

        #verify that the correct URL was called
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/name/{name_id}",
            params={"format": args.format},
                verify = False
        )

#testing the endpoint for searching a title
class TestSearchName (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.get")
    def test_search_name(self, mock_get): 
        #pass the corresponding arguments
        name = ""
        args = argparse.Namespace(name = name, format="csv")

        #call the function
        cli.searchname(args)

        #verify that the correct URL was called
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/searchname",
            data=json.dumps({"namePart": name}),
            headers={'Content-Type': 'application/json'},
            params={"format": args.format},
                verify = False
        )



if __name__ == "__main__": 
    unittest.main()
