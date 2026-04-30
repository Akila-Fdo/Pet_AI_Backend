from langchain.memory import ConversationBufferMemory

# ✅ FIX: Memory configuration compatible with LangChain 0.1.x
memory = ConversationBufferMemory(
    memory_key="chat_history",
    human_prefix="User",
    ai_prefix="Assistant",
    return_messages=True
)