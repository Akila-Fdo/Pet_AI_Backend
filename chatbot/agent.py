from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.callbacks import StdOutCallbackHandler
from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

# Tools list - the @tool decorator in tools.py creates a LangChain tool
tools = [analyze_pet_image]

# Initialize the agent with proper configuration
# Using structured chat agent which supports multi-input tools
# (image_path, animal, disease_type parameters)
agent_executor = AgentExecutor(
    agent=create_structured_chat_agent(
        llm=llm,
        tools=tools,
        system_prompt="You are a helpful pet health assistant that can analyze images and provide diagnostic information."
    ),
    tools=tools,
    memory=memory,
    verbose=True,
    callbacks=[StdOutCallbackHandler()],
    max_iterations=5,
    handle_parsing_errors=True
)

# Export as 'agent' for backward compatibility
agent = agent_executor