# ingestion/base.py
import datetime as dt
import uuid
from abc import ABC, abstractmethod
import pandas as pd
from .warehouse import Warehouse
class DataQualityError(Exception):
pass
class Connector(ABC):
name: str = "base"
# {raw
_
table: [columns that must be present]}
required
columns: dict[str, list[str]] = {}
_
def
init
(self, warehouse: Warehouse):
__
__
self.wh = warehouse
@abstractmethod
def extract(self) -> dict[str, pd.DataFrame]:
"""Return {raw
table
name: DataFrame of text columns}.
_
_
def validate(self, table: str, df: pd.DataFrame) -> None:
if df.empty:
"""
Page 10 of 33
Clinical Intelligence Platform v0.1: Data Platform Build Guide
return # an incremental run with nothing new is fine
missing = set(self.required
_
columns.get(table, [])) - set(df.columns)
if missing:
raise DataQualityError(f"{self.name}.{table}: missing columns
{sorted(missing)}")
def run(self) -> dict[str, int]:
batch, started = uuid.uuid4().hex, dt.datetime.now(dt.timezone.utc)
counts = {}
try:
for table, df in self.extract().items():
self.validate(table, df)
if df.empty:
counts[table] = 0
continue
df = df.assign(
batch
_
_
id=batch, _
source=self.name,
loaded
at=started.isoformat())
_
_
counts[table] = self.wh.write(df, table)
self.
_
log(batch, started,
"success"
, counts)
return counts
except Exception as exc:
self.
_
log(batch, started,
"failed"
, counts, str(exc)[:1000])
raise
def
_
log(self, batch, started, status, counts, error=""):
rows = [{"batch
id": batch,
"connector": self.name,
_
"row
count": str(n),
"status": status,
"table
name": t,
_
"error": error,
_
"started
at": started.isoformat(),
_
"finished
at": dt.datetime.now(dt.timezone.utc).isoformat()}
_
for t, n in (counts or {"*": 0}).items()]
self.wh.write(pd.DataFrame(rows),
"load
_
log")
# Watermarks: remember how far an incremental connector got
def get
watermark(self) -> str | None:
_
self.wh.execute("CREATE TABLE IF NOT EXISTS RAW.WATERMARKS (CONNECTOR
VARCHAR, VALUE VARCHAR)")
rows = self.wh.execute("SELECT MAX(VALUE) FROM RAW.WATERMARKS WHERE
CONNECTOR = %s"
, (self.name,))
return rows[0][0] if rows else None
def set
watermark(self, value: str) -> None:
_
self.wh.execute("INSERT INTO RAW.WATERMARKS VALUES (%s, %s)"
(self.name, value))