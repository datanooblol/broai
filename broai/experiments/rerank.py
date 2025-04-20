from broai.interface import Context
from typing import List, Tuple, Any
import numpy as np
from broai.experiments.utils import experiment

@experiment
def rerank_contexts(contexts:List[Context], scores:np.ndarray, top_n:int=5)->List[Tuple[Any]]:
    top_rank = scores.argsort()[::-1][:top_n]
    ranked_contents = [contexts[n] for n in top_rank]
    ranked_scores = scores[top_rank]
    return ranked_contents, ranked_scores.tolist()