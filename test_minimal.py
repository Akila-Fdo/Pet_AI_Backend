#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/akilafernando/Documents/GitHub/Pet_AI_Backend')

try:
    print("Importing agent...")
    from chatbot.agent import agent
    print("✅ Agent imported")
    
    print("\nTesting agent.invoke() method...")
    response = agent.invoke({"input": "Hello, what can you tell me about dog skin diseases?"})
    print(f"✅ Success!")
    print(f"Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
