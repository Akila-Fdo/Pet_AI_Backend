# Quick Reference: Table-Aware RAG Ingestion

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run ingestion
python chatbot/rag/ingest.py
```

Expected time: ~3-5 minutes for 350 files

---

## ⚙️ Configuration

Edit `IngestConfig` in `chatbot/rag/ingest.py`:

```python
@dataclass
class IngestConfig:
    # Paths
    data_path: Path = base_dir / "rag_output_cleaned"  # Input
    db_path: str = "chatbot/db"                         # Output
    
    # Chunking
    prose_chunk_size: int = 512              # Text: 512 chars
    prose_chunk_overlap: int = 100           # Text: 100 chars overlap
    max_table_chunk_rows: int = 10           # Tables: 10 rows max
    table_row_overlap: int = 1               # Tables: 1 row overlap
    
    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Performance
    batch_size: int = 1000
```

### Tuning Presets

**For small datasets / fast processing:**
```python
prose_chunk_size = 256
prose_chunk_overlap = 50
max_table_chunk_rows = 5
```

**For large tables:**
```python
max_table_chunk_rows = 20
table_row_overlap = 2
```

**For better context (slower):**
```python
prose_chunk_size = 1024
prose_chunk_overlap = 200
max_table_chunk_rows = 15
```

---

## 📊 Chunk Types & Metadata

### Table Chunk
```json
{
  "source": "file.txt",
  "chunk_type": "table",
  "chunk_id": "table_0_chunk_0",
  "table_id": "file.txt_table_0",
  "row_start": 0,
  "row_end": 10,
  "total_rows": 25,
  "num_columns": 3,
  "headers": "Drug|Uses|Comments",
  "is_table_chunk": true
}
```

### Prose Chunk
```json
{
  "source": "file.txt",
  "chunk_type": "prose",
  "chunk_id": "prose_0",
  "is_table_chunk": false
}
```

---

## 📈 Output Interpretation

```
✓ Created 2,450 total chunks
  - Table chunks: 520 (21%)
  - Prose chunks: 1,930 (79%)
```

- More table chunks = more structured content
- Prose/table ratio depends on source material
- Typical range: 15-30% tables, 70-85% prose

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| No tables detected | Check markdown format (need `\|...\|` pattern) |
| Slow embedding | Switch to faster model in config |
| High memory | Reduce `batch_size` to 500 |
| Chroma errors | Delete `chatbot/db/` and re-run |
| Import errors | Run `pip install -r requirements.txt` |

---

## 🎯 Output Verification

After running, check:

```bash
# Check database size
du -sh chatbot/db

# Verify chunks created
python -c "
import chromadb
client = chromadb.PersistentClient(path='chatbot/db')
col = client.get_collection('pet_knowledge')
print(f'Total chunks: {col.count()}')
"
```

---

## 🔄 Pipeline Flow

```
Load Files
    ↓
Extract Tables
    ├→ Parse table structure
    ├→ Serialize to semantic text
    └→ Chunk by rows (max 10)
    ↓
Extract Prose
    ├→ Remove table content
    └→ Chunk by sentences
    ↓
Generate Embeddings
    ├→ HuggingFace all-MiniLM-L6-v2
    └→ ~22M params (fast)
    ↓
Store in Chroma
    ├→ Embeddings
    ├→ Metadata
    ├→ Document text
    └→ Unique chunk ID
```

---

## 💡 Key Concepts

### Row Preservation
- Tables split by rows, not mid-row
- Each row stays complete in its chunk
- Headers repeated for context

### Semantic Text
- Tables converted to text: "Table with columns: X, Y. Row 1: X: val1; Y: val2"
- Better for embeddings than raw markdown
- Maintains semantic relationships

### Metadata Filtering
```python
# Later, filter chunks by type:
table_chunks = [c for c in results if c.metadata['is_table_chunk']]
prose_chunks = [c for c in results if not c.metadata['is_table_chunk']]
```

---

## 📝 Example: Adding Custom Tables

If you want to test table handling:

Create `chatbot/rag_output_cleaned/test_table.txt`:
```
# Drug Treatment Table

| Drug | Uses | Comments |
|------|------|----------|
| Amitriptyline | Anxiety, aggression | Has analgesic effects |
| Fluoxetine | Anxiety, OCD | Takes 3-4 weeks |
| Buspirone | Anxiety marking | Low side effects |

This is prose text describing the drugs above...
```

Run pipeline, verify table chunk is created with proper metadata.

---

## 🚀 Next Steps

1. **Run ingestion**: `python chatbot/rag/ingest.py`
2. **Verify database**: Check `chatbot/db` directory created
3. **Test retrieval**: Integrate with your RAG query system
4. **Monitor quality**: Review sample chunks and metadata
5. **Fine-tune**: Adjust config based on results

---

## 📚 Full Documentation

See `RAG_TABLE_AWARE_INGESTION.md` for:
- Detailed architecture explanation
- Configuration best practices
- Performance metrics
- Integration guides
- Troubleshooting guide
- Future enhancements

---

## ✅ Checklist Before Running

- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Input directory exists: `chatbot/rag_output_cleaned/`
- [ ] Have .txt files in input directory
- [ ] ~5 minutes free (or adjust `batch_size` for speed)
- [ ] ~500MB free disk space for Chroma DB

---

## 🆘 Support

**Error**: `ModuleNotFoundError: No module named 'llama_index'`
→ Run: `pip install -r requirements.txt`

**Error**: `No such file or directory: 'chatbot/rag_output_cleaned'`
→ Check data path in IngestConfig, ensure .txt files exist

**Error**: `Chroma: ERROR creating index`
→ Delete `chatbot/db/` directory and retry

---

**Version**: 1.0 | **Date**: 2026-05-09 | **Status**: Production Ready ✅
