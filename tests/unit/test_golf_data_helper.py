import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from golf_data_helper.golf_data_helper import GolfData
from os import environ

class MockBotoS3:
    def __init__(self):
        self.status_code = 200
    def upload_file(self, **kwargs):
        return 200
    def get_object(self, **kwargs):
        return 200
    
class TestGolfDataHelper(TestCase):
    def setUp(self):
        environ["API_KEY"] = "fakekey"
        environ["tournament_id"] = "1"
        self.golf_data_client = GolfData()

    # @patch("requests.request", return_value=None)
    # @patch("golf_data_helper.golf_data_helper.GolfData._create_json_file", return_value=None)
    # @patch("golf_data_helper.golf_data_helper.GolfData._load_to_s3", return_value=200)
    # def test_runnner(self, mock_s3, mock_json, mock_requests):
    #     retval = self.golf_data_client.runner()
    #     self.assertEqual(retval, 200)
    
    @patch("boto3.client", return_value=MockBotoS3())
    def test_load_s3(self, mock_s3):
        self.golf_data_client.s3_client = mock_s3
        retval = self.golf_data_client._load_to_s3()
        self.assertEqual(mock_s3.call_count, 1)