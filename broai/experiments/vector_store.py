from broai.duckdb_management.utils import get_create_table_query, get_insert_query
from broai.interface import Context
from typing import List, Dict, Any, Literal
import duckdb
import os
import json
from broai.experiments.utils import experiment
from broai.experiments.huggingface_embedding import BaseEmbeddingModel

def validate_baseclass(input_instance, input_name, baseclass):
    if not isinstance(input_instance, baseclass):
        raise TypeError(f"{input_name} must be of type, {baseclass.__name__}. Instead got {type(input_instance)}")
    return input_instance

@experiment
class DuckVectorStore:
    """
    A vector store backed by DuckDB.

    Args:
        db_name (str): Path to the DuckDB file (e.g., './duckmemory.db').
        table (str): Name of the table to store embeddings.
        embedding (BaseEmbeddingModel): An embedding model that implements the `.run()` method.
        limit (int, optional): Default number of top results to return. Defaults to 5.
    """
    def __init__(self, db_name:str, table:str, embedding:BaseEmbeddingModel, limit:int=5):
        self.db_name = db_name
        self.table = table
        self.embedding_model = validate_baseclass(embedding, "embedding", BaseEmbeddingModel)
        self.embedding_size = self.embedding_model.run(["test"]).shape[1]
        self.limit = limit
        self.__schemas = {
            "id": "VARCHAR",
            "context": "VARCHAR",
            "metadata": "JSON",
            "embedding": f"FLOAT[{self.embedding_size}]"
        }
        self.create_table()
    
    def sql(self, query, params:Dict[str, Any]=None):
        with duckdb.connect(self.db_name) as con:
            con.sql(query, params=params)

    def sql_df(self, query, params:Dict[str, Any]=None):
        with duckdb.connect(self.db_name) as con:
            df = con.sql(query, params=params).to_df()
        return df

    def sql_contexts(self, query, params:Dict[str, Any]=None):
        df = self.sql_df(query, params=params)
        if df.shape[0]==0:
            return
        df = df.loc[~df['score'].isna(), ["id", "context", "metadata"]].copy()
        return [Context(id=record["id"], context=record["context"], metadata=json.loads(record["metadata"])) for record in df.to_dict(orient="records")]
    
    def create_table(self,):
        query = get_create_table_query(table=self.table, schemas=self.__schemas)
        self.sql(query)

    def get_schemas(self):
        return self.__schemas

    def vector_search(self, search_query:str, limit:int=5, context:bool=True):
        vector = self.embedding_model.run(sentences=[search_query])[0]
        query = f"""SELECT *, array_cosine_similarity(embedding, $searchVector::FLOAT[{self.embedding_size}]) AS score FROM {self.table} ORDER BY score DESC LIMIT {limit};"""
        if context==False:
            return self.sql_df(query=query, params=dict(searchVector=vector))
        return self.sql_contexts(query=query, params=dict(searchVector=vector))

    def fulltext_search(self, search_query:str, limit:int=5, context:bool=True):
        query = f"""\
        SELECT *
        FROM (
            SELECT *, fts_main_{self.table}.match_bm25(
                id,
                '{search_query}',
                fields := 'context'
            ) AS score
            FROM {self.table}
        ) sq
        ORDER BY score DESC;
        """
        if context==False:
            return self.sql_df(query=query, params=None)
        return self.sql_contexts(query=query, params=None)
    
    def add_contexts(self, contexts:List[Context]):
        id_list = [c.id for c in contexts]
        context_list = [c.context for c in contexts]
        metadata_list = [c.metadata for c in contexts]
        embedding_list = self.embedding_model.run(context_list)
        rows = list(zip(id_list, context_list, metadata_list, embedding_list))
        with duckdb.connect(self.db_name) as con:
            con.executemany(f"INSERT INTO {self.table} (id, context, metadata, embedding) VALUES (?, ?, ?, ?)", rows)
        self.create_fts_index()

    def read(self, ):
        query = f"SELECT * FROM {self.table};"
        return self.sql_df(query)

    def delete_table(self, ):
        query = f"DELETE FROM {self.table};"
        self.sql(query)

    def drop_table(self)->None:
        query = f"""DROP TABLE {self.table};"""
        self.sql(query)

    def remove_database(self, confirm:Literal["remove database"]=None)->None:
        if confirm == "remove database":
            os.remove(self.db_name)
            return
        print("If you want to remove database, use confirm 'remove database'")

    def create_fts_index(self):
        query = f"""
        INSTALL fts;
        LOAD fts;
        PRAGMA create_fts_index(
            '{self.table}', 'id', 'context', overwrite=1
        );
        """.strip()
        self.sql(query)
    