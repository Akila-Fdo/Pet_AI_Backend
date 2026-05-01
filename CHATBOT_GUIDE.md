# Pet AI Chatbot - Complete Integration Guide

## 🎯 What's Fixed

The chatbot now correctly integrates with the FastAPI backend with these key fixes:

### 1. **Fixed Agent Looping Issue** ✅
- **Problem**: Agent was attempting to call `analyze_pet_image` with placeholder paths (`/path/to/image.jpg`), ignoring user instructions
- **Solution**: Added strict `agent_kwargs` with a system prefix that explicitly instructs the agent to:
  - Only call tool when user provides real file paths (starting with `/` or `~/`)
  - Provide helpful general information without tool use
  - Never imagine or create placeholder tool calls
- **Result**: Agent now provides helpful responses without looping

### 2. **Tool Integration** ✅
- **Fixed Tool Format**: Single JSON input string instead of multiple parameters
- **Tool Name**: `analyze_pet_image` 
- **Input Format**: `{"image_path": "...", "animal": "dog|cat", "disease_type": "skin|eye"}`
- **Returns**: JSON with error details or prediction results

### 3. **LangChain Version Compatibility** ✅
- Downgraded to LangChain 0.1.14 (stable, with working agent functionality)
- Using `ZERO_SHOT_REACT_DESCRIPTION` agent type
- `.invoke()` API instead of deprecated `.run()`
- max_iterations: 3 (prevents excessive looping)

### 4. **Error Handling** ✅
- Gracefully handles missing images
- Detects placeholder paths and rejects them
- Falls back to helpful general advice when tool unavailable
- Returns JSON error messages for debugging

## 📋 How to Use

### Interactive CLI Mode
```bash
cd /Users/akilafernando/Documents/GitHub/Pet_AI_Backend/chatbot
source ../.venv/bin/activate
python main.py
```

Then in the chatbot:
```
You: My dog has been scratching for a week
Bot: <provides general information about scratching>

You: Can you analyze this image: /Users/me/Pictures/dog_rash.jpg
Bot: <analyzes image via FastAPI endpoint>
```

### Key Features

1. **General Health Questions** - No image needed
   ```
   User: "My dog has red patches"
   Bot: Provides helpful general information
   ```

2. **Image Analysis** - With real file paths
   ```
   User: "Analyze this: /path/to/image.jpg"
   Bot: Calls analyze_pet_image tool → FastAPI /predict endpoint
   ```

3. **Placeholder Path Detection** - Prevents tool call
   ```
   User: "Check /path/to/image.jpg"
   Bot: Asks for actual file path
   ```

4. **Multi-Turn Conversation** - Maintains context
   ```
   User: "My dog has skin issues"
   Bot: Provides information
   User: "Is this serious?"
   Bot: Continues conversation with context
   ```

## 🔧 Component Overview

### chatbot/agent.py
```python
# Key configuration:
agent = initialize_agent(
    tools=[analyze_pet_image],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    max_iterations=3,  # Prevents looping
    agent_kwargs={"prefix": "You are a helpful..."}  # Strict instructions
)
```

### chatbot/tools.py
```python
@tool
def analyze_pet_image(input_request: str) -> str:
    # Input: JSON string '{"image_path": "...", "animal": "dog", "disease_type": "skin"}'
    # Output: JSON with prediction or error
    # Detects placeholder paths and rejects them
```

### chatbot/main.py
```python
# User input enrichment:
enriched_input = f"""[SYSTEM: You are a helpful veterinary assistant...]

Pet type: {animal}
User message: {user_input}
"""
agent.invoke({"input": enriched_input})
```

## ✅ Validation

Run the validation script:
```bash
python validate_chatbot.py
```

Expected output:
```
Test 1: General conversation (no image path)
✅ PASS - Agent responded

Test 2: User provides real image file path
✅ PASS - Agent processed image path

Test 3: Multi-turn conversation with memory
✅ PASS - Multi-turn conversation works

RESULTS: 3/3 tests passed
✅ All tests PASSED - Chatbot integration is working!
```

## 🚀 Starting the Full Stack

### Terminal 1 - FastAPI Backend
```bash
cd /Users/akilafernando/Documents/GitHub/Pet_AI_Backend
source .venv/bin/activate
python app/main.py
# Runs on http://127.0.0.1:8000
```

### Terminal 2 - Chatbot CLI
```bash
cd /Users/akilafernando/Documents/GitHub/Pet_AI_Backend/chatbot
source ../.venv/bin/activate
python main.py
# Then interact with the chatbot
```

## 📊 Conversation Flow

```
User Input
    ↓
Enriched with context (pet type)
    ↓
Agent processes with LangChain
    ↓
├─ If simple question → Direct answer
├─ If real image path → Call analyze_pet_image tool
│    ↓
│    Tool validates path (rejects placeholders)
│    ↓
│    POST to FastAPI /predict endpoint
│    ↓
│    Returns prediction or error
└─ If no image → Helpful general information
    ↓
Response to user
```

## 🐛 Troubleshooting

### Issue: Tool not being called with real path
- Verify file path is absolute (starts with `/` or `~/`)
- Check file actually exists
- Ensure JSON formatting: `{"image_path": "...", "animal": "dog", "disease_type": "skin"}`

### Issue: "Connection refused" errors
- Ensure FastAPI backend is running: `python app/main.py`
- Check it's listening on `http://127.0.0.1:8000`

### Issue: Agent looping
- Already fixed! But if issues persist:
  - Check `agent_kwargs` in chatbot/agent.py has the system prefix
  - Reduce max_iterations to 2
  - Restart the chatbot and clear Python cache

### Issue: Placeholder paths being used
- Tool now detects and rejects: `/path/to/image`, `example`, `test`, etc.
- Only accepts real file paths
- Falls back to general advice automatically

## 📝 Dependencies

All required packages are in `requirements.txt`:
- langchain==0.1.14
- langchain-core==0.1.48
- langchain-openai==0.0.7
- openai
- python-dotenv
- requests
- fastapi
- pydantic
- opencv-python
- torch
- torchvision

## 🎓 Learning Resources

- **LangChain Agents**: https://python.langchain.com/docs/modules/agents/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenRouter API**: https://openrouter.ai/

## ✨ Summary

The chatbot-backend integration is now **fully functional**:
- ✅ No more looping errors
- ✅ Intelligent tool use (only with real paths)
- ✅ Helpful general information when no image provided  
- ✅ Proper JSON tool invocation
- ✅ Multi-turn conversation memory
- ✅ Graceful error handling
- ✅ All tests passing

**The system is ready for use!**
