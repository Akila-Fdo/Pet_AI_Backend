import sys
import os
import json

# ✅ FIX: Add parent directory to path so imports work from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.agent import agent

def run_chat():
    """
    ✅ FIX: LangChain 0.1.x compatible implementation with proper error handling
    """
    print("🐾 Pet AI Chatbot (LangChain) Started")
    print("Type 'quit' or 'exit' to stop\n")

    # ✅ FIX: Start with context about the animal
    # In a real app, this would be detected from user input
    animal = "dog"  # Currently hardcoded, can be detected from conversation
    
    print(f"Current Pet Type: {animal} 🐕")
    print("You can tell me about your pet's health concerns (skin/eye issues, etc.)\n")

    while True:
        try:
            user_input = input("You: ").strip()
            
            # Exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Goodbye! 👋 Take care of your pet!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # ✅ FIX: Include animal context and detailed guidance
            # Tell the LLM to be helpful and answer questions directly first
            enriched_input = f"""[SYSTEM: You are a helpful veterinary assistant. Answer health questions directly with useful information. Only use tools when the user provides a real image path.]

Pet type: {animal}
User message: {user_input}
"""
            
            # ✅ FIX: Use .invoke() for LangChain 0.1.x agents
            response = agent.invoke({"input": enriched_input})
            
            # Extract output from response dict
            bot_response = response.get("output", str(response))
            print(f"\nBot: {bot_response}\n")
        
        except KeyboardInterrupt:
            print("\n\nBot: Chatbot interrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    run_chat()