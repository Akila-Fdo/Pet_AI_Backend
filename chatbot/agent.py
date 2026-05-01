from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StdOutCallbackHandler
from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

# Tools list - the @tool decorator in tools.py creates a LangChain tool
tools = [analyze_pet_image]

# Initialize the agent with proper configuration
# Using STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION which supports multi-input tools
# (image_path, animal, disease_type parameters)
# 
# Note: initialize_agent is deprecated in newer LangChain versions but still works.
# Future migration path: create_structured_chat_agent (when memory integration improved)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    callbacks=[StdOutCallbackHandler()],
    max_iterations=5,
    early_stopping_method="generate",
    handle_parsing_errors=True
)