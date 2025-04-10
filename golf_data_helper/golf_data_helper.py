import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError
import json
import logging
import ast
import sys
from datetime import datetime

from os import environ

class GolfData:
    def __init__(self):
        self.api_key = self.retrieve_api_key()
        self.tournament_id = str(environ["tournament_id"])
        self.leaderboard_data = {}
        self.tournament_data = {}
        self.s3_client = boto3.client("s3")
        self.logger = logging.getLogger("Golf Data Logger")
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        logging.basicConfig()
    
    def retrieve_api_key(self):
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
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)
        else:
            secret_dict = ast.literal_eval(secret_res['SecretString'])
            secret = secret_dict['API_KEY']
            return secret
    
    def load_to_s3(self):
        try:
            existing_file = self.get_existing_filename()
            self.logger.info(f"Deleting {existing_file} from S3")
            self.s3_client.delete_object(Bucket="golfpickem-bucket", Key=existing_file)
            self.logger.info(f"Uploading golf_tournament_data_{self.timestamp}.json to S3")
            self.s3_client.upload_file(Filename=f"/tmp/golf_tournament_data_{self.timestamp}.json", Bucket="golfpickem-bucket", Key=f"golf_tournament_data{self.timestamp}.json")
        except Exception as e:
            self.logger.error(f"File Upload Error: {e}")
            raise Exception from e
        
    def check_data(self):
        file_name = self.get_existing_filename()
        print(file_name)
        cur_data = self.download_file(file_name)
        try:
            if cur_data["results"]["tournament"]["live_details"]["status"] in ["endofday", "completed"] and cur_data["results"]["tournament"]["id"] == self.tournament_id:
                self.logger.info("Tournament is end of Day - No Data to Pull")
                sys.exit(0)
        except Exception as e:
            self.logger.info(f"Error Checking Existing Data: {e}")

    def download_file(self, file_name):
        try:
            response = self.s3_client.get_object(Bucket="golfpickem-bucket", Key=file_name)
            return response
        except Exception as e:
            print(e)
            self.logger.error(e)
            raise Exception from e

    def create_json_file(self):
        with open(f"/tmp/golf_tournament_data_{self.timestamp}.json", "w+") as f:
            json.dump(self.golf_data, f)
    
    def get_existing_filename(self):
        files = self.s3_client.list_objects_v2(Bucket="golfpickem-bucket", Prefix="golf_tournament_data")
        return files["Contents"][0]["Key"]
    
    def runner(self):
        self.logger.info("Starting Process")
        self.logger.info("Checking Existing Data")
        
        self.check_data()
        self.logger.info("Data Requires Update - Executing Data Pull")

        url = f"https://golf-leaderboard-data.p.rapidapi.com/leaderboard/{self.tournament_id}"


        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com"
        }
        try:
            response = requests.request("GET", url, headers=headers)
            self.logger.info(f"API RESPONSE: {response.status_code}")
            self.golf_data = response.json()
        except HTTPError as httpe:
            print(f"HTTP ERROR: {httpe.args[0]} - Full Log: {httpe}")
        except ConnectionError as conne:
            print(f"Connection Error: {conne}")
        except RequestException as reqe:
            print(f"Request Exception: {reqe}")
            raise Exception from reqe
        self.create_json_file()
        try:
            self.load_to_s3()
            self.logger.info(f"S3 Upload Success")
            return True
        except Exception as e:
            print(e)
            raise Exception from e 
    
def lambda_handler(event, context):
    data_client = GolfData()
    data_client.runner()
    print("Lambda Function Complete")

# if __name__ == "__main__":
#     data_client = GolfData()
#     data_client.runner()
