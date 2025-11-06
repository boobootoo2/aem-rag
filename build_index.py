#!/usr/bin/env python3
"""
build_index.py
--------------
Reads the flattened AEM export (aem_index_meta.json) and builds a FAISS index.

Usage:
    python build_index.py
"""

import os, json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

INPUT_FILE = "aem_index_meta.json"
OUTPUT_DIR = "aem_index_store"

# ---------------------------------------------------------------------
# 1️⃣  Load flattened JSON
# ---------------------------------------------------------------------
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError("❌ aem_index_meta.json not found — run flatten_infinity.py first.")

print(f"📂 Loading {INPUT_FILE} ...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

total_docs = len(data)
non_empty = [d for d in data if d.get("content", "").strip()]
print(f"✅ Loaded {total_docs} docs ({len(non_empty)} with text content)")

if not non_empty:
    raise ValueError("❌ No non-empty documents found. Check your crawler output.")

# Optional: simple breakdown by top-level path
prefix_counts = {}
for d in non_empty:
    path = d["metadata"].get("path", "")
    if not path:
        continue
    prefix = "/" + path.strip("/").split("/")[1] if "/" in path.strip("/") else path
    prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

print("\n📊 Document distribution by root path:")
for k, v in sorted(prefix_counts.items()):
    print(f"  {k:20s} {v:6d}")

# ---------------------------------------------------------------------
# 2️⃣  Build FAISS index
# ---------------------------------------------------------------------
print("\n⚙️  Building FAISS index (this may take a few minutes)...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

docs = [
    Document(page_content=d["content"], metadata=d["metadata"])
    for d in non_empty
]

vectorstore = FAISS.from_documents(docs, embeddings)
os.makedirs(OUTPUT_DIR, exist_ok=True)
vectorstore.save_local(OUTPUT_DIR)
print(f"\n✅ FAISS index saved to {OUTPUT_DIR}/ ({len(docs)} documents)\n")
