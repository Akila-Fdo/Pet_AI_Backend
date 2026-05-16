"""
RAG Question-Answering Module

Provides ask_rag() function that:
- Retrieves relevant context
- Generates answers using LLM
- Supports both legacy and advanced retrievers
"""

import logging
from typing import Optional

from chatbot.rag.retriever import get_retriever, get_advanced_retriever
from chatbot.llm import llm


logger = logging.getLogger(__name__)


def ask_rag(
    question: str,
    use_advanced_rag: bool = True,
) -> str:
    """
    Answer question using RAG pipeline
    
    Args:
        question: User question
        use_advanced_rag: Use advanced retriever if available
        
    Returns:
        Answer string
    """
    try:
        # Retrieve context using the advanced retriever when available
        if use_advanced_rag:
            advanced_retriever = get_advanced_retriever()
            if advanced_retriever.semantic_retriever:
                logger.info("Using advanced RAG retriever")
                context = advanced_retriever.get_context(question, top_k=5)
            else:
                logger.info("Advanced retriever not ready, falling back to legacy")
                retriever = get_retriever()
                docs = retriever.invoke(question)
                context = "\n\n".join([doc.page_content for doc in docs])
        else:
            logger.info("Using legacy retriever")
            retriever = get_retriever()
            docs = retriever.invoke(question)
            context = "\n\n".join([doc.page_content for doc in docs])

        # Safety: trim very long context to keep prompt size reasonable
        MAX_CONTEXT_CHARS = 8000
        if context and len(context) > MAX_CONTEXT_CHARS:
            # Keep the most recent/likely relevant tail of the context
            context = context[-MAX_CONTEXT_CHARS:]

        # Build a clear system-style prompt for the LLM
        system_prefix = (
            "You are a veterinary expert assistant. Use the provided context from trusted veterinary sources "
            "to answer the user's question in a clear, safe, and professional manner. If the answer is not in the "
            "context, say you don't know and suggest next diagnostic steps."
        )

        prompt = (
            system_prefix
            + "\n\nCONTEXT:\n" + (context or "<no context available>")
            + "\n\nQUESTION:\n" + question
            + "\n\nAnswer concisely, include references to the context where applicable, and recommend veterinary follow-up when appropriate."
        )

        response = llm.invoke(prompt)

        return response.content if hasattr(response, "content") else str(response)
    
    except Exception as e:
        logger.error(f"Error in ask_rag: {e}")
        return f"Error processing question: {e}"