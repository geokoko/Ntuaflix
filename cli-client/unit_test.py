import unittest, requests, argparse
from unittest.mock import patch
import cli 
BASE_URL = "http://127.0.0.1:9876/ntuaflix_api"

#the basis of the unit test is that we are mocking the HTTP requests made (both get and post) and they are not really executed

class TesstHealthcheck (unittest.TestCase): 
    
    #determine whether the request is post or get
    @patch("requests.post")
    def test_successful_newtitles(self, mock_post): 
        filename = "./back-end/db/data/truncated_title.basics.tsv"
        #determine the status code and the output text that we are expecting here
        

        #pass the corresponding arguments
        args = argparse.Namespace(filename=filename, format="json")

        #call the function
        cli.newtitles(args)

        #verify that the correct URL was called
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/admin/upload/titlebasics",
           files=mock_post.mock_calls[0][2]['files']
        )

if __name__ == "__main__": 
    unittest.main()