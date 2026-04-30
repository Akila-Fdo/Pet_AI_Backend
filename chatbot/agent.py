import sys
import os

# ✅ FIX: Add parent directory to path so imports work from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import initialize_agent, AgentType
from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

# ✅ FIX: Tools list
tools = [analyze_pet_image]

# ✅ FIX: Create agent with conversation memory
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    early_stopping_method="generate"
)