from typing import Literal, List, Optional, Any
from pydantic import BaseModel, Field
from sentence_transformers.cross_encoder import CrossEncoder
from broai.interface import Context
from broai.experiments.utils import experiment

@experiment
class ReRanker(BaseModel):
    model_id:Literal["cross-encoder/ms-marco-MiniLM-L6-v2"] = Field(default="cross-encoder/ms-marco-MiniLM-L6-v2")
    model:Any = None

    def __init__(self, **data):
        super().__init__(**data)
        self.model = self.get_model()

    def get_model(self):
        return CrossEncoder(model_name_or_path=self.model_id)

    def run(self, search_query:str, contexts:List[Context], top_n:int=5):
        paired_sentences = [[search_query, context.context] for context in contexts]
        scores = self.model.predict(paired_sentences)
        top_rank = scores.argsort()[::-1][:top_n]
        ranked_contents = [contexts[n] for n in top_rank]
        ranked_scores = scores[top_rank]
        return ranked_contents, ranked_scores.tolist()