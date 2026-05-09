"""
Table-Aware RAG Ingestion Pipeline
Hybrid chunking for both tables and prose text using Docling
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "rag_output_cleaned"  # Use cleaned files
DB_PATH = "chatbot/db"

# Chunking config
PROSE_CHUNK_SIZE = 800       # Characters for prose text
PROSE_CHUNK_OVERLAP = 150    # Overlap for prose semantic continuity
TABLE_CHUNK_SIZE = 5000      # Max chars per table chunk (multiple rows)
BATCH_SIZE = 1000            # Vector DB batch size


# ─────────────────────────────────────────────────────────────────
# Data Classes for Metadata
# ─────────────────────────────────────────────────────────────────

@dataclass
class ChunkMetadata:
    """Metadata for each chunk"""
    source_file: str          # Original filename
    chunk_type: str          # 'table' or 'prose'
    chunk_id: int            # Sequential ID
    section: Optional[str]   # Section heading if available
    table_id: Optional[int]  # Table index if chunk_type='table'
    row_range: Optional[str] # "rows 1-5" for tables
    has_header: bool         # Whether chunk includes table header
    char_count: int          # Characters in chunk
    
    def to_dict(self):
        return asdict(self)


# ─────────────────────────────────────────────────────────────────
# Table Detection & Parsing
# ─────────────────────────────────────────────────────────────────

class MarkdownTableParser:
    """Parse and chunk markdown tables intelligently"""
    
    @staticmethod
    def extract_tables(text: str) -> List[Dict]:
        """
        Extract markdown tables from text.
        Handles single-line flattened tables where header|separator|rows are all on one line.
        """
        tables = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip non-table lines
            if not line.startswith('|'):
                i += 1
                continue
            
            # Split by pipe and clean up
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]  # Remove empty cells
            
            # Need at least 2 cells
            if len(cells) < 2:
                i += 1
                continue
            
            # Find separator pattern in cells (---, :--:, ---, etc.)
            separator_indices = []
            for idx, cell in enumerate(cells):
                if re.match(r'^[:\-]+$', cell):
                    separator_indices.append(idx)
            
            # If no separator found, skip
            if not separator_indices:
                i += 1
                continue
            
            # The first separator marks where the separator pattern ends
            # Number of columns = index of first separator
            num_cols = separator_indices[0]
            
            # Sanity check
            if num_cols < 2:
                i += 1
                continue
            
            # Extract headers
            headers = cells[:num_cols]
            
            # Extract rows (skip the separator cells)
            rows = []
            
            # After num_cols header cells, there should be num_cols separator cells
            # So data rows start at index 2 * num_cols
            row_start_idx = 2 * num_cols
            
            current_row = []
            for cell_idx in range(row_start_idx, len(cells)):
                cell = cells[cell_idx]
                current_row.append(cell)
                
                # When we have enough cells for a complete row, save it
                if len(current_row) == num_cols:
                    if any(c.strip() for c in current_row):  # Only add if has content
                        rows.append(current_row[:])
                    current_row = []
            
            # Add remaining cells as final row if incomplete
            if current_row and any(c.strip() for c in current_row):
                # Pad with empty strings
                while len(current_row) < num_cols:
                    current_row.append('')
                rows.append(current_row)
            
            # Check for additional rows in following lines
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                
                if not next_line.startswith('|'):
                    # End of table
                    break
                
                # Parse next line
                next_cells = [c.strip() for c in next_line.split('|')]
                next_cells = [c for c in next_cells if c]
                
                # Skip if it contains separators
                if any(re.match(r'^[:\-]+$', c) for c in next_cells):
                    # Encountered another separator, end table
                    break
                
                # Add cells from this line
                for cell in next_cells:
                    current_row.append(cell)
                    
                    if len(current_row) == num_cols:
                        if any(c.strip() for c in current_row):
                            rows.append(current_row[:])
                        current_row = []
                
                j += 1
            
            # Add incomplete final row
            if current_row:
                while len(current_row) < num_cols:
                    current_row.append('')
                if any(c.strip() for c in current_row):
                    rows.append(current_row)
            
            # Only add if we have valid table
            if rows and len(headers) >= 2:
                tables.append({
                    'headers': headers,
                    'rows': rows,
                    'original_text': '\n'.join(lines[i:j]) if j > i + 1 else line,
                    'start_pos': i,
                    'end_pos': j
                })
                i = j
            else:
                i += 1
        
        return tables
    
    @staticmethod
    def serialize_table_row(headers: List[str], row: List[str]) -> str:
        """Convert table row to semantic text for embedding"""
        pairs = []
        for header, cell in zip(headers, row):
            if cell.strip():  # Only include non-empty cells
                pairs.append(f"{header}: {cell}")
        return " | ".join(pairs)
    
    @staticmethod
    def serialize_table(headers: List[str], rows: List[List[str]]) -> str:
        """Convert entire table to semantic text"""
        serialized = []
        
        # Add header summary
        header_text = " | ".join(headers)
        serialized.append(f"Table columns: {header_text}")
        
        # Serialize each row
        for row in rows:
            serialized.append(MarkdownTableParser.serialize_table_row(headers, row))
        
        return "\n".join(serialized)


# ─────────────────────────────────────────────────────────────────
# Intelligent Table Chunking
# ─────────────────────────────────────────────────────────────────

class TableChunker:
    """Intelligently chunk tables while preserving structure"""
    
    @staticmethod
    def chunk_table(
        headers: List[str],
        rows: List[List[str]],
        table_id: int,
        max_chunk_size: int = TABLE_CHUNK_SIZE
    ) -> List[Dict]:
        """
        Chunk table rows intelligently:
        - Preserve row integrity (no row splitting)
        - Repeat headers in each chunk
        - Maintain relationships
        """
        chunks = []
        
        # Serialize header for reuse
        header_text = " | ".join(headers)
        header_serialized = f"Table columns: {header_text}\n"
        
        current_chunk_rows = []
        current_chunk_text = header_serialized
        
        for row_idx, row in enumerate(rows):
            # Serialize this row
            row_text = MarkdownTableParser.serialize_table_row(headers, row)
            row_text_with_newline = row_text + "\n"
            
            # Check if adding this row exceeds limit
            if (len(current_chunk_text) + len(row_text_with_newline) > max_chunk_size
                and current_chunk_rows):
                # Save current chunk
                chunks.append({
                    'text': current_chunk_text.strip(),
                    'row_range': f"rows {len(chunks) * len(current_chunk_rows)}-"
                                 f"{len(chunks) * len(current_chunk_rows) + len(current_chunk_rows) - 1}",
                    'row_count': len(current_chunk_rows),
                    'has_header': True
                })
                
                # Start new chunk with header
                current_chunk_rows = []
                current_chunk_text = header_serialized
            
            # Add row to current chunk
            current_chunk_rows.append(row)
            current_chunk_text += row_text_with_newline
        
        # Save final chunk
        if current_chunk_rows:
            chunks.append({
                'text': current_chunk_text.strip(),
                'row_range': f"rows {len(rows) - len(current_chunk_rows)}-{len(rows) - 1}",
                'row_count': len(current_chunk_rows),
                'has_header': True
            })
        
        return chunks


# ─────────────────────────────────────────────────────────────────
# Prose Text Chunking
# ─────────────────────────────────────────────────────────────────

class ProseChunker:
    """Semantically chunk prose text"""
    
    def __init__(
        self,
        chunk_size: int = PROSE_CHUNK_SIZE,
        chunk_overlap: int = PROSE_CHUNK_OVERLAP
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        if len(text) < 100:
            return [text]
        
        docs = self.splitter.split_text(text)
        return [d for d in docs if d.strip()]


# ─────────────────────────────────────────────────────────────────
# Hybrid Pipeline
# ─────────────────────────────────────────────────────────────────

class HybridRAGChunker:
    """Hybrid pipeline: tables + prose"""
    
    def __init__(self):
        self.table_parser = MarkdownTableParser()
        self.table_chunker = TableChunker()
        self.prose_chunker = ProseChunker()
    
    def process_file(self, file_path: Path) -> List[Tuple[str, ChunkMetadata]]:
        """
        Process a single file:
        1. Extract tables
        2. Chunk tables intelligently
        3. Chunk remaining prose
        4. Return chunks with metadata
        """
        chunks_with_metadata = []
        
        # Read file
        text = file_path.read_text(encoding='utf-8')
        filename = file_path.name
        lines = text.split('\n')
        
        # Extract tables (with line indices)
        tables = self.table_parser.extract_tables(text)
        
        if not tables:
            # No tables - just chunk prose
            prose_chunks = self.prose_chunker.chunk_text(text)
            for i, chunk in enumerate(prose_chunks):
                metadata = ChunkMetadata(
                    source_file=filename,
                    chunk_type='prose',
                    chunk_id=i,
                    section=None,
                    table_id=None,
                    row_range=None,
                    has_header=False,
                    char_count=len(chunk)
                )
                chunks_with_metadata.append((chunk, metadata))
        else:
            # Has tables - process carefully
            chunk_id = 0
            processed_lines = set()  # Track which lines are part of tables
            
            # Mark table lines as processed
            table_line_ranges = []
            for table in tables:
                table_line_ranges.append((table['start_pos'], table['end_pos']))
                for line_idx in range(table['start_pos'], table['end_pos']):
                    processed_lines.add(line_idx)
            
            # Process content in order
            for table_idx, table in enumerate(tables):
                table_start_line = table['start_pos']
                
                # Get prose before this table
                prose_lines = []
                for line_idx in range(0 if table_idx == 0 else tables[table_idx-1]['end_pos'], 
                                     table_start_line):
                    if line_idx not in processed_lines:
                        prose_lines.append(lines[line_idx])
                
                prose_before = '\n'.join(prose_lines)
                if prose_before.strip():
                    prose_chunks = self.prose_chunker.chunk_text(prose_before)
                    for prose_chunk in prose_chunks:
                        if prose_chunk.strip():
                            metadata = ChunkMetadata(
                                source_file=filename,
                                chunk_type='prose',
                                chunk_id=chunk_id,
                                section=None,
                                table_id=None,
                                row_range=None,
                                has_header=False,
                                char_count=len(prose_chunk)
                            )
                            chunks_with_metadata.append((prose_chunk, metadata))
                            chunk_id += 1
                
                # Process table
                table_chunks = self.table_chunker.chunk_table(
                    table['headers'],
                    table['rows'],
                    table_idx
                )
                
                for sub_chunk_idx, table_chunk in enumerate(table_chunks):
                    metadata = ChunkMetadata(
                        source_file=filename,
                        chunk_type='table',
                        chunk_id=chunk_id,
                        section=None,
                        table_id=table_idx,
                        row_range=table_chunk['row_range'],
                        has_header=table_chunk['has_header'],
                        char_count=len(table_chunk['text'])
                    )
                    chunks_with_metadata.append((table_chunk['text'], metadata))
                    chunk_id += 1
            
            # Process prose after last table
            if tables:
                prose_lines = []
                last_table_end = tables[-1]['end_pos']
                for line_idx in range(last_table_end, len(lines)):
                    if line_idx not in processed_lines:
                        prose_lines.append(lines[line_idx])
                
                prose_after = '\n'.join(prose_lines)
                if prose_after.strip():
                    prose_chunks = self.prose_chunker.chunk_text(prose_after)
                    for prose_chunk in prose_chunks:
                        if prose_chunk.strip():
                            metadata = ChunkMetadata(
                                source_file=filename,
                                chunk_type='prose',
                                chunk_id=chunk_id,
                                section=None,
                                table_id=None,
                                row_range=None,
                                has_header=False,
                                char_count=len(prose_chunk)
                            )
                            chunks_with_metadata.append((prose_chunk, metadata))
                            chunk_id += 1
        
        return chunks_with_metadata
    
    def process_all_files(self, data_path: Path) -> List[Tuple[str, ChunkMetadata]]:
        """Process all markdown files in directory"""
        all_chunks = []
        
        files = sorted(data_path.glob("*.txt"))
        print(f"\n{'='*80}")
        print(f"  HYBRID TABLE-AWARE CHUNKING PIPELINE")
        print(f"{'='*80}\n")
        print(f"Processing {len(files)} files from {data_path}\n")
        
        for idx, file_path in enumerate(files, 1):
            try:
                file_chunks = self.process_file(file_path)
                all_chunks.extend(file_chunks)
                
                table_chunks = sum(1 for _, meta in file_chunks if meta.chunk_type == 'table')
                prose_chunks = sum(1 for _, meta in file_chunks if meta.chunk_type == 'prose')
                
                print(f"[{idx:3d}] {file_path.name}")
                print(f"      Chunks: {len(file_chunks)} (tables: {table_chunks}, prose: {prose_chunks})")
                
            except Exception as e:
                print(f"[{idx:3d}] ✗ ERROR: {file_path.name} - {e}")
        
        print(f"\n{'='*80}")
        print(f"Total chunks created: {len(all_chunks)}")
        print(f"{'='*80}\n")
        
        return all_chunks


# ─────────────────────────────────────────────────────────────────
# Document Loading
# ─────────────────────────────────────────────────────────────────

def load_documents_with_table_awareness():
    """Load documents using hybrid table-aware chunking"""
    chunker = HybridRAGChunker()
    chunks_with_metadata = chunker.process_all_files(DATA_PATH)
    
    # Convert to LangChain Documents with metadata
    documents = []
    for chunk_text, metadata in chunks_with_metadata:
        doc = Document(
            page_content=chunk_text,
            metadata=metadata.to_dict()
        )
        documents.append(doc)
    
    print(f"\nLoaded {len(documents)} documents with metadata")
    return documents


# ─────────────────────────────────────────────────────────────────
# Vector DB Storage
# ─────────────────────────────────────────────────────────────────

def build_db():
    """Build Chroma database with table-aware chunks"""
    
    # Load documents
    docs = load_documents_with_table_awareness()
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create database
    db = Chroma(
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )
    
    print(f"\nStoring {len(docs)} documents in batches (size={BATCH_SIZE})...")
    
    for i in range(0, len(docs), BATCH_SIZE):
        batch = docs[i:i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}: Storing {len(batch)} documents...")
        db.add_documents(batch)
    
    db.persist()
    
    print(f"\n✅ Chroma DB built successfully!")
    print(f"   Location: {DB_PATH}")
    print(f"   Total documents: {len(docs)}")
    
    # Print statistics
    table_docs = sum(1 for doc in docs if doc.metadata.get('chunk_type') == 'table')
    prose_docs = len(docs) - table_docs
    
    print(f"\nDocument Statistics:")
    print(f"   Table chunks: {table_docs}")
    print(f"   Prose chunks: {prose_docs}")


if __name__ == "__main__":
    build_db()