from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from chatbot.llm import llm
from chatbot.tools import analyze_pet_image
from chatbot.memory import memory

tools = [analyze_pet_image]

# ✅ FIX: Modern LangChain prompt with proper structure
system_prompt = """You are a veterinary assistant chatbot.

Your job:
- Help users with pet health concerns (dogs and cats)
- Use disease predictions from image analysis tools when appropriate
- Give simple, safe advice
- Do NOT give dangerous medical advice
- Ask for clarification if needed

When users mention pet health concerns:
- Listen for disease type keywords: skin (dermatitis, fungal, itching, rash) or eye (discharge, redness, squinting)
- Ask for an image if they have one and want a diagnosis
- Use the analyze_pet_image tool ONLY when user provides an image path AND mentions skin/eye disease concern

If disease prediction is provided:
- Explain the condition in simple terms
- Suggest safe actions (e.g., "Visit a vet")
- Suggest what to avoid

Rules:
- Be helpful and friendly
- Use tools when appropriate (only for image analysis)
- Provide safe and clear advice
- If no image path is provided, offer guidance without the tool"""

# ✅ FIX: Create modern ReAct agent with memory and proper tools
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ✅ FIX: Use modern create_react_agent and AgentExecutor
agent_runnable = create_react_agent(llm, tools, prompt)

agent = AgentExecutor(
    agent=agent_runnable,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)