import duckdb
from typing import Any
from broai.duckdb_management.utils import get_create_table_query, get_where_statement, get_batch_update_query
import pandas as pd

class DuckStore:
    def __init__(self, db, table, schemas):
        self.db = db
        self.table = table
        self.schemas = schemas

    def sql(self, query:str)->None:
        with duckdb.connect(self.db) as conn:
            conn.sql(query)
    
    def sql_df(self, query:str)->pd.DataFrame:
        with duckdb.connect(self.db) as conn:
            return conn.sql(query).df()

    def delete_table(self)->None:
        query = f"""DELETE FROM {self.table};"""
        self.sql(query)

    def drop_table(self)->None:
        query = f"""DROP TABLE {self.table};"""
        self.sql(query)

    def create_table(self)->None:
        query = get_create_table_query(table=self.table, schemas=self.schemas)
        self.sql(query)