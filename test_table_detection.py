#!/usr/bin/env python3
"""Test table detection on a real cleaned file"""

import sys
sys.path.insert(0, '/Users/akilafernando/Documents/GitHub/Pet_AI_Backend')

from pathlib import Path
from chatbot.rag.ingest import HybridRAGChunker

# Test on a file we know has tables
test_file = Path("/Users/akilafernando/Documents/GitHub/Pet_AI_Backend/chatbot/rag_output_cleaned/www.msdvetmanual.com__cat-owners__behavior-of-cats__treatment-of-behavior-problems-in-cats.txt")

if not test_file.exists():
    print(f"❌ Test file not found: {test_file}")
    sys.exit(1)

print(f"Testing table detection on: {test_file.name}\n")

# Read file
text = test_file.read_text(encoding='utf-8')
print(f"File size: {len(text)} characters")
print(f"File has {len(text.split(chr(10)))} lines\n")

# Create chunker and process
chunker = HybridRAGChunker()
chunks_with_metadata = chunker.process_file(test_file)

print(f"Total chunks: {len(chunks_with_metadata)}\n")

# Analyze chunks
table_chunks = [c for c in chunks_with_metadata if c[1].chunk_type == 'table']
prose_chunks = [c for c in chunks_with_metadata if c[1].chunk_type == 'prose']

print(f"Table chunks: {len(table_chunks)}")
print(f"Prose chunks: {len(prose_chunks)}\n")

if table_chunks:
    print("=" * 80)
    print("SAMPLE TABLE CHUNKS:")
    print("=" * 80)
    
    for idx, (text_content, metadata) in enumerate(table_chunks[:3]):
        print(f"\n[Table Chunk {idx + 1}]")
        print(f"  Metadata:")
        print(f"    - Table ID: {metadata.table_id}")
        print(f"    - Row Range: {metadata.row_range}")
        print(f"    - Char Count: {metadata.char_count}")
        print(f"  Content Preview:")
        lines = text_content.split('\n')[:5]
        for line in lines:
            print(f"    {line[:100]}")
        if len(text_content.split('\n')) > 5:
            print(f"    ... ({len(text_content.split(chr(10)))} total lines)")
else:
    print("⚠️  No tables detected!")
    print("\nFirst 50 lines of file:")
    for i, line in enumerate(text.split('\n')[:50]):
        if line.strip():
            print(f"{i+1:3d}: {line[:100]}")

print("\n" + "=" * 80)
