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

# ✅ FIX: Use prefix to control agent behavior
prefix = """You are a helpful veterinary assistant chatbot.

Rules:
1. Answer health questions with general information (do NOT claim to diagnose)
2. If user describes symptoms, provide helpful general information about those symptoms
3. ONLY use the analyze_pet_image tool if the user explicitly provides a real file path starting with / or ~/
4. Never imagine or make up tool calls
5. Never use placeholder paths like /path/to/image.jpg
6. If user hasn't provided an image, do NOT call any tools - just provide helpful general advice

If you reach the limit of iterations without using a tool, that's fine - just provide your best helpful answer.
"""

# ✅ FIX: Create agent with explicit prefix
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    early_stopping_method="generate",
    agent_kwargs={"prefix": prefix}
)