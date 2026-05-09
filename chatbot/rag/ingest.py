"""
Table-Aware RAG Ingestion Pipeline using LlamaIndex

This module implements intelligent chunking for markdown files with:
- Markdown-aware parsing to detect tables separately from prose
- Table-aware chunking that preserves row/column relationships
- Semantic chunking for prose text
- Rich metadata preservation (source, chunk type, table ID, etc.)
- Hybrid chunking pipeline for optimal RAG performance
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
import chromadb


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class IngestConfig:
    """Configuration for the ingestion pipeline."""
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_path: Path = base_dir / "rag_output_cleaned"
    db_path: str = "chatbot/db"
    
    # Chunking parameters
    prose_chunk_size: int = 512
    prose_chunk_overlap: int = 100
    max_table_chunk_rows: int = 10  # Max rows per table chunk
    table_row_overlap: int = 1  # Rows to repeat between chunks
    
    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Batch processing
    batch_size: int = 1000


class ChunkType(str, Enum):
    """Types of chunks produced by the pipeline."""
    PROSE = "prose"
    TABLE = "table"
    TABLE_HEADER = "table_header"


# ============================================================================
# Table Processing Module
# ============================================================================

class TableProcessor:
    """Handles intelligent chunking and serialization of markdown tables."""
    
    TABLE_PATTERN = re.compile(
        r'\|.+\|.*\n\|[-:\|\s]+\|.*\n(?:\|.+\|\n)*',
        re.MULTILINE
    )
    
    def __init__(self, config: IngestConfig):
        self.config = config
        self.table_counter = 0
    
    def extract_tables(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract markdown tables from text.
        
        Returns:
            List of tuples (table_text, start_position)
        """
        tables = []
        for match in self.TABLE_PATTERN.finditer(text):
            tables.append((match.group(), match.start()))
        return tables
    
    def parse_markdown_table(self, table_text: str) -> Dict[str, Any]:
        """
        Parse markdown table into structured format.
        
        Returns:
            Dict with headers, rows, and metadata
        """
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        # Extract headers
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        
        if not headers:
            return None
        
        # Extract rows
        rows = []
        for line in lines[2:]:  # Skip header and separator
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        
        return {
            'headers': headers,
            'rows': rows,
            'num_rows': len(rows),
            'num_cols': len(headers)
        }
    
    def serialize_table_to_text(
        self,
        headers: List[str],
        rows: List[Dict[str, str]]
    ) -> str:
        """
        Convert table structure to semantically meaningful text for embedding.
        
        This preserves semantic relationships for better vector search.
        """
        lines = [f"Table with columns: {', '.join(headers)}"]
        
        for i, row in enumerate(rows, 1):
            row_text_parts = [f"Row {i}:"]
            for header, value in zip(headers, [row.get(h, '') for h in headers]):
                if value:
                    row_text_parts.append(f"{header}: {value}")
            lines.append("; ".join(row_text_parts))
        
        return " ".join(lines)
    
    def chunk_table(
        self,
        table_data: Dict[str, Any],
        source_file: str,
        table_id: str
    ) -> List[TextNode]:
        """
        Intelligently chunk large tables while preserving structure.
        
        - Keeps rows together (no row splitting)
        - Repeats headers for context in each chunk
        - Creates semantic text for embedding
        """
        chunks = []
        headers = table_data['headers']
        rows = table_data['rows']
        max_rows = self.config.max_table_chunk_rows
        overlap = self.config.table_row_overlap
        
        # Process rows in chunks with overlap
        for i in range(0, len(rows), max_rows - overlap):
            chunk_rows = rows[i:i + max_rows]
            
            if not chunk_rows:
                continue
            
            # Create semantic text
            semantic_text = self.serialize_table_to_text(headers, chunk_rows)
            
            # Create metadata
            chunk_idx = len(chunks)
            chunk_id = f"{table_id}_chunk_{chunk_idx}"
            
            metadata = {
                'source': source_file,
                'chunk_type': ChunkType.TABLE.value,
                'table_id': table_id,
                'chunk_id': chunk_id,
                'row_start': i,
                'row_end': min(i + max_rows, len(rows)),
                'total_rows': len(rows),
                'num_columns': len(headers),
                'headers': '|'.join(headers),
                'is_table_chunk': True
            }
            
            # Create node
            node = TextNode(
                text=semantic_text,
                metadata=metadata,
            )
            chunks.append(node)
        
        return chunks


# ============================================================================
# Prose Processing Module
# ============================================================================

