# BroAI: If you want to be a bro, you need to use broai.

BroAI is a library designed to help you develop AI Chatbots or Agents with ease.

## Features

### ToolBro
A class that transforms your functions into a format readable by Large Language Models (LLMs).

- Acts as a wrapper function or Pydantic class to convert functions into prompts for LLMs.
- Simple installation and usage.

### AgentBro
A class to package ideas into ready-to-use prompts.

- Includes attributes like name, persona, background, examples, and structured output.
- Example class provides your AgentBro with examples of what to do.
- Easy integration with any LLM in the market, wrapped in a BroModel.

### Pydantic Integration
BroAI provides RequestBro, ResponseBro, and FieldBro to wrap Pydantic's BaseModel.

- Simplifies integration with Pydantic's BaseModel and Field.
- Allows easy wrapping of any LLM in a structured format for seamless integration.

## Future Updates
Initial focus will be on the above features.