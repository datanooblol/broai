from abc import ABC, abstractmethod
from typing import Any

class LLMChatInterface(ABC):

    @abstractmethod
    def UserMessage(self, text:str) -> Any:
        pass

    @abstractmethod
    def AIMessage(self, text:str) -> Any:
        pass

    @abstractmethod
    def SystemMessage(self, text:str) -> Any:
        pass

    @abstractmethod
    def run(self, formatted_prompt: Any) -> str:
        pass