class ProseProcessor:
    """Handles semantic chunking of prose text."""
    
    def __init__(self, config: IngestConfig):
        self.config = config
    
    def remove_tables(self, text: str) -> str:
        """Remove markdown tables from text."""
        table_pattern = re.compile(
            r'\|.+\|.*\n\|[-:\|\s]+\|.*\n(?:\|.+\|\n)*',
            re.MULTILINE
        )
        return table_pattern.sub('', text)
    
    def split_into_chunks(
        self,
        text: str,
        source_file: str
    ) -> List[TextNode]:
        """
        Split prose text into semantic chunks.
        
        Uses simple sentence-based splitting with configurable overlap.
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        chunks = []
        chunk_size = self.config.prose_chunk_size
        overlap = self.config.prose_chunk_overlap
        
        # Split by sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        chunk_idx = 0
        
        for sentence in sentences:
            sent_length = len(sentence)
            
            # Check if adding this sentence exceeds chunk size
            if current_length + sent_length + 1 > chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                metadata = {
                    'source': source_file,
                    'chunk_type': ChunkType.PROSE.value,
                    'chunk_id': f"prose_{chunk_idx}",
                    'is_table_chunk': False
                }
                
                node = TextNode(text=chunk_text, metadata=metadata)
                chunks.append(node)
                
                # Reset with overlap
                # Keep last ~overlap chars worth of sentences
                overlap_words = max(1, overlap // 30)  # ~30 chars per word
                current_chunk = current_chunk[-overlap_words:] if current_chunk else []
                current_length = sum(len(w) for w in current_chunk) + len(current_chunk) - 1
                chunk_idx += 1
            
            current_chunk.append(sentence)
            current_length += sent_length + 1
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            metadata = {
                'source': source_file,
                'chunk_type': ChunkType.PROSE.value,
                'chunk_id': f"prose_{chunk_idx}",
                'is_table_chunk': False
            }
            node = TextNode(text=chunk_text, metadata=metadata)
            chunks.append(node)
        
        return chunks


# ============================================================================
# Main Ingestion Pipeline
# ============================================================================

class HybridRAGIngestionPipeline:
    """
    Main pipeline that orchestrates table-aware and prose chunking.
    
    Architecture:
    1. Load markdown files
    2. Parse using MarkdownElementNodeParser
    3. Process tables with table-aware chunking
    4. Process prose with semantic chunking
    5. Combine and store in vector database with metadata
    """
    
    def __init__(self, config: Optional[IngestConfig] = None):
        self.config = config or IngestConfig()
        self.table_processor = TableProcessor(self.config)
        self.prose_processor = ProseProcessor(self.config)
        self.embed_model = HuggingFaceEmbedding(
            model_name=self.config.embedding_model
        )
        self._setup_chroma()
    
    def _setup_chroma(self):
        """Initialize Chroma vector store."""
        chroma_client = chromadb.PersistentClient(
            path=self.config.db_path
        )
        
        # Get or create collection with metadata support
        self.collection = chroma_client.get_or_create_collection(
            name="pet_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.collection
        )
    
    def _load_documents(self) -> List[Document]:
        """Load all markdown files from data directory."""
        documents = []
        
        for file_path in Path(self.config.data_path).glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = Document(
                    text=content,
                    metadata={
                        'source': file_path.name,
                        'file_path': str(file_path)
                    }
                )
                documents.append(doc)
                print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")
        
        return documents
    
    def _process_document(self, doc: Document) -> List[TextNode]:
        """
        Process a single document with hybrid chunking.
        
        1. Extract and chunk tables
        2. Extract and chunk prose
        3. Combine with proper metadata
        """
        source_file = doc.metadata.get('source', 'unknown')
        text = doc.text
        
        all_nodes = []
        table_count = 0
        
        # Process tables
        tables = self.table_processor.extract_tables(text)
        
        for table_text, _ in tables:
            table_data = self.table_processor.parse_markdown_table(table_text)
            
            if table_data:
                table_id = f"{source_file}_table_{table_count}"
                table_nodes = self.table_processor.chunk_table(
                    table_data,
                    source_file,
                    table_id
                )
                all_nodes.extend(table_nodes)
                table_count += 1
        
        # Process prose (remove tables first)
        prose_text = self.prose_processor.remove_tables(text)
        
        if prose_text.strip():
            prose_nodes = self.prose_processor.split_into_chunks(
                prose_text,
                source_file
            )
            all_nodes.extend(prose_nodes)
        
        return all_nodes
    
    def _generate_chunk_hash(self, text: str, metadata: dict) -> str:
        """Generate unique hash for chunk to avoid duplicates."""
        combined = f"{text}{str(metadata)}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def ingest(self):
        """
        Main ingestion pipeline orchestrator.
        
        Flow:
        1. Load documents
        2. Process with table-aware/prose chunking
        3. Add to vector store with metadata
        4. Persist database
        """
        print("\n" + "="*70)
        print("Starting Table-Aware RAG Ingestion Pipeline")
        print("="*70)
        
        # Load documents
        print("\n📖 Loading documents...")
        documents = self._load_documents()
        print(f"✓ Loaded {len(documents)} documents\n")
        
        if not documents:
            print("✗ No documents found!")
            return
        
        # Process all documents
        print("🔄 Processing documents with hybrid chunking...")
        all_nodes = []
        table_count = 0
        prose_count = 0
        
        for doc in documents:
            nodes = self._process_document(doc)
            
            for node in nodes:
                if node.metadata.get('chunk_type') == ChunkType.TABLE.value:
                    table_count += 1
                else:
                    prose_count += 1
            
            all_nodes.extend(nodes)
            print(f"  ✓ {doc.metadata['source']}: "
                  f"{len(nodes)} chunks ({len([n for n in nodes if n.metadata.get('is_table_chunk')])} table, "
                  f"{len([n for n in nodes if not n.metadata.get('is_table_chunk')])} prose)")
        
        print(f"\n✓ Created {len(all_nodes)} total chunks")
        print(f"  - Table chunks: {table_count}")
        print(f"  - Prose chunks: {prose_count}")
        
        # Store in vector database with metadata
        print("\n💾 Storing in Chroma vector database...")
        
        for i, node in enumerate(all_nodes, 1):
            try:
                # Generate embedding
                embedding = self.embed_model.get_text_embedding(node.text)
                
                # Create unique chunk ID
                chunk_hash = self._generate_chunk_hash(node.text, node.metadata)
                chunk_id = f"{node.metadata.get('chunk_id', f'chunk_{i}')}_{chunk_hash}"
                
                # Add to Chroma collection
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    metadatas=[node.metadata],
                    documents=[node.text]
                )
                
                if i % 100 == 0:
                    print(f"  ✓ Stored {i}/{len(all_nodes)} chunks")
            
            except Exception as e:
                print(f"  ✗ Error storing chunk {i}: {e}")
        
        print(f"✓ Successfully stored {len(all_nodes)} chunks in Chroma\n")
        
        # Verify storage
        try:
            count = self.collection.count()
            print(f"✅ Verification: Chroma contains {count} documents")
            
            # Show metadata statistics
            print("\n📊 Chunk Statistics:")
            table_chunks = sum(1 for n in all_nodes if n.metadata.get('is_table_chunk'))
            prose_chunks = len(all_nodes) - table_chunks
            print(f"  - Total chunks: {len(all_nodes)}")
            print(f"  - Table chunks: {table_chunks} ({100*table_chunks//len(all_nodes) if all_nodes else 0}%)")
            print(f"  - Prose chunks: {prose_chunks} ({100*prose_chunks//len(all_nodes) if all_nodes else 0}%)")
            
            # Sample metadata from different chunk types
            table_sample = next((n for n in all_nodes if n.metadata.get('is_table_chunk')), None)
            prose_sample = next((n for n in all_nodes if not n.metadata.get('is_table_chunk')), None)
            
            if table_sample:
                print(f"\n📋 Sample Table Chunk Metadata:")
                print(f"  Source: {table_sample.metadata.get('source')}")
                print(f"  Type: {table_sample.metadata.get('chunk_type')}")
                print(f"  Table ID: {table_sample.metadata.get('table_id')}")
                print(f"  Rows: {table_sample.metadata.get('row_start')}-{table_sample.metadata.get('row_end')}")
            
            if prose_sample:
                print(f"\n📄 Sample Prose Chunk Metadata:")
                print(f"  Source: {prose_sample.metadata.get('source')}")
                print(f"  Type: {prose_sample.metadata.get('chunk_type')}")
                print(f"  Preview: {prose_sample.text[:100]}...")
            
            print("\n" + "="*70)
            print("✅ Ingestion Complete!")
            print("="*70 + "\n")
        
        except Exception as e:
            print(f"✗ Error verifying database: {e}")


# ============================================================================
# Execution
# ============================================================================

if __name__ == "__main__":
    config = IngestConfig()
    pipeline = HybridRAGIngestionPipeline(config)
    pipeline.ingest()
