import io
import os

import boto3
import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to the source (MinIO)
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["MINIO_ROOT_USER"],
    aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
)
bucket = os.environ["LANDING_BUCKET"]

# 2. Read the file's contents into a DataFrame
key = "billing/2026-10-24/payers.csv"
response = s3.get_object(Bucket=bucket, Key=key)
contents = response["Body"].read()
df = pd.read_csv(io.BytesIO(contents), dtype=str)
print(df.head())

# 3. Connect to the warehouse (DuckDB)
conn = duckdb.connect("data/playground.duckdb")
conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

# 4. Write the DataFrame as a table in RAW
conn.register("incoming", df)
conn.execute("CREATE OR REPLACE TABLE raw.billing_payers AS SELECT * FROM incoming")
print(conn.execute("SELECT COUNT(*) FROM raw.billing_payers").fetchall())