from unittest import TestCase
from unittest.mock import patch, mock_open
from golf_data_helper.golf_data_helper import GolfData, lambda_handler
from os import environ

class MockBotoS3:
    def __init__(self):
        self.status_code = 200
    def upload_file(self, **kwargs):
        return 200
    def get_object(self, **kwargs):
        return 200
    
class MockRequest:
    def __init__(self):
        self.status_code = 200
    def json(self):
        return [{"foo": "bar"}]
    
class TestGolfDataHelper(TestCase):
    def setUp(self):
        environ["API_KEY"] = "fakekey"
        environ["tournament_id"] = "1"
        self.golf_data_client = GolfData()

    @patch("requests.request", return_value=MockRequest())
    @patch("golf_data_helper.golf_data_helper.GolfData.create_json_file", return_value=None)
    @patch("golf_data_helper.golf_data_helper.GolfData.load_to_s3", return_value=200)
    def test_runnner(self, mock_s3, mock_json, mock_requests):
        retval = self.golf_data_client.runner()
        self.assertEqual(retval, 200)
    
    @patch("boto3.client", return_value=MockBotoS3())
    def test_load_s3(self, mock_s3):
        self.golf_data_client.s3_client = mock_s3
        retval = self.golf_data_client.load_to_s3()
        self.assertEqual(mock_s3.upload_file.call_count, 1)

    @patch("boto3.client", return_value=MockBotoS3())
    def test_load_s3(self, mock_s3):
        self.golf_data_client.s3_client = mock_s3
        retval = self.golf_data_client.load_to_s3()
        self.assertEqual(mock_s3.upload_file.call_count, 1)

    @patch("golf_data_helper.golf_data_helper.GolfData")
    def test_handler(self, mock_class):
        retval = lambda_handler({}, None)
        self.assertEqual(retval, "Complete")

    @patch('builtins.open', mock_open(read_data="1"))
    def test_create_json_file(self):
        self.golf_data_client.golf_data = [{"foo": "bar"}]
        retval = self.golf_data_client.create_json_file()
        open.assert_called_with("/tmp/golf_tournament_data.json", "w+")
        self.assertEqual(retval, None)