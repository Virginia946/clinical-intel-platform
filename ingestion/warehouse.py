# thid code connect the Warehouse to DuckDB

import os

import pandas as pd


class Warehouse:
    """Writes DataFrames to the RAW layer of Snowflake or DuckDB."""

    def __init__(self):
        self.backend = os.getenv("WAREHOUSE_BACKEND", "snowflake")
        if self.backend == "snowflake":
            import snowflake.connector
            self.conn = snowflake.connector.connect(
                account=os.environ["SNOWFLAKE_ACCOUNT"],
                user=os.environ["SNOWFLAKE_USER"],
                private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_FILE"],
                role=os.environ["SNOWFLAKE_ROLE"],
                warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
                database=os.environ["SNOWFLAKE_DATABASE"],
                schema="RAW",
            )
        else:
            import duckdb
            self.conn = duckdb.connect(os.getenv("DUCKDB_PATH", "data/clinical.duckdb"))
            self.conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

    def execute(self, sql: str, params: tuple = ()):
        if self.backend == "duckdb":
            sql = sql.replace("%s", "?")
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall() if cur.description else []

    def write(self, df: pd.DataFrame, table: str, replace: bool = False) -> int:
        df = df.copy()
        df.columns = [c.upper() for c in df.columns]
        table = table.upper()
        if self.backend == "snowflake":
            from snowflake.connector.pandas_tools import write_pandas
            write_pandas(self.conn, df, table, auto_create_table=True,
                         overwrite=replace, quote_identifiers=False)
        else:
            self.conn.register("incoming", df)
            if replace:
                self.conn.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM incoming")
            else:
                self.conn.execute(f"CREATE TABLE IF NOT EXISTS raw.{table} AS SELECT * FROM incoming WHERE 1 = 0")
                self.conn.execute(f"INSERT INTO raw.{table} BY NAME SELECT * FROM incoming")
            self.conn.unregister("incoming")
        return len(df)