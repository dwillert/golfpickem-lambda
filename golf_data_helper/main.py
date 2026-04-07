"""Main entry point for Golf Data Helper Lambda function."""
from datetime import datetime
import json
from pathlib import Path
import os
import logging
from golf_data_helper.clients.espn import ESPNClient
from golf_data_helper.clients.s3 import S3Client

logger = logging.getLogger("Golf Data Logger")

# def load_to_s3():
#     try:
#         existing_file = self.get_existing_filename()
#         logger.info(f"Deleting {existing_file} from S3")
#         s3_client.delete_object(Bucket="golfpickem-bucket", Key=existing_file)
#         logger.info(f"Uploading golf_tournament_data_{self.timestamp}.json to S3")
#         s3_client.upload_file(Filename=f"/tmp/golf_tournament_data_{self.timestamp}.json", Bucket="golfpickem-bucket", Key=f"golf_tournament_data{self.timestamp}.json")
#     except Exception as e:
#         self.logger.error(f"File Upload Error: {e}")
#         raise Exception from e
    
# def check_data(self):
#     file_name = self.get_existing_filename()
#     cur_data = self.download_file(file_name)
#     try:
#         if cur_data["results"]["tournament"]["live_details"]["status"] in ["endofday", "completed"] and cur_data["results"]["tournament"]["id"] == self.tournament_id:
#             self.logger.info("Tournament is end of Day - No Data to Pull")
#             sys.exit(0)
#     except Exception as e:
#         self.logger.info(f"Error Checking Existing Data: {e}")

# def download_file(self, file_name):
#     try:
#         response = self.s3_client.get_object(Bucket="golfpickem-bucket", Key=file_name)
#         return response
#     except Exception as e:
#         print(e)
#         self.logger.error(e)
#         raise Exception from e

def create_json_file(data: dict) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_file_path = f"/tmp/golf_tournament_data_{timestamp}.json"
    with open(tmp_file_path, "w+") as f:
        json.dump(data, f)
    return tmp_file_path


def lambda_handler(event, context):
    s3 = S3Client()
    latest_file_name = s3.get_existing_filename()
    # latest_data = s3.download_file(latest_file_name)
    #todo add live details to espn payload

    tournament_id = os.getenv("tournament_id", "401703504")
    golf_data = ESPNClient.get_golf_data(tournament_id=tournament_id)

    logger.info("Data retrieved from ESPN API. Uploading to S3...")
    s3.delete_object(key=latest_file_name)
    tmp_file_path = create_json_file(golf_data)
    s3.upload_file(filename=tmp_file_path, key=f"golf_tournament_data{datetime.now().strftime('%Y%m%d%H%M%S')}.json")

    return {"statusCode": 200, "body": f"Hello from Golf Data Helper! Got data for tournament ID: {tournament_id}"}