from langchain.memory import ConversationBufferMemory

# Initialize conversation memory for the chatbot
# This keeps track of the conversation history for context
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input",
    output_key="output"
)