"""S3 Client for Data Access Layer Abstraction."""

import json
import boto3
from botocore.exceptions import ClientError

class S3Client:
    def __init__(self, bucket_name="golfpickem-bucket", region_name=None):
        session = boto3.session.Session()
        self.s3 = session.resource("s3", region_name=region_name) if region_name else session.resource("s3")
        self.bucket_name = bucket_name
        self.bucket = self.s3.Bucket(bucket_name)

    def list_objects(self, prefix=""):
        return [obj.key for obj in self.bucket.objects.filter(Prefix=prefix)]

    def get_existing_filename(self, prefix="golf_tournament_data"):
        keys = self.list_objects(prefix=prefix)
        if not keys:
            raise FileNotFoundError(f"No objects found in bucket {self.bucket_name} with prefix '{prefix}'")
        return keys[0]

    def delete_object(self, key):
        try:
            self.bucket.Object(key).delete()
        except ClientError as e:
            raise

    def upload_file(self, filename, key):
        try:
            self.bucket.upload_file(Filename=filename, Key=key)
        except ClientError as e:
            raise

    def download_file(self, key):
        try:
            obj = self.bucket.Object(key)
            response = obj.get()
            return json.load(response["Body"])
        except ClientError as e:
            raise
