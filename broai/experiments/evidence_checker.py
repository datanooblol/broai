from rouge_score import rouge_scorer
from pydantic import BaseModel, Field
from typing import List
import json
from broai.interface import Context
from collections import defaultdict


class Contexts(BaseModel):
    """This data model is a wrapper for easy usage"""
    contexts: List[Context]

    def _source_token(self, text, token_type):
        return f"<|start_{token_type}|> {text} <|end_{token_type}|>"

    def as_prompt(self):
        prompt = []
        for context in self.contexts:
            s = self._source_token(context.metadata['source'], token_type="source")
            c = self._source_token(context.context, token_type="context")
            prompt.append(
                f"{s}\n{c}"
            )
        return "\n".join(prompt)


class Answer(BaseModel):
    """Any answer in RAG system must return its evidence for further investigation"""
    answer: str = Field(description="The answer from LLM in RAG system")
    evidence: str = Field(description="The evedence that the LLM uses to answer the question")


class Answers(BaseModel):
    """This is considered a container for all answers.

    Example of Prompt to construct Answers:

        <|SYSTEM_RPOMPT|>
        Extract the information from Contexts based on Query. 
        Do not make up your response. 
        Return your response in a json code block with the following JSON schemas:
        ```json
        [
            {
                "answer": "your answer based on Query",
                "evidence": "an evidence from Contexts that you use it to answer"
            },
            {
                "answer": "your answer based on Query",
                "evidence": "an evidence from Contexts that you use it to answer"
            }
        ]
        ```
    """
    answers: List[Answer] = Field(description="This is a list containing Answer")

    @staticmethod
    def _extract_json(text):
        text = "```".join(text.split("```")[1:])
        if text.startswith("json"):
            text = text[4:]
        text = text.split("```")[0]
        return text

    @classmethod
    def parse_raw_json(cls, text):
        try:
            array_of_answers = json.loads(text)
        except:
            text = cls._extract_json(text)
            array_of_answers = json.loads(text)
        return cls(answers=array_of_answers)


class EvidenceChecker:
    """This is an evidence checker that will be used accompanying with Answers and Contexts class
    Cautions:
        - it's possible to get the same evidence across the contexts if contexts are chunked by using overlapping method. The reason is the evidence may live around the middle or end of one context and live around the middle or start of one another.
    """

    def __init__(self):
        pass

    def deduplicate(self, base_results):
        """Find the way to pop the list based on index and add deduplicated back later"""
        results = base_results.copy()
        compositions = []
        for result in results:
            answer = result['answer']
            composition = f"{answer.answer} {answer.evidence}"
            compositions.append(composition)
        index_map = defaultdict(list)
        for idx, value in enumerate(compositions):
            index_map[value].append(idx)

        # Filter to keep only duplicates
        duplicates = {key: idxs for key, idxs in index_map.items() if len(idxs) > 1}
        filter_out_index = list(duplicates.values())[0]
        filter_out_index = sorted(filter_out_index, reverse=True)
        duplicated_results = []
        # print(filter_out_index)
        for idx in filter_out_index:
            pop_out = results.pop(idx)
            duplicated_results.append(pop_out)
        baseline = 0
        deduplicated_result = None
        for result in duplicated_results:
            score = result['scores']['f1']
            if score > baseline:
                baseline = score
                deduplicated_result = result
        results.append(deduplicated_result)
        return results

    def rouge_search(self, query, answers: Answers, contexts: Contexts, metric="rougeL"):
        scorer = rouge_scorer.RougeScorer(rouge_types=[metric], use_stemmer=True)
        results = []
        # selected_contexts = []
        for answer in answers.answers:
            e = answer.evidence
            for context in contexts.contexts:
                c = context.context
                score = scorer.score(target=c, prediction=e)[metric]
                if score.precision > 0.8:
                    results.append({
                        "answer": answer,
                        "context": context,
                        "scores": {
                            "precision": score.precision,
                            "recall": score.recall,
                            "f1": score.fmeasure
                        }
                    })
        return {
            "query": query,
            "results": results
        }