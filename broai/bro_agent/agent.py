from pydantic import BaseModel
from typing import List, Optional, Callable

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
    
class Agent(BaseModel):
    name:str
    persona:str
    background:str
    tasks:str
    response:Optional[str] = None
    examples:Optional[List[Example]] = None
    llm:Optional[Callable] = None
    tool:Optional[Callable] = None

    def __call__(self, user_input):
        return self.run(user_input)
    
    def as_prompt(self):
        prompt = []
        targets = ["name", "persona", "background", "tasks", "response", "examples"]
        for k, v in self.model_dump().items():
            if k in targets and v is not None:
                prompt.append(f"Your {k} is {v}")
        return "\n".join(prompt)
    
    def run(self, user_input:str):
        prompt = f"{self.as_prompt()}\n\n{user_input}"
        response = self.llm(prompt)
        return response