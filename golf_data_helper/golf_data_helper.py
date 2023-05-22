import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError
import json
import logging
import ast

from os import environ

class GolfData:
    def __init__(self):
        self.api_key = self._retrieve_api_key()
        self.tournament_id = str(environ["tournament_id"])
        self.leaderboard_data = {}
        self.tournament_data = {}
        self.s3_client = boto3.client("s3")
        self.logger = logging.getLogger("Golf Data Logger")
    
    def _retrieve_api_key(self):
        secret_name = "golfpickem/api_key"
        secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
        try:
            secret_res = secrets_client.get_secret_value(
                SecretId=secret_name,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                print("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)
        else:
            secret_dict = ast.literal_eval(secret_res['SecretString'])
            secret = secret_dict['API_KEY']
            return secret
    
    def _load_to_s3(self):
        try:
            response = self.s3_client.upload_file(Filename="/tmp/golf_tournament_data.json", Bucket="golfpickem-bucket", Key="golf_tournament_data.json")
            print(response)
            self.logger.info(response)
            return response 
        except Exception as e:
            print(e)
            self.logger.error(e)
            raise Exception from e
        
    def _download_file(self):
        try:
            response = self.s3_client.get_object(Bucket="golfpickem-bucket", Key="golf_tournament_data.json")
        except Exception as e:
            print(e)
            self.logger.error(e)
            raise Exception from e
        return response

    def _create_json_file(self):
        with open(f"/tmp/golf_tournament_data.json", "w+") as f:
            json.dump(self.golf_data, f)
    
    def runner(self):
        print("Starting Data Pull")
        # self.logger.info("Starting Data Pull")
        url = f"https://golf-leaderboard-data.p.rapidapi.com/leaderboard/{self.tournament_id}"


        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com"
        }
        try:
            response = requests.request("GET", url, headers=headers)
            print(f"API RESPONSE: {response.status_code}")
            # self.logger.info(f"API RESPONSE: {response.status_code}")
            self.golf_data = response.json()
        except HTTPError as httpe:
            print(f"HTTP ERROR: {httpe.args[0]} - Full Log: {httpe}")
        except ConnectionError as conne:
            print(f"Connection Error: {conne}")
        except RequestException as reqe:
            print(f"Request Exception: {reqe}")
            raise Exception from reqe
        self._create_json_file()
        try:
            s3_response = self._load_to_s3()
            print(f"S3 Client RESPONSE: {s3_response}")
            # self.logger.info(f"S3 Client RESPONSE: {s3_response}")
            return s3_response
        except Exception as e:
            print(e)
            raise Exception from e 
    
def lambda_handler(event, context):
    data_client = GolfData()
    data_client.runner()
    return "Complete"

if __name__ == "__main__":
    data_client = GolfData()
    data_client.runner()
