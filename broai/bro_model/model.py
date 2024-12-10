from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
import json
from broai.utils.extract_text import extract_json_from_codeblock

def FieldBro(description, default=None, **kwargs):
    kwargs['example'] = default
    return Field(description=description, default=default, **kwargs)

def extract_content(input_str: str) -> str:
    start = input_str.find('{') + 1
    end = input_str.rfind('}')
    if start == 0 or end == -1 or start >= end:
        return ""  # Return an empty string if the braces are not found or in the wrong order
    return input_str[start:end]

class RequestBro(BaseModel):
    """This is what we need to know about a bro agent."""
    name:str = Field(description="bro name")
    role:str = Field(description="bro role")
    persona:str = Field(description="bro persona")
    experiences:List[str] = Field(description="bro experiences")
    tasks:List[str] = Field(description="bro tasks")
    inputs:List[str] = Field(description="bro inputs")

    def to_prompt(self):
        prompt = []
        for name, value in self.model_dump().items():
            if value is not None:
                if isinstance(value, list):
                    if(name != "inputs"):
                        value = "\n\t-".join(value)
                        prompt.append(f"Your {name} is: \n\t-{value}")
                    # else:
                    #     value = "\n\n".join(value)
                    #     prompt.append(f"\n{value}")
                else:
                    prompt.append(f"Your {name} is {value}")
        return "\n".join(prompt)
    
    def to_inputs(self):
        prompt = []
        for name, value in self.model_dump().items():
            if name == "inputs":
                for val in value:
                    prompt.append(f"{val}")
        return "\n\n".join(prompt)+"\n"

    def get_inputs(self):
        inputs = []
        for input_str in self.inputs:
            inputs.append(extract_content(input_str))
        return inputs


class PromptBro(BaseModel):
    @classmethod
    def add_code(cls, code)->str:
        return f"""\n```json\n\n{code}\n\n```\n"""
    
    @classmethod
    def to_prompt(cls)->str:
        cls.to_do()
        cls.to_example()
        return "\n".join([cls.to_do(), cls.to_example()])
    
    @classmethod
    def to_do(cls)->str:
        prompt = []
        prompt.append("""Remember always return your response in a code block with the correct JSON schema format becuase your response will be used later in the next stage.""")
        prompt.append("Use this JSON schemas: ")
        code = {name:annotaion.description for name, annotaion in cls.model_fields.items()}
        prompt.append(cls.add_code(code))
        return "\n".join(prompt)
    
    @classmethod
    def to_example(cls)->str:
        prompt = []
        prompt.append("Example of the response: ")
        code = {name:annotaion.json_schema_extra['example'] for name, annotaion in cls.model_fields.items()}
        prompt.append(cls.add_code(json.dumps(code)))
        return "\n".join(prompt)

class ResponseBro(PromptBro):
    @classmethod
    def from_json(cls, json_str:str) -> ResponseBro:
        data = extract_json_from_codeblock(json_str)
        return cls.model_validate_json(data)
    

    
    
    
