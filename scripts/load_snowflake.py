import _path  # noqa
import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from clinical_rag.fhir_client import fetch_all
from clinical_rag.documents import code_text, d

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
)

patients = pd.DataFrame([{
    "PATIENT_ID": p["id"],
    "GENDER": p.get("gender"),
    "BIRTH_DATE": p.get("birthDate"),
} for p in fetch_all("Patient")])

conditions = pd.DataFrame([{
    "CONDITION_ID": c["id"],
    "PATIENT_ID": c.get("subject", {}).get("reference", "").split("/")[-1],
    "CONDITION": code_text(c.get("code")),
    "ONSET_DATE": d(c.get("onsetDateTime")),
} for c in fetch_all("Condition")])

for name, df in [("PATIENTS", patients), ("CONDITIONS", conditions)]:
    ok, _, n_rows, _ = write_pandas(conn, df, name, auto_create_table=True, overwrite=True)
    print(f"{name}: loaded={ok} rows={n_rows}")

conn.close()