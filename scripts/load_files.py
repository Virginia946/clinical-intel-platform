import os 
from dotenv import load_dotenv
import boto3
import datetime
import pathlib
load_dotenv()


#connect to client adresse 
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
)


bucket = os.environ["LANDING_BUCKET"]



#create bucket if the one given does not exist 
names = []
for b in s3.list_buckets()["Buckets"]:
    names.append(b["Name"])

if bucket not in names:
    s3.create_bucket(Bucket=bucket)
    print("created bucket:",bucket)
else:
    print("Bucket already exists:", bucket)

#upload payers  and claims to minIo
run = datetime.date.today().isoformat()
billing_files = [
    "data/synthea/output/csv/claims.csv",
    "data/synthea/output/csv/payers.csv",
]
print(len(billing_files))
for path in billing_files:
    name = pathlib.Path(path).name
    key = f"billing/{run}/{name}"
    s3.upload_file(path, bucket, key)
    print("Uploaded", key)


cms_files = list(pathlib.Path("data/cms").glob("*.csv"))
print(cms_files)