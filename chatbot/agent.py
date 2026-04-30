from langchain.agents import initialize_agent, AgentType
from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

tools = [analyze_pet_image]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)