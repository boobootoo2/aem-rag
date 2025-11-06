#!/usr/bin/env python3
"""
Resumable FAISS index builder for AEM RAG.
- Reads OPENAI_API_KEY from environment.
- Skips entries already embedded if interrupted.
- Displays progress, elapsed time, and ETA.
"""

import os, json, faiss, numpy as np, time
from tqdm import tqdm
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("❌ Please set OPENAI_API_KEY before running.")

INPUT_FILE = "aem_flattened_inventory.jsonl"
INDEX_FILE = "aem_index.faiss"
META_FILE  = "aem_index_meta.json"
STATE_FILE = "index_state.json"

MODEL = "text-embedding-3-large"
BATCH_SIZE = 10   # reduce API overhead

client = OpenAI(api_key=API_KEY)

# ---------------------------------------------------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed": 0, "total": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ---------------------------------------------------------------------
def load_index(dimension):
    if os.path.exists(INDEX_FILE):
        print(f"📂 Loading existing index from {INDEX_FILE}")
        index = faiss.read_index(INDEX_FILE)
    else:
        index = faiss.IndexFlatL2(dimension)
    return index

# ---------------------------------------------------------------------
def build_index():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    total = len(records)
    state = load_state()
    start_idx = state.get("processed", 0)
    print(f"🔄 Resuming from {start_idx}/{total}")

    # load meta and index if continuing
    meta = []
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            meta = json.load(f)

    # determine embedding dimension (2048 for text-embedding-3-large)
    dim = 3072 if "large" in MODEL else 1536
    index = load_index(dim)

    start_time = time.time()
    for i in tqdm(range(start_idx, total, BATCH_SIZE), desc="Embedding"):
        batch = records[i : i + BATCH_SIZE]
        texts = [r["content"] for r in batch if r.get("content")]

        if not texts:
            continue

        try:
            response = client.embeddings.create(model=MODEL, input=texts)
            vectors = [d.embedding for d in response.data]
            arr = np.array(vectors).astype("float32")
            index.add(arr)
            meta.extend(batch)

            # update state
            processed = i + len(batch)
            state["processed"] = processed
            state["total"] = total

            # save every few batches
            if processed % (BATCH_SIZE * 20) == 0:
                faiss.write_index(index, INDEX_FILE)
                with open(META_FILE, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                save_state(state)

                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed else 0
                remaining = total - processed
                eta = remaining / rate if rate else 0
                print(f"💾 Saved progress @ {processed}/{total} ({processed/total*100:.1f}%) • ETA {eta/60:.1f} min")

        except Exception as e:
            print(f"⚠️ Error at batch {i}: {e}")
            save_state(state)
            time.sleep(5)

    # final save
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    save_state({"processed": total, "total": total})

    elapsed = time.time() - start_time
    print(f"✅ Completed {total} embeddings in {elapsed/60:.2f} minutes.")
    print(f"💾 Saved index: {INDEX_FILE}, metadata: {META_FILE}")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    build_index()
