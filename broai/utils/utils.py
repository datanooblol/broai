from pydantic import BaseModel
from typing import Dict, Any
from functools import wraps
from datetime import datetime
import requests

def timelog(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        response = func(*args, **kwargs)
        time_elapsed = datetime.now() - start_time
        print('\x1b[6;37;42m'+'Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed)+'\x1b[0m')
        return response
    return wrapper

class Document(BaseModel):
    id:str = None
    page_content:str
    metadata:Dict[str, Any]
    type:str = None
    


def scrape_jina_ai(url: str) -> str:
    response = requests.get("https://r.jina.ai/" + url)
    return response.text

def quick_chunk(data:str, chunk_size:int=500, overlap:int=100)->list:
    tokens = data.split(" ")
    chunks = []
    n_token = len(tokens)
    batch = int(n_token/chunk_size)+1
    for i in range(batch):
        if (i!=0) and (overlap is not None):
            start_idx = (i*chunk_size)-overlap
            end_idx = ((i+1)*chunk_size)-overlap
        else:
            start_idx = i*chunk_size
            end_idx = (i+1)*chunk_size
        proxy = tokens[start_idx:end_idx]
        proxy = " ".join(proxy)
        chunks.append(proxy)
    return chunks









