"""
Minimal SemanticRetriever stub for compatibility.

The real implementation may live in another module or be provided
by the project's RAG library. This lightweight stub prevents
import-time failures when running tests that only use the legacy
LangChain/Chroma retriever.
"""
from typing import List, Dict


class SemanticRetriever:
    """Compatibility stub exposing `search(query, top_k)`.

    Returns an empty list for now. Implement a real semantic
    retriever if/when LlamaIndex integration is available.
    """

    def __init__(self, index=None):
        self.index = index

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        return []

    def get_context(self, query: str, top_k: int = 5) -> str:
        results = self.search(query, top_k=top_k)
        return "\n\n".join([r.get("content", "") for r in results])
