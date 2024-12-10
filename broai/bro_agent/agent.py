from pydantic import BaseModel
from typing import List, Optional, Callable
from broai.bro_model.model import ResponseBro, RequestBro

class Example(BaseModel):
    input:str
    output:str
    
class Examples(BaseModel):
    examples:List[Example]
    
    def as_prompt(self):
        examples = []
        for enum, example in enumerate(self.examples):
            examples.append(f"Example {enum+1}\n\nInput: \n\n{example.input}\n\nOutput:\n\n{example.output}\n\n")
        return "".join(examples)
    
class AgentBro:
    def __init__(self,
        request:RequestBro,
        response:ResponseBro,
        examples:Optional[List[Example]] = None,
        llm:Callable=None,
        tool:Optional[Callable] = None,
    ):
        self.request = request
        self.response = response
        self.examples = examples
        self.llm = llm
        self.tool = tool    
        self.prompt = None

    # def __call__(self, user_input):
    #     return self.run(user_input)
    
    # def as_prompt(self):
    #     prompt = []
    #     targets = ["name", "persona", "background", "tasks", "response", "examples"]
    #     for k, v in self.model_dump().items():
    #         if k in targets and v is not None:
    #             prompt.append(f"Your {k} is {v}")
    #     return "\n".join(prompt)

    def to_prompt(self, **inputs)->str: 
        _request = self.request.to_prompt()
        _response = self.response.to_prompt()
        _inputs = self.request.to_inputs()
        if len(inputs) == 0:
            return f"{_request}\n\n{_response}\n{_inputs}"

        function_inputs = set(inputs.keys())
        request_inputs = set(self.request.get_inputs())
        if len(function_inputs & request_inputs) != len(request_inputs):
            raise ValueError(f"You have to provide all the inputs. {list(request_inputs-function_inputs)} are missing.")

        input_dict = {}
        for key, value in inputs.items():
            if key in self.request.get_inputs():
                input_dict[key] = value
        _inputs = _inputs.format(**input_dict)
        prompt = f"{_request}\n\n{_response}\n{_inputs}"
        return prompt

    
    def run(self, **user_inputs)->str:
        prompt = self.to_prompt(**user_inputs)
        self.prompt = prompt
        # message = prompt
        message = self.llm(prompt)
        return message