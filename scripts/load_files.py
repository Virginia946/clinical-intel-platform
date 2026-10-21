import os 
from dotenv import load_dotenv

load_dotenv()
print(os.environ["LANDING_BUCKET"])
print(os.environ["S3_ENDPOINT"]) 
