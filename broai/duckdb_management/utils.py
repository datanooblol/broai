from typing import Optional

def get_batch_update_query(table:str, schemas:dict, param:str, ref_keys:list):
    query = f"""
    CREATE TEMP TABLE updates ({", ".join([f"{field} {schema}" for field, schema in schemas.items()])});
    INSERT INTO updates ({", ".join([f"{field}" for field in schemas.keys()])}) VALUES {param};

    UPDATE {table}
    SET {", ".join([f"{field} = updates.{field}" for field in schemas.keys() if field not in ref_keys])}
    FROM updates
    WHERE {" AND ".join([f"{table}.{field} = updates.{field}" for field in schemas.keys() if field in ref_keys])};
    """
    return query

def get_where_statement(where:Optional[str]):
    return f"WHERE {where.replace(';', '')}" if where is not None else ""

def get_create_table_query(table, schemas):
    param = "\n\t".join([f"{field} {dtype}" for field, dtype in schemas.items()])
    query = f"""
    CREATE TABLE IF NOT EXISTS {table} (\n\t{param}\n);
    """.strip()
    return query

def get_insert_query(table, schemas):
    ...