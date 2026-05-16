import os
from pathlib import Path
os.environ.setdefault('PYTHONPATH', os.getcwd())
from chatbot.rag.qa import ask_rag

q = "What are common causes and treatments for dermatitis in dogs?"
try:
    ans = ask_rag(q)
    out = f"LENGTH: {len(ans) if hasattr(ans, '__len__') else 'unknown'}\n\nREPR:\n{repr(ans)}\n\nTEXT:\n{ans}\n"
except Exception as e:
    out = f"Error: {e}\n"
Path('ask_rag_verbose_output.txt').write_text(out, encoding='utf-8')
print('Wrote ask_rag_verbose_output.txt')
