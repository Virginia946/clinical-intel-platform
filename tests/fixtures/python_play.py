import pandas as pd
from dotenv import load_dotenv
from ingestion.warehouse import Warehouse

load_dotenv()
wh = Warehouse()

df = pd.DataFrame({"patient_id": ["p1", "p2"], "gender": ["female", "male"]})
replace=True
print(wh.execute("SELECT * FROM raw.test_patients"))
