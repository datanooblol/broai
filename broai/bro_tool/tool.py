from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Callable, get_args
import typing
from broai.utils.convert_text import function_to_json_schema
from broai.utils.extract_text import extract_json_from_codeblock

class Tool(BaseModel):
    tool: str = Field(description="the name of the tool", example="the name of the tool")
    parameters: Dict[str, Any] = Field(description="a key value object contains all the tool's inputs", example={"param1": "input of param1", "param2": "input of param2", "paramN": "input of paramN"})
    
    @classmethod
    def parse(cls, json_str:str):
        data = extract_json_from_codeblock(json_str)
        # return data
        return cls.model_validate_json(data)

class ToolBro(BaseModel):
    tools:List[Callable]
    
    def _as_prompt(self):
        prompt = ["Read the input carefully, think what the input is all about and which tool is the best match. Return only the name of the tools\n"]
        for tool in self.tools:
            name = tool.__name__
            doc = tool.__doc__
            params = {}
            for k, v in tool.__annotations__.items():
                dtype, desc = get_args(v)
                if (k!='return') & isinstance(v, typing._AnnotatedAlias):
                    params.update({k:desc})
            
            prompt.append(
                f"tool: {name}\n"
                f"description: {doc}\n"
                f"parameters: {json.dumps(params)}\n"
            )
        return "\n".join(prompt)
    
    def to_prompt(self):
        prompt = ["Read the input carefully, think what the input is all about and which tool is the best match. Return only the name and parameters of these tools\n"] 
        json_schemas = []
        for tool in self.tools:
            json_schema = function_to_json_schema(tool)
            json_schemas.append(json_schema)
        prompt.append(json.dumps(json_schemas))
        return "\n\n".join(prompt)
