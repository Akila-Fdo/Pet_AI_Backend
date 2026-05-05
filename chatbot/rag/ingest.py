import os
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


DATA_PATH = "rag_output"        # your crawler output
DB_PATH = "chatbot/db"


def load_documents():
    docs = []

    for file in Path(DATA_PATH).glob("*.txt"):
        loader = TextLoader(str(file), encoding="utf-8")
        docs.extend(loader.load())

    print(f"Loaded {len(docs)} documents")
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    print(f"Created {len(chunks)} chunks")
    return chunks


def build_db():
    docs = load_documents()
    chunks = split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    db.persist()
    print("✅ Chroma DB built successfully!")


if __name__ == "__main__":
    build_db()