from langchain.memory import ConversationBufferMemory

# ✅ FIX: Proper memory configuration with input/output keys
memory = ConversationBufferMemory(
    memory_key="chat_history",  # Key used in prompt template
    input_key="input",           # Key for user input
    output_key="output",         # Key for agent output
    return_messages=True         # Return as message objects for modern LangChain
)