import glob, os
import requests
from dotenv import load_dotenv

load_dotenv()
BASE = os.environ["FHIR_BASE_URL"]

files = sorted(glob.glob("data/synthea/output/fhir/*.json"))
shared = [f for f in files if "hospitalInformation" in f or "practitionerInformation" in f]
patients = [f for f in files if f not in shared]

session = requests.Session()
session.headers["Content-Type"] = "application/fhir+json"
failed = []
for i, path in enumerate(shared + patients, 1):
    with open(path, "rb") as fh:
        r = session.post(BASE, data=fh, timeout=300)
    if r.status_code >= 300:
        failed.append((path, r.status_code, r.text[:200]))
    if i % 10 == 0:
        print(f"{i}/{len(files)} files loaded")

print(f"Done with {len(failed)} failures")
for f in failed:
    print(f)