#!/usr/bin/env python3
"""
Simple validation test - checks that chatbot works without FastAPI backend
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.agent import agent
from chatbot.memory import memory

print("\n🐾 CHATBOT INTEGRATION VALIDATION\n")

tests_passed = 0
tests_total = 0

# Test 1: General conversation without images
tests_total += 1
print("Test 1: General conversation (no image path)")
try:
    memory.clear()
    response = agent.invoke({"input": "My dog has been scratching. What could this be?"})
    if response and "output" in response:
        print(f"✅ PASS - Agent responded\n")
        tests_passed += 1
    else:
        print(f"❌ FAIL - No response\n")
except Exception as e:
    print(f"❌ FAIL - {str(e)[:100]}\n")

# Test 2: With real image path
tests_total += 1
print("Test 2: User provides real image file path")
try:
    memory.clear()
    img_path = "/Users/akilafernando/Documents/GitHub/Pet_AI_Backend/sample_images/Atopic-dermatitis_Dog-chronic-lick-sore-on-leg_DermVets_jpg.rf.e3f4c6fcb1f3dbf3f44e1ef209b12004.jpg"
    response = agent.invoke({"input": f"Can you analyze this image: {img_path}"})
    if response and "output" in response:
        print(f"✅ PASS - Agent processed image path\n")
        tests_passed += 1
    else:
        print(f"❌ FAIL - No response\n")
except Exception as e:
    print(f"❌ FAIL - {str(e)[:100]}\n")

# Test 3: Multi-turn conversation
tests_total += 1
print("Test 3: Multi-turn conversation with memory")
try:
    memory.clear()
    response1 = agent.invoke({"input": "My dog has itchy skin"})
    response2 = agent.invoke({"input": "Is this serious?"})
    if response1 and response2 and "output" in response1 and "output" in response2:
        print(f"✅ PASS - Multi-turn conversation works\n")
        tests_passed += 1
    else:
        print(f"❌ FAIL - Incomplete responses\n")
except Exception as e:
    print(f"❌ FAIL - {str(e)[:100]}\n")

# Summary
print("="*50)
print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
print("="*50)

if tests_passed == tests_total:
    print("✅ All tests PASSED - Chatbot integration is working!")
    sys.exit(0)
else:
    print(f"⚠️  {tests_total - tests_passed} test(s) failed")
    sys.exit(1)
