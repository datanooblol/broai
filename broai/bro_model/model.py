from pydantic import BaseModel, Field

class BroModel(BaseModel):
    @classmethod
    def as_prompt(cls):
        return "prompt"