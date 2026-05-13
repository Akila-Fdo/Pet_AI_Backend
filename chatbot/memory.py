"""
Simple conversation memory implementation
Stores and retrieves conversation history without LangChain dependencies
"""

class SimpleConversationMemory:
    """Minimal conversation buffer memory implementation"""
    
    def __init__(self, memory_key="chat_history", return_messages=True, input_key="input", output_key="output"):
        self.memory_key = memory_key
        self.return_messages = return_messages
        self.input_key = input_key
        self.output_key = output_key
        self.messages = []
    
    def save_context(self, inputs, outputs):
        """Save context from this conversation turn"""
        input_str = inputs.get(self.input_key, "") if isinstance(inputs, dict) else str(inputs)
        output_str = outputs.get(self.output_key, "") if isinstance(outputs, dict) else str(outputs)
        
        self.messages.append({
            "input": input_str,
            "output": output_str
        })
    
    def load_memory_variables(self, inputs):
        """Load memory variables for use in prompts"""
        # Build chat history string from messages
        history = ""
        for msg in self.messages:
            history += f"User: {msg['input']}\n"
            history += f"Assistant: {msg['output']}\n\n"
        
        return {
            self.memory_key: history,
            "messages": self.messages
        }
    
    def clear(self):
        """Clear the memory"""
        self.messages = []

# Initialize conversation memory
memory = SimpleConversationMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input",
    output_key="output"
)