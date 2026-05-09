#!/usr/bin/env python3
"""Check database completion"""
import sys
from pathlib import Path

# Simple check
db_path = Path("chatbot/db/chroma.sqlite3")
if db_path.exists():
    size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"✅ Chroma database exists: {size_mb:.1f} MB")
else:
    print("❌ Database not found")
    sys.exit(1)

# Try to query
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(embedding_function=embeddings, persist_directory="chatbot/db")
    
    # Get count
    collection = db._client.get_or_create_collection("documents")
    count = collection.count()
    print(f"✅ Documents in database: {count}")
    
except Exception as e:
    print(f"⚠️ Could not query: {e}")
