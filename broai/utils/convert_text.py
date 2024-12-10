from pydantic import BaseModel
import json
from typing import Callable
from broai.utils.extract_text import extract_annotations
from broai.utils.mapping import map_with_dtypes

def convert_pydantic_to_prompt(obj:BaseModel):
    schemas = {}
    example = {}
    for k, v in obj.model_fields.items():
        schemas.update({k: f"{map_with_dtypes(v.annotation)} {v.description}" })
        example.update({k:v.json_schema_extra['example']})
    format_instructions = f"""Do not add any preambles, explanation, conversations or interactions. \nUse this JSON schemas: \n\n{json.dumps(schemas)}\n\nExample: \n\n{json.dumps(example)}\n\nIt's important to remember that always return your response as in the schema above in a code block becuase I have to use the data in JSON format."""
    return schemas, example, format_instructions

def function_to_json_schema(func:Callable)->dict:
    func_type = str(func.__class__.__name__)
    func_name = func.__name__
    func_desc = func.__doc__
    parameters = extract_annotations(func)
    required = parameters.get("required", None)
    if required is not None:
        parameters.pop("required")
    json_schema = {
        "type": func_type,
        func_type: {
            "name": func_name,
            "description": func_desc,
            "parameters": parameters,
        }
    }
    if required is not None:
        json_schema.update({"required": required})
    return json_schema