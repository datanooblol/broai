from broai.prompt_management.core import PromptGenerator
from broai.prompt_management.interface import Persona, Instructions, Examples, Example
from broai.experiments.bro_agent import BroAgent
from pydantic import BaseModel, Field
from typing import Tuple, List, Dict, Any, Optional

# you can use any model sharing the same methods: .run, .SystemMessage, .UserMessage, .AIMessage
from broai.llm_management.ollama import BedrockOllamaChat
bedrock_model = BedrockOllamaChat(
    model_name="us.meta.llama3-2-1b-instruct-v1:0",
    temperature=0,
)

class InputMessage(BaseModel):
    message:str = Field(description="A user's input message that you have to understand and respond according to the task")

class StructuredOutput(BaseModel):
    respond:str = Field(description="An agent's respond to the message based on the task provided in the instructions")

prompt_generator = PromptGenerator(
    persona=Persona(name="John", description="a helpful assistant"),
    instructions=Instructions(
        instructions=[
            "something John must do to complete the task"
        ],
        cautions=[
            "something John must not do. if he does, he may fail the task"
        ]
    ),
    structured_output=StructuredOutput,
    examples=Examples(examples=[
        Example(
            setting="A setting of an example, i.e. a journal article, a blog post, a social encounter",
            input=InputMessage(message="This is a user's input message"),
            output=StructuredOutput(respond="This is what an agent should respond")
        )
    ]),
    fallback=StructuredOutput(respond="Fall back is used when parsing structured_output fails or LLM service yields error")
)

agent = BroAgent(
    prompt_generator=prompt_generator,
    model=bedrock_model
)