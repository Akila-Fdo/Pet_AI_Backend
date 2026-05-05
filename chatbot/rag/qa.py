from chatbot.rag.retriever import get_retriever
from chatbot.llm import llm


retriever = get_retriever()


def ask_rag(question: str):
    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Use the following veterinary knowledge to answer:

{context}

Question:
{question}

Answer clearly and safely.
"""

    response = llm.invoke(prompt)

    return response.content