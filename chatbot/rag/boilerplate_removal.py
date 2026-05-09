"""
boilerplate_removal.py
----------------------
Cleans extracted web content using jusText + custom rules to remove boilerplate
and extract only main educational/veterinary knowledge.

Removes:
- Navigation menus and footers
- Copyright notices and author metadata
- Cookie notices and quiz links
- All URLs (they add no semantic value)
- Repeated site structure elements

Preserves:
- Main educational and veterinary knowledge
- Important headings and structure
"""

import re
import os
from pathlib import Path
import justext

# Get project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAG_OUTPUT_DIR = BASE_DIR / "rag_output"

# Backup directory for original files
BACKUP_DIR = RAG_OUTPUT_DIR / "backups_original"


# ─────────────────────────────────────────────────────────────────
# Custom cleaning rules
# ─────────────────────────────────────────────────────────────────

def remove_urls(text: str) -> str:
    """Remove all HTTP(S) URLs and mailto links - they add no semantic value."""
    # Remove http(s) URLs
    text = re.sub(r'https?://[^\s\)]+', '', text)
    # Remove mailto links
    text = re.sub(r'mailto:[^\s\)]+', '', text)
    return text


def remove_author_metadata(text: str) -> str:
    """Remove author attribution lines like 'By Nick Roman', 'Reviewed By Laurie Hess'."""
    patterns = [
        r'(?:By|Written by|Author:)[A-Za-z\[\]\(\)\s\.,\-]*(?:\n|$)',  # More flexible author matching
        r'(?:Reviewed by|Reviewed By|Checked by|Editor:)[A-Za-z\[\]\(\)\s\.,\-]*(?:\n|$)',
        r'(?:Edited by|Edited By)[A-Za-z\[\]\(\)\s\.,\-]*(?:\n|$)',
        r'(?:Illustrated by|Illustrated By)[A-Za-z\[\]\(\)\s\.,\-]*(?:\n|$)',
        r'\n\s*(?:BSc|DVM|MRCVS|DACVB|DECAWBM|PhD|MD|RVT)[A-Za-z\s\.,\-]*(?=\n|$)',  # Credentials
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def remove_copyright_and_legal(text: str) -> str:
    """Remove copyright notices, legal disclaimers, and similar boilerplate."""
    patterns = [
        r'©\s*\d{4}.*?(?:\n|$)',  # Copyright symbol with year
        r'Copyright\s+©?\s*\d{4}.*?(?:\n|$)',  # Copyright text
        r'All rights reserved.*?(?:\n|$)',
        r'Terms?\s+(?:of|and)\s+(?:use|service|conditions)',
        r'Privacy Policy',
        r'Disclaimer',
        r'This material is provided for educational purposes',
        r'This content is provided as is',
        r'No part of this publication',
        r'MSD Manual.*?(?:\n|$)',  # Specific to MSD Vet Manual
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def remove_cookie_notices(text: str) -> str:
    """Remove cookie notices and consent forms."""
    patterns = [
        r'.*?cookie.*?(?:\n|$)',
        r'.*?consent.*?(?:\n|$)',
        r'(?:Accept|Reject)\s+(?:all\s+)?cookies?',
        r'.*?(?:preferences|settings).*?cookies?.*?(?:\n|$)',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def remove_navigation_boilerplate(text: str) -> str:
    """Remove common navigation and UI elements."""
    patterns = [
        r'Skip to.*?(?:\n|$)',
        r'Expand all.*?(?:\n|$)',
        r'Collapse all.*?(?:\n|$)',
        r'(?:TABLE OF CONTENTS|IN THIS TOPIC|IN THIS CHAPTER|OTHER TOPICS)',
        r'Home\s*/\s*[A-Za-z\s/]+',  # Breadcrumb navigation
        r'^\s*→\s*',  # Arrow navigation
        r'^\s*←\s*',
        r'(?:Next|Previous|Back|Forward)\s+(?:Page|Article|Section)',
        r'\[\w+\s*/\s*\w+\]',  # [Item / Category] style navigation
        r'Find In Topic',
        r'Multimedia',
        r'PET OWNER VERSION',
        r'PROFESSIONAL VERSION',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def remove_empty_markdown_links(text: str) -> str:
    """Remove markdown links with empty or removed URLs: [text]() → text"""
    # Convert [text]() to just text
    text = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', text)
    # Also handle pipe-separated table of contents links with empty URLs
    text = re.sub(r'\|\s*\[([^\]]+)\]\(\s*\)\s*\|', r'|', text)
    # Clean up leftover pipes
    text = re.sub(r'\|\s*\|\s*', '|', text)
    return text


def remove_empty_lines_and_normalize(text: str) -> str:
    """
    Collapse multiple blank lines, strip excessive whitespace,
    and normalize newlines.
    """
    # Collapse multiple newlines to at most 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove trailing/leading whitespace from each line
    lines = [line.rstrip() for line in text.split('\n')]
    
    # Remove trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()
    
    # Remove leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    
    return '\n'.join(lines)


def custom_clean(text: str) -> str:
    """Apply all custom cleaning rules in sequence."""
    text = remove_urls(text)
    text = remove_author_metadata(text)
    text = remove_copyright_and_legal(text)
    text = remove_cookie_notices(text)
    text = remove_navigation_boilerplate(text)
    text = remove_empty_markdown_links(text)
    text = remove_empty_lines_and_normalize(text)
    return text


# ─────────────────────────────────────────────────────────────────
# jusText extraction
# ─────────────────────────────────────────────────────────────────

def extract_main_content_justext(text: str) -> str:
    """
    Use jusText to extract main content, removing boilerplate.
    
    jusText classifies paragraphs as:
    - neargboilerplate: probably boilerplate
    - boilerplate: definitely boilerplate
    - content: actual content
    - nearcontent: likely content
    """
    try:
        # Parse with jusText
        paragraphs = justext.justext(text, stoplist=justext.get_stoplist("English"))
        
        # Keep only content and nearcontent classes
        content_paragraphs = [
            p.text for p in paragraphs 
            if p.class_type in ('content', 'nearcontent')
        ]
        
        return '\n\n'.join(content_paragraphs)
    except Exception as e:
        print(f"  ⚠ jusText extraction failed: {e}")
        print(f"    Falling back to custom cleaning only...")
        return text


# ─────────────────────────────────────────────────────────────────
# Main processing
# ─────────────────────────────────────────────────────────────────

def clean_file(input_path: Path, output_path: Path, backup_path: Path) -> tuple[int, int, bool]:
    """
    Clean a single file using jusText + custom rules.
    
    Returns: (original_chars, cleaned_chars, success)
    """
    try:
        # Read original content
        original_text = input_path.read_text(encoding='utf-8')
        original_size = len(original_text)
        
        # Step 1: Extract main content with jusText
        main_content = extract_main_content_justext(original_text)
        
        # Step 2: Apply custom cleaning
        cleaned_text = custom_clean(main_content)
        cleaned_size = len(cleaned_text)
        
        # If cleaning removed too much content, use a gentler approach
        if cleaned_size < original_size * 0.1:  # If less than 10% remains
            print(f"    ⚠ Aggressive cleaning removed >90% of content, using gentler approach...")
            cleaned_text = custom_clean(original_text)
            cleaned_size = len(cleaned_text)
        
        # Save to backup
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(original_text, encoding='utf-8')
        
        # Save cleaned version
        output_path.write_text(cleaned_text, encoding='utf-8')
        
        return original_size, cleaned_size, True
        
    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return 0, 0, False


def main():
    """Main entry point: clean all files in rag_output."""
    print(f"\n{'='*70}")
    print(f"  RAG Content Boilerplate Removal")
    print(f"{'='*70}")
    print(f"\nInput directory: {RAG_OUTPUT_DIR}")
    print(f"Backup directory: {BACKUP_DIR}\n")
    
    # Get all .txt files
    txt_files = sorted(RAG_OUTPUT_DIR.glob("*.txt"))
    
    if not txt_files:
        print("❌ No .txt files found in rag_output directory!")
        return
    
    print(f"Found {len(txt_files)} files to clean.\n")
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_original = 0
    total_cleaned = 0
    successful = 0
    failed = 0
    
    for i, input_file in enumerate(txt_files, 1):
        filename = input_file.name
        output_file = input_file  # Overwrite in place
        backup_file = BACKUP_DIR / filename
        
        print(f"[{i}/{len(txt_files)}] {filename}")
        
        orig_size, clean_size, success = clean_file(input_file, output_file, backup_file)
        
        if success:
            reduction_pct = ((orig_size - clean_size) / orig_size * 100) if orig_size > 0 else 0
            print(f"  ✓ {orig_size:,} → {clean_size:,} chars ({reduction_pct:.1f}% removed)")
            total_original += orig_size
            total_cleaned += clean_size
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  Cleaning Complete")
    print(f"{'='*70}")
    print(f"Processed   : {successful}/{len(txt_files)} successful ({failed} failed)")
    print(f"Total size  : {total_original:,} → {total_cleaned:,} chars")
    print(f"Reduction   : {((total_original - total_cleaned) / total_original * 100):.1f}%")
    print(f"Originals backed up in: {BACKUP_DIR}/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
