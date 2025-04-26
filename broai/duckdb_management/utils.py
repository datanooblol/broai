from typing import Optional, List, Dict, Any

def get_batch_update_query(table:str, schemas:dict, data:str, ref_keys:list)->str:
    query = f"""
    CREATE TEMP TABLE updates ({", ".join([f"{field} {schema}" for field, schema in schemas.items()])});
    INSERT INTO updates ({", ".join([f"{field}" for field in schemas.keys()])}) VALUES {data};

    UPDATE {table}
    SET {", ".join([f"{field} = updates.{field}" for field in schemas.keys() if field not in ref_keys])}
    FROM updates
    WHERE {" AND ".join([f"{table}.{field} = updates.{field}" for field in schemas.keys() if field in ref_keys])};
    """.strip()
    return query

def get_create_table_query(table:str, schemas:Dict[str, Any])->str:
    param = ",\n\t".join([f"{field} {dtype}".replace('', '') for field, dtype in schemas.items()])
    query = f"""
    CREATE TABLE IF NOT EXISTS {table} (\n\t{param}\n);
    """.strip()
    return query

def get_insert_query(table:str, fields:List[str], data:str)->str:
    query = f"""
    INSERT INTO {table} ({", ".join(fields).replace(";", "")}) VALUES {data.replace(";", "")};
    """.strip()
    return query

def get_select_query(table:str, fields:List[str], where:Optional[str]=None)->str:
    query = f"""
    SELECT {", ".join(fields)} FROM {table} {where};
    """
    return query

def get_delete_query(table:str, where_condition:str):
    where_condition = where_condition.replace(";", "").strip()
    text = "where "
    if where_condition.lower().startswith(text):
        where_condition = where_condition[len(text):]
    query = f"""DELETE FROM {table} WHERE {where_condition};"""
    return query

def replace_single_quote(text:str):
    return text.replace("'", "<|single_quote|>")

def reverse_single_quote(text:str):
    return text.replace("<|single_quote|>", "'")

class DataTypeConversion:
    @staticmethod
    def convert_single_quote(text:str):
        return text.replace("'", "<|single_quote|>")

    @staticmethod        
    def reverse_single_quote(text:str):
        return text.replace("<|single_quote|>", "'")