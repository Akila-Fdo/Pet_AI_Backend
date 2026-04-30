from chatbot.agent import agent
import json

def run_chat():
    """
    ✅ FIX: Modern LangChain implementation with proper error handling
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
            
            # ✅ FIX: Include animal context for better responses
            enriched_input = f"""
User's pet type: {animal}

User query: {user_input}
"""
            
            # ✅ FIX: Use .invoke() instead of deprecated .run()
            # Modern LangChain AgentExecutor requires dict input with "input" key
            response = agent.invoke({"input": enriched_input})
            
            # ✅ FIX: Proper output handling
            # AgentExecutor returns dict with "output" key
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