"""Main entry point for Golf Data Helper Lambda function."""
from datetime import datetime
import json
from pathlib import Path
import os
import logging
from golf_data_helper.clients.espn import ESPNClient
from golf_data_helper.clients.s3 import S3Client

logger = logging.getLogger("Golf Data Logger")


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

    tournament_id = os.getenv("tournament_id", "401811940")
    golf_data = ESPNClient.get_golf_data(tournament_id=tournament_id)

    logger.info("Data retrieved from ESPN API. Uploading to S3...")
    if latest_file_name:
        s3.delete_object(key=latest_file_name)
    tmp_file_path = create_json_file(golf_data)
    s3.upload_file(filename=tmp_file_path, key=f"golf_tournament_data{datetime.now().strftime('%Y%m%d%H%M%S')}.json")

    return {"statusCode": 200, "body": f"Hello from Golf Data Helper! Got data for tournament ID: {tournament_id}"}