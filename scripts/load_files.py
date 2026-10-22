import os 
from dotenv import load_dotenv
import boto3
load_dotenv()


#connect to client adresse 
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
)
#create bucket and print 
s3.create_bucket(Bucket=os.environ["LANDING_BUCKET"])
print(s3.list_buckets()["Buckets"])




