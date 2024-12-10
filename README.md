# Yo Bro!!

This is a library to help you develop AI Chatbot or Agent easier.  

Here what is my plan, bro:  

## BroTool
Here is a class that can magically change your function into LLM readable format. 

- This is gonna act as a wrapper function or pydantic class that convert it into to prompt for LLM.  
- This should not be any problem in installing since I plan to make it simple.  

## BroAgent  
Here is a class where you can pack some ideas into a ready to use prompt.  

- This may include your bro: name, persona, background, example, structured_output.  
- Example class is where you give your BroAgent an example what to do.
- BroAgent will be easy to integrate with any kind of LLM in the market, but you need to wrap in all up as in BroModel which I'll explain it later


## BroModel  
Here is where your LLM is live here.  

- This is gonna be dead simple. You just warp any LLM you prefer in our explictly instructed structure, so you can integreate with me easily. 
- BroModel will follow the practice using a class with `__call__` in the object, so we can do it like a breeze.  

# Future updates  
Nah bro, I'll try to do only this first.