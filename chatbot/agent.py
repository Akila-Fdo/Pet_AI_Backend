from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

# Tools list - the @tool decorator in tools.py creates a LangChain tool
tools = [analyze_pet_image]

# Create a simple agent wrapper that delegates to LLM
# This is compatible with various LangChain versions
class SimpleAgent:
    """Simple agent wrapper that delegates to LLM and tool calling"""
    
    def __init__(self, llm, tools, memory, verbose=True, callbacks=None, max_iterations=5):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.verbose = verbose
        self.callbacks = callbacks or []
        self.max_iterations = max_iterations
        self.tool_map = {tool.name: tool for tool in tools}
    
    def run(self, input_text):
        """Run the agent with the given input"""
        if self.verbose:
            print(f"Agent input: {input_text}\n")
        
        # For simple cases, just return the LLM response
        # The main.py handles most of the logic directly
        response = self.llm.invoke(input_text)
        return response.content if hasattr(response, 'content') else str(response)

# Initialize the simple agent
agent = SimpleAgent(
    llm=llm,
    tools=tools,
    memory=memory,
    verbose=True,
    callbacks=[],
    max_iterations=5
)

# For backward compatibility, also create an agent_executor
class AgentExecutorWrapper:
    def __init__(self, agent, tools, memory):
        self.agent = agent
        self.tools = tools
        self.memory = memory
    
    def run(self, input_text):
        return self.agent.run(input_text)
    
    def invoke(self, input_dict):
        input_text = input_dict.get('input', '') if isinstance(input_dict, dict) else str(input_dict)
        return {"output": self.agent.run(input_text)}

agent_executor = AgentExecutorWrapper(agent, tools, memory)