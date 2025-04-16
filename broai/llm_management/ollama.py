from typing import Any, Dict, List, Literal
import boto3
import requests
import os

from broai.llm_management.interface import LLMChatInterface

class BedrockOllamaChat(LLMChatInterface):
    def __init__(
            self, 
            model_name:str="us.meta.llama3-2-11b-instruct-v1:0", 
            temperature:float=0, 
            region_name:str="us-west-2",
            aws_access_key_id:str=None,
            aws_secret_access_key:str=None,
            aws_session_token:str=None
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

    def get_model(self, ):
        param = {
            "service_name": "bedrock-runtime",
            "region_name": self.region_name,
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "aws_session_token": self.aws_session_token,
        }
        return boto3.client(**param)

    def UserMessage(self, text:str)->Dict[str, str]:
        return {"role": "user", "content": [{"text": text}]}
    
    def AIMessage(self, text:str)->Dict[str, str]:
        return {"role": "assistant", "content": [{"text": text}]}
    
    def SystemMessage(self, text:str)->List[Dict[str, str]]:
        return [{"text": text}]

    def run(self, system_prompt:str, messages:List[Dict[str, str]])->str:
        model = self.get_model()
        response = model.converse(
            modelId=self.model_name,
            messages=messages,
            system=self.SystemMessage(system_prompt),
            inferenceConfig={"temperature": self.temperature},
        )
        return response['output']['message']['content'][0]['text']
