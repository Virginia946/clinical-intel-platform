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

    # {raw_table: [columns that must be present]}
    required_columns: dict[str, list[str]] = {}

    def __init__(self, warehouse: Warehouse):
        self.wh = warehouse

    @abstractmethod
    def extract(self) -> dict[str, pd.DataFrame]:
        """Return {raw_table_name: DataFrame of text columns}."""
        pass

    def validate(self, table: str, df: pd.DataFrame) -> None:
        if df.empty:
            return  # An incremental run with nothing new is fine.

        missing = set(self.required_columns.get(table, [])) - set(df.columns)

        if missing:
            raise DataQualityError(
                f"{self.name}.{table}: missing columns {sorted(missing)}"
            )

    def run(self) -> dict[str, int]:
        batch = uuid.uuid4().hex
        started = dt.datetime.now(dt.timezone.utc)
        counts = {}

        try:
            for table, df in self.extract().items():
                self.validate(table, df)

                if df.empty:
                    counts[table] = 0
                    continue

                df = df.assign(
                    batch_id=batch,
                    source=self.name,
                    loaded_at=started.isoformat(),
                )

                counts[table] = self.wh.write(df, table)

            self._log(batch, started, "success", counts)
            return counts

        except Exception as exc:
            self._log(batch, started, "failed", counts, str(exc)[:1000])
            raise

    def _log(self, batch, started, status, counts, error=""):
        rows = [
            {
                "batch_id": batch,
                "connector": self.name,
                "row_count": str(n),
                "status": status,
                "table_name": table,
                "error": error,
                "started_at": started.isoformat(),
                "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            for table, n in (counts or {"*": 0}).items()
        ]

        self.wh.write(pd.DataFrame(rows), "load_log")

    # Watermarks: remember how far an incremental connector got
    def get_watermark(self) -> str | None:
        self.wh.execute(
            "CREATE TABLE IF NOT EXISTS RAW.WATERMARKS "
            "(CONNECTOR VARCHAR, VALUE VARCHAR)"
        )

        rows = self.wh.execute(
            "SELECT MAX(VALUE) FROM RAW.WATERMARKS WHERE CONNECTOR = %s",
            (self.name,),
        )

        return rows[0][0] if rows else None

    def set_watermark(self, value: str) -> None:
        self.wh.execute(
            "INSERT INTO RAW.WATERMARKS VALUES (%s, %s)",
            (self.name, value),
        )