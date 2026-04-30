#!/usr/bin/env python3
"""
Test script to verify chatbot-FastAPI integration
"""
import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/akilafernando/Documents/GitHub/Pet_AI_Backend')

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("TEST 1: Testing imports...")
    print("=" * 60)
    try:
        from chatbot.llm import llm
        print("✅ LLM import successful")
        
        from chatbot.tools import analyze_pet_image
        print("✅ Tools import successful")
        
        from chatbot.agent import agent
        print("✅ Agent import successful")
        
        from chatbot.memory import memory
        print("✅ Memory import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_initialization():
    """Test that agent is properly initialized"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing agent initialization...")
    print("=" * 60)
    try:
        from chatbot.agent import agent
        print(f"✅ Agent type: {type(agent)}")
        print(f"✅ Agent has tools: {agent.tools is not None}")
        print(f"✅ Agent has memory: {agent.memory is not None}")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_query():
    """Test a simple query without tool invocation"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing simple query (no image)...")
    print("=" * 60)
    try:
        from chatbot.agent import agent
        
        # ✅ FIX: Use .invoke() with proper input dict for LangChain 0.1.x agents
        response = agent.invoke({
            "input": """
User's pet type: dog

User query: My dog seems to be scratching a lot. What could be the cause?
"""
        })
        
        output = response.get("output", str(response))
        print(f"✅ Query successful!")
        print(f"Response: {output[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_availability():
    """Test that tool is properly available"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing tool availability...")
    print("=" * 60)
    try:
        from chatbot.agent import agent
        
        tools = [t.name for t in agent.tools]
        print(f"✅ Available tools: {tools}")
        
        if "analyze_pet_image" in tools:
            print("✅ analyze_pet_image tool is available")
            return True
        else:
            print("❌ analyze_pet_image tool not found")
            return False
    except Exception as e:
        print(f"❌ Tool check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("🐾 PET AI HEALTHCARE SYSTEM - INTEGRATION TEST 🐾")
    print("\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Agent Initialization", test_agent_initialization()))
    results.append(("Tool Availability", test_tool_availability()))
    results.append(("Simple Query", test_simple_query()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED! Integration looks good.")
        print("\nYou can now run: python chatbot/main.py")
    else:
        print("❌ Some tests failed. Check errors above.")
    print("=" * 60)
    print("\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
