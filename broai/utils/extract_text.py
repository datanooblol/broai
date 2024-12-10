from broai.utils.mapping import map_with_dtypes
import inspect
from typing import Callable, get_args

def extract_json_from_codeblock(content: str) -> str:
    content = content.split("```json")[1]
    content = content.split("```")[0]
    first_paren = content.find("{")
    last_paren = content.rfind("}")
    return content[first_paren : last_paren + 1]

def extract_annotations(func:Callable):
    parameters = {}
    signature = inspect.signature(func)
    for name, param in signature.parameters.items():
        dtype, desc = get_args(param.annotation)
        default = param.default
        parameters[name] = {"type": map_with_dtypes(dtype), "description": desc}
        if default is inspect._empty:
            if parameters.get("required", None) is None:
                parameters["required"] = []
            parameters["required"].append(name)
        else:
            parameters[name].update({"default": default})
    return parameters