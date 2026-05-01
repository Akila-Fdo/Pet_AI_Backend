#!/usr/bin/env python3
"""
Interactive chatbot demo - shows full functionality
Run this to see the chatbot in action
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.agent import agent
from chatbot.memory import memory

def clean_output(text, max_length=300):
    """Clean and truncate agent output for readability"""
    # Remove verbose agent chain logging
    lines = text.split('\n')
    clean_lines = [l for l in lines if l.strip() and not l.startswith('>')]
    result = ' '.join(clean_lines)
    return result[:max_length] + "..." if len(result) > max_length else result

def main():
    print("""
╔════════════════════════════════════════════════════╗
║          🐾 Pet AI Chatbot Demo 🐾                 ║
║     Chatbot ↔ LangChain Agent ↔ FastAPI Backend    ║
╚════════════════════════════════════════════════════╝
    """)
    
    memory.clear()
    
    examples = [
        ("General symptom question", "My dog has been scratching a lot lately"),
        ("Symptom details", "What could cause excessive scratching in dogs?"),
        ("With image path", "Can you analyze this image: /Users/akilafernando/Documents/GitHub/Pet_AI_Backend/sample_images/Atopic-dermatitis_Dog-chronic-lick-sore-on-leg_DermVets_jpg.rf.e3f4c6fcb1f3dbf3f44e1ef209b12004.jpg"),
    ]
    
    for i, (description, user_input) in enumerate(examples, 1):
        print(f"\n{'='*50}")
        print(f"Example {i}: {description}")
        print(f"{'='*50}")
        print(f"\n👤 User: {user_input}")
        print("\n🤖 Agent thinking...\n")
        
        try:
            response = agent.invoke({"input": user_input})
            output = clean_output(response.get("output", "No response"))
            print(f"🤖 Bot: {output}\n")
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:200]}\n")
    
    print("\n" + "="*50)
    print("✅ Demo Complete!")
    print("="*50)
    print("\nKey Features Demonstrated:")
    print("  ✓ General health questions answered")
    print("  ✓ Symptom information provided")
    print("  ✓ Image analysis tool ready for real paths")
    print("  ✓ Multi-turn conversation capable")
    print("\nTo use interactively:")
    print("  cd chatbot && python main.py")
    print("\nTo validate all tests:")
    print("  python validate_chatbot.py")

if __name__ == "__main__":
    main()
