from FlagEmbedding import BGEM3FlagModel
from typing import Literal, List, Optional, Any, Protocol
from pydantic import BaseModel, Field
from broai.experiments.utils import experiment
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

class EmbeddingDimension(Enum):
    BAAI_BGE_M3 = 1024

class BaseEmbeddingModel(ABC):
    @abstractmethod
    def run(self, sentences: List[str]) -> np.ndarray:
        ...

@experiment
class BAAIEmbedding(BaseEmbeddingModel, BaseModel):
    model_id: Literal["BAAI/bge-m3"] = Field(default="BAAI/bge-m3")
    use_fp16: bool = Field(default=True)
    batch_size:Optional[int] = Field(default=None)
    max_length:Optional[int] = Field(default=None)
    model: Optional[Any] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.model = self.get_model()

    def get_model(self):
        params = {}
        params['model_name_or_path'] = self.model_id
        params['use_fp16'] = self.use_fp16
        if self.batch_size:
            params['batch_size'] = self.batch_size
        if self.max_length:
            params['max_length'] = self.max_length
        return BGEM3FlagModel(**params)
    
    def run(self, sentences: List[str]):
        if not isinstance(sentences, list):
            raise TypeError(f"sentences must be of type list with str as element, not {type(sentences)}")
        vectors = self.model.encode(sentences)
        return vectors['dense_vecs']