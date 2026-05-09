#!/usr/bin/env python3
"""Test full ingestion pipeline on a few files"""

import sys
sys.path.insert(0, '/Users/akilafernando/Documents/GitHub/Pet_AI_Backend')

from pathlib import Path
from chatbot.rag.ingest import build_db
import shutil

# Temporarily move all files except a few for testing
test_dir = Path("/Users/akilafernando/Documents/GitHub/Pet_AI_Backend/chatbot/rag_output_cleaned")
backup_dir = Path("/Users/akilafernando/Documents/GitHub/Pet_AI_Backend/chatbot/rag_output_cleaned_backup")

if not test_dir.exists():
    print(f"❌ Directory not found: {test_dir}")
    sys.exit(1)

# Create backup
if backup_dir.exists():
    print(f"⚠️  Backup already exists, skipping backup creation")
else:
    print(f"Creating backup of all cleaned files...")
    shutil.copytree(test_dir, backup_dir)

# Keep only a few test files
all_files = sorted(test_dir.glob("*.txt"))
test_files = all_files[:5]  # Test with first 5 files
moved_files = []

print(f"\nMoving {len(all_files) - len(test_files)} files to temporary location...")
for file_path in all_files:
    if file_path not in test_files:
        temp_path = backup_dir / file_path.name
        file_path.unlink()
        moved_files.append(file_path.name)

print(f"Kept {len(test_files)} files for testing")
print(f"Files to test:")
for f in test_files:
    print(f"  - {f.name}")

print(f"\n{'='*80}")
print(f"Running ingestion pipeline on {len(test_files)} files...")
print(f"{'='*80}\n")

# Run ingestion
try:
    build_db()
    print("\n✅ Ingestion completed successfully!")
except Exception as e:
    print(f"\n❌ Error during ingestion: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore all files
    print(f"\n{'='*80}")
    print(f"Restoring all cleaned files...")
    for file_path in backup_dir.glob("*.txt"):
        dest = test_dir / file_path.name
        if not dest.exists():
            shutil.copy2(file_path, dest)
    
    print(f"✅ Restored {len(list(backup_dir.glob('*.txt')))} files")
