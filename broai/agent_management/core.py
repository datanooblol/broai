from typing import Any, Callable, List, Union
from pydantic import BaseModel
from broai.prompt_management.core import PromptGenerator
from broai.prompt_management.utils import get_input, get_json_schema, parse_json_output
from broai.llm_management.interface import LLMChatInterface

class BroAgent:
    def __init__(
            self,
            prompt_generator:PromptGenerator,
            model:LLMChatInterface,
            retry:int=3,
            tools:List[Callable] = None
    ):
        self.prompt_generator = prompt_generator
        self.model = model
        self.retry = retry
        self.tools = tools
        self.cnt = 0
        self.__errors = []

    def get_error_msg(self, errors:List[str])->str:
        if len(errors)==0:
            return ""
        return "Avoid the following errors: \n\n{error_msg}".format(error_msg="\n".join(errors))

    def response_pydantic(self, text:str):
        try:
            parsed_json = parse_json_output(text)
            structure_output = self.prompt_generator.structured_output.model_validate_json(parsed_json)
            return structure_output
        except Exception as e:
            self.__errors.append(str(e))
            self.cnt+=1
            return None
    
    def _run(self, request):
        response = self.model.run(
            system_prompt=self.prompt_generator.as_prompt(), 
            messages=[self.model.UserMessage(request + "\n" + self.get_error_msg(self.__errors))]
        )
        if isinstance(self.prompt_generator.structured_output, str) or self.prompt_generator.structured_output is None:
            return response
        return self.response_pydantic(response)

    def read_errors(self):
        return self.__errors
    
    def run(self, request:Union[str, BaseModel])->Any:
        self.cnt=0
        if isinstance(request, BaseModel):
            request = get_input(request)
        while self.cnt < self.retry:
            response = self._run(request)
            if response is not None:
                self.cnt=0
                return response
        if response is None:
            # fallback is None -> default message
            if self.prompt_generator.fallback is None:
                return "unknown error"
            # in other case return as it is
            return self.prompt_generator.fallback



