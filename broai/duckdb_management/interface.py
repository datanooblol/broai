import duckdb
from typing import Any, Literal, List, Dict, Optional, Tuple
from broai.duckdb_management.utils import get_create_table_query, get_select_query, get_insert_query, get_batch_update_query, get_delete_query
import pandas as pd
import os

class DuckStoreInterface:
    def __init__(self, db_name:str, table:str, schemas:dict):
        self.db_name = db_name
        self.table = table
        self.__schemas = schemas

    def show_schemas(self)->Dict[str, Any]:
        return self.__schemas
    
    def sql(self, query:str)->None:
        with duckdb.connect(self.db_name) as conn:
            conn.sql(query)
    
    def sql_df(self, query:str)->pd.DataFrame:
        with duckdb.connect(self.db_name) as conn:
            return conn.sql(query).df()

    def executemany(self, query, rows:List[Tuple[Any]]):
        with duckdb.connect(self.db_name) as con:
            con.executemany(query, rows)
    
    def delete_table(self)->None:
        query = f"""DELETE FROM {self.table};"""
        self.sql(query)

    def drop_table(self)->None:
        query = f"""DROP TABLE {self.table};"""
        self.sql(query)

    def create_table(self)->None:
        query = get_create_table_query(table=self.table, schemas=self.show_schemas())
        self.sql(query)

    def remove_database(self, confirm:str=None)->None:
        if confirm == f"remove {self.db_name}":
            os.remove(self.db_name)
            return
        print(f"If you want to remove database, use confirm 'remove {self.db_name}'")

    def add(self, fields:List[str], data:str):
        query = get_insert_query(table=self.table, fields=fields, data=data)
        self.sql(query)

    def read(self, fields:List[str]=None, where:Optional[str]=None)->None:
        if fields is None:
            fields = ["*"]
        query = get_select_query(table=self.table, fields=fields, where=where)
        return self.sql_df(query)

    def update(self, schemas:Dict[str, Any], data:str, ref_keys:List[str])->None:
        query = get_batch_update_query(table=self.table, schemas=schemas, data=data, ref_keys=ref_keys)
        self.sql(query)

    def delete(self, where_condition:str)->None:
        query = get_delete_query(table=self.table, where_condition=where_condition)
        self.sql(query)