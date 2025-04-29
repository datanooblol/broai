from broai.duckdb_management.utils import get_create_table_query, get_insert_query
from broai.interface import Context
from typing import List, Dict, Any, Literal, Tuple
import duckdb
import os
import json
from broai.experiments.utils import experiment
from broai.experiments.huggingface_embedding import BaseEmbeddingModel
from functools import wraps

def validate_baseclass(input_instance, input_name, baseclass):
    if not isinstance(input_instance, baseclass):
        raise TypeError(f"{input_name} must be of type, {baseclass.__name__}. Instead got {type(input_instance)}")
    return input_instance

def get_json_where_query(field:str, filter_metadata:Dict[str, Any]=None):
    if filter_metadata is None:
        return ""
    query = []
    str_int = lambda k, v: f"{field} ->> '{k}' = '{v}'" if isinstance(v, str) else f"CAST({field} ->> '{k}' AS INTEGER) = {v}"
    for k, v in filter_metadata.items():
        query.append(str_int(k, v))
    return f"WHERE {' AND '.join(query)}"

class BaseVectorStore:
    def __init__(self, db_name:str, table, schemas:Dict[str, Any]):
        self.db_name = db_name
        self.table = table
        self.__schemas = schemas
        self.create_table()

    def sql(self, query, params:Dict[str, Any]=None):
        with duckdb.connect(self.db_name) as con:
            con.sql(query, params=params)

    def sql_df(self, query, params:Dict[str, Any]=None):
        with duckdb.connect(self.db_name) as con:
            df = con.sql(query, params=params).to_df()
        return df

    def executemany(self, query, rows:List[Tuple[Any]]):
        with duckdb.connect(self.db_name) as con:
            con.executemany(query, rows)
    
    def show_schemas(self):
        return self.__schemas

    def delete_table(self):
        query = f"DELETE FROM {self.table};"
        self.sql(query)

    def drop_table(self)->None:
        query = f"""DROP TABLE {self.table};"""
        self.sql(query)

    def create_table(self,):
        query = get_create_table_query(table=self.table, schemas=self.show_schemas())
        self.sql(query)

    def remove_database(self, confirm:str=None)->None:
        if confirm == f"remove {self.db_name}":
            os.remove(self.db_name)
            return
        print(f"If you want to remove database, use confirm 'remove {self.db_name}'")

