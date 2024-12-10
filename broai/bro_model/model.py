from pydantic import BaseModel, Field

class BroModel(BaseModel):
    @classmethod
    def as_prompt(cls):
        return "prompt boi!!"
    
    @classmethod
    def as_test(cls):
        proxy = cls.model_fields
        return proxy
    
def BroField(description, default=None, **kwargs):
    return Field(description=description, default=default, **kwargs)
    
