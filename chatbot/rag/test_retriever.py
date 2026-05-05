import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chatbot.rag.retriever import get_retriever

retriever = get_retriever()

queries = [
    "What causes dermatitis in dogs?",
    "Symptoms of ringworm in cats",
    "dog eye infection treatment",
    "why is my dog not eating",
]

for q in queries:
    print("\n" + "="*50)
    print("QUERY:", q)

    docs = retriever.invoke(q)

    for i, d in enumerate(docs):
        print(f"\n--- Result {i+1} ---")
        print(d.page_content[:300])