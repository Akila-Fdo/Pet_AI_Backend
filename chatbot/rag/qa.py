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
        # Try to use advanced retriever first
        if use_advanced_rag:
            advanced_retriever = get_advanced_retriever()
            
            # Check if advanced retriever is initialized
            if advanced_retriever.semantic_retriever:
                logger.info("Using advanced RAG retriever")
                context = advanced_retriever.get_context(question, top_k=5)
            else:
                logger.info("Advanced retriever not ready, falling back to legacy")
                retriever = get_retriever()
                docs = retriever.invoke(question)
                context = "\n\n".join([doc.page_content for doc in docs])
        else:
            # Use legacy retriever
            logger.info("Using legacy retriever")
            retriever = get_retriever()
            docs = retriever.invoke(question)
            context = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate answer
        prompt = f"""Use the following veterinary knowledge to answer:

{context}

Question:
{question}

Answer clearly and safely."""

        response = llm.invoke(prompt)
        
        return response.content if hasattr(response, "content") else str(response)
    
    except Exception as e:
        logger.error(f"Error in ask_rag: {e}")
        return f"Error processing question: {e}"