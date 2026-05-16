import os
os.environ.setdefault('PYTHONPATH', os.getcwd())
from chatbot.llm import invoke

print('Testing LLM invoke with a short prompt...')
resp = invoke('Say hello in one sentence.')
print('TYPE:', type(resp))
print('CONTENT SNIPPET:', resp.content[:200])
