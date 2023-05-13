import boto3
import requests
import json
import logging

from os import environ

class GolfData:
    def __init__(self):
        self.api_key = environ["API_KEY"]
        self.tournament_id = environ["tournament_id"]
        self.leaderboard_data = {}
        self.tournament_data = {}
        self.s3_client = boto3.client("s3")
        self.logger = logging.getLogger("Golf Data Logger")
        
    def _load_to_s3(self):
        try:
            response = self.s3_client.upload_file(Filename="/tmp/golf_tournament_data.json", Bucket="willert-bucket", Key="Projects/GolfPickem/golf_tournament_data.json")
            print(response)
            self.logger.info(response)
            return response 
        except Exception as e:
            print(e)
            self.logger.error(e)
            raise Exception from e
        
    def _download_file(self):
        try:
            response = self.s3_client.get_object(Bucket="willert-bucket", Key="Projects/GolfPickem/golf_tournament_data.json")
        except Exception as e:
            print(e)
            self.logger.error(e)
            raise Exception from e
        return response

    def _create_json_file(self):
        with open(f"/tmp/golf_tournament_data.json", "w+") as f:
            json.dump(self.golf_data, f)
    
    def runner(self):
        url = f"https://golf-leaderboard-data.p.rapidapi.com/leaderboard/{self.tournament_id}"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com"
        }
        try:
            response = requests.request("GET", url, headers=headers)
            self.logger.info(f"API RESPONSE: {response.status_code}")
            self.golf_data = response.json()
        except Exception as e:
            raise Exception from e
        self._create_json_file()
        try:
            s3_response = self._load_to_s3()
            self.logger.info(f"S3 Client RESPONSE: {s3_response}")
            return s3_response
        except Exception as e:
            raise Exception from e 
    
def lambda_handler(event, context):
    data_client = GolfData()
    data_client.runner()
    return "Complete"

# if __name__ == "__main__":
#     data_client = GolfData()
#     data_client.runner()
