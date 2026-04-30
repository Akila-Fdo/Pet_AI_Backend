from chatbot.agent import agent

def run_chat():
    print("🐾 Pet AI Chatbot (LangChain) Started")

    # manually define pet type for now
    animal = "dog"

    while True:
        user_input = input("You: ")

        # simple instruction injection
        enriched_input = f"""
        User pet type: {animal}

        {user_input}
        """

        response = agent.run(enriched_input)

        print("Bot:", response)


if __name__ == "__main__":
    run_chat()