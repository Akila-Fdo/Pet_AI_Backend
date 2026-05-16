import os
from pathlib import Path

# Ensure repo root is on PYTHONPATH when running from tools
os.environ.setdefault('PYTHONPATH', os.getcwd())

from chatbot.rag.qa import ask_rag

question = "What are common causes and treatments for dermatitis in dogs?"

try:
    answer = ask_rag(question)
    out = f"QUESTION: {question}\n\nANSWER:\n{answer}\n"
except Exception as e:
    out = f"Error calling ask_rag: {e}\n"

Path('ask_rag_output.txt').write_text(out, encoding='utf-8')
print('Wrote ask_rag_output.txt')