@experiment
class DuckVectorStore(BaseVectorStore):
    """
    A vector store backed by DuckDB.

    Args:
        db_name (str): Path to the DuckDB file (e.g., './duckmemory.db').
        table (str): Name of the table to store embeddings.
        embedding (BaseEmbeddingModel): An embedding model that implements the `.run()` method.
        limit (int, optional): Default number of top results to return. Defaults to 5.
    """
    def __init__(self, db_name:str, table:str, embedding:BaseEmbeddingModel, limit:int=5):
        self.embedding_model = validate_baseclass(embedding, "embedding", BaseEmbeddingModel)
        self.embedding_size = self.embedding_model.run(["test"]).shape[1]
        self.limit = limit
        schemas = {
            "id": "VARCHAR",
            "context": "VARCHAR",
            "metadata": "JSON",
            "type": "VARCHAR",
            "embedding": f"FLOAT[{self.embedding_size}]",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP",
        }
        super().__init__(db_name=db_name, table=table, schemas=schemas)

    @staticmethod
    def with_fts_index(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.create_fts_index()
            return result
        return wrapper
    
    # ---- [Create] ---- #
    @with_fts_index
    def add_contexts(self, contexts:List[Context]):
        id_list = [c.id for c in contexts]
        context_list = [c.context for c in contexts]
        metadata_list = [c.metadata for c in contexts]
        type_list = [c.type for c in contexts]
        embedding_list = self.embedding_model.run(context_list)
        created_list = [c.created_at for c in contexts]
        rows = list(zip(id_list, context_list, metadata_list, type_list, embedding_list, created_list, created_list))
        query = f"INSERT INTO {self.table} (id, context, metadata, type, embedding, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.executemany(query, rows)

    # ---- [Read] ---- #
    def read_all(self):
        query = f"SELECT * FROM {self.table};"
        return self.sql_df(query)

    def read_by_ids(self, ids:List[str]):
        params = ", ".join([f'{i}' for i in ids])
        query = f"SELECT * FROM {self.table} WHERE id IN ({params});"
        return self.sql_df(query)

    def vector_search(self, search_query:str, filter_metadata:Dict[str, Any]=None, context:bool=True, limit:int=None):
        if limit is None or not isinstance(limit, int):
            limit = self.limit
        vector = self.embedding_model.run(sentences=[search_query])[0]
        filter_query = get_json_where_query(field="metadata", filter_metadata=filter_metadata)
        query = f"""SELECT *, array_cosine_similarity(embedding, $searchVector::FLOAT[{self.embedding_size}]) AS score FROM {self.table} {filter_query} ORDER BY score DESC LIMIT {limit};"""
        if context is False:
            return self.sql_df(query=query, params=dict(searchVector=vector))
        return self.sql_contexts(query=query, params=dict(searchVector=vector))

    def fulltext_search(self, search_query:str, filter_metadata:Dict[str, Any]=None, context:bool=True, limit:int=None):
        if limit is None or not isinstance(limit, int):
            limit = self.limit
        filter_query = get_json_where_query(field="metadata", filter_metadata=filter_metadata)
        query = f"""\
        SELECT *
        FROM (
            SELECT *, fts_main_{self.table}.match_bm25(
                id,
                '{search_query}',
                fields := 'context'
            ) AS score
            FROM {self.table}
            {filter_query}
        ) sq
        ORDER BY score DESC
        LIMIT {limit};
        """
        if context is False:
            return self.sql_df(query=query, params=None)
        return self.sql_contexts(query=query, params=None)

    def hybrid_search(self, search_query:str, filter_metadata:Dict[str, Any]=None, limit:int=None):
        context = True
        vs_contexts = self.vector_search(search_query, filter_metadata, context, limit)
        fts_contexts = self.fulltext_search(search_query, filter_metadata, context, limit)
        hbs_contexts = []
        id_list = []
        for c in vs_contexts+fts_contexts:
            if c.id not in id_list:
                id_list.append(c.id)
                hbs_contexts.append(c)
        return hbs_contexts
    
    def search(self, 
               search_query:str, 
               filter_metadata:Dict[str, Any]=None, 
               context=True,
               limit:int=None, 
               search_method:Literal["vector", "fulltext", "hybrid"]="vector"
              ):

        if limit is None or not isinstance(limit, int):
            limit = self.limit

        if search_method=='vector':
            return self.vector_search(search_query, filter_metadata, context, limit)
        
        if search_method=='fulltext':
            return self.fulltext_search(search_query, filter_metadata, context, limit)
        
        if search_method=='hybrid':
            return self.hybrid_search(search_query=search_query, filter_metadata=filter_metadata, limit=limit)
        
        raise ValueError(f"search_method: {search_method} is not implemented yet, try: 'vector', 'fulltext', 'hybrid', instead.")
        
    # ---- [Update] ---- #
    @with_fts_index
    def update_contexts(self, contexts:List[Context]):
        id_list = [c.id for c in contexts]
        context_list = [c.context for c in contexts]
        metadata_list = [c.metadata for c in contexts]
        created_list = [c.created_at for c in contexts]
        rows = list(zip(context_list, metadata_list, created_list, id_list))
        query = f"UPDATE {self.table} SET context = ?, metadata = ?, updated_at = ? WHERE id = ?"
        self.executemany(query, rows)

    # ---- [Delete] ---- #
    @with_fts_index
    def delete_contexts(self, contexts:List[Context]):
        rows = [(c.id,) for c in contexts]
        query = f"DELETE FROM {self.table} WHERE id = ?"
        self.executemany(query, rows)

    # ---- [Utils] ---- #
    def sql_contexts(self, query, params:Dict[str, Any]=None):
        df = self.sql_df(query, params=params)
        if df.shape[0]==0:
            return
        df = df.loc[~df['score'].isna(), ["id", "context", "metadata", "type", "updated_at"]].copy()
        return [Context(id=record["id"], context=record["context"], metadata=json.loads(record["metadata"]), type=record['type'], created_at=record['updated_at']) for record in df.to_dict(orient="records")]

    def create_fts_index(self):
        query = f"""
        INSTALL fts;
        LOAD fts;
        PRAGMA create_fts_index(
            '{self.table}', 'id', 'context', overwrite=1
        );
        """.strip()
        self.sql(query)
