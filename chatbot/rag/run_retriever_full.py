from pathlib import Path
from chatbot.rag.retriever import get_retriever

retriever = get_retriever()

queries = [
    "What causes dermatitis in dogs?",
    "Symptoms of ringworm in cats",
    "dog eye infection treatment",
    "why is my dog not eating",
]

out = []
for q in queries:
    out.append("\n" + "="*50)
    out.append(f"QUERY: {q}\n")

    try:
        docs = retriever.invoke(q)
    except Exception as e:
        out.append(f"Retriever invocation error: {e}\n")
        continue

    if not docs:
        out.append("No results returned.\n")
    for i, d in enumerate(docs):
        snippet = d.page_content.replace('\n', ' ')[:1000]
        out.append(f"\n--- Result {i+1} ---\n{snippet}\n")

Path('retriever_full_output.txt').write_text('\n'.join(out), encoding='utf-8')
print('Wrote retriever_full_output.txt')
