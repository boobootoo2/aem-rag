#!/usr/bin/env python3
import requests, json, os
from urllib.parse import urljoin

AEM_HOST = "http://localhost:4502"
AUTH = ("admin", "admin")
OUTPUT_FILE = "aem_index_meta.json"
MAX_DEPTH = 6

BASE_PATHS = [
    "/apps/core",
    "/apps/core-components-examples",
    "/apps/we-retail-communities",
    "/apps/we-retail-screens",
    "/apps/weretail",
    "/apps/wknd-events",
    "/content/we-retail",
    "/content/wknd-events",
    "/conf/we-retail",
    "/conf/wknd-events",
    "/content/dam",
]

# ---------------------------------------------------
def fetch_json(path):
    """Fetch .infinity.json, or merge paginated .N.json fragments if returned."""
    url = urljoin(AEM_HOST, path.strip("/") + ".infinity.json")
    print(f"🔍 Fetching {url}")
    try:
        r = requests.get(url, auth=AUTH, timeout=20)
        r.raise_for_status()
        if "html" in r.headers.get("Content-Type", "").lower():
            print(f"⚠️  {path} returned HTML (login or not accessible)")
            return {}

        data = r.json()
        # Pagination handling
        if isinstance(data, list) and all(isinstance(x, str) and x.endswith(".json") for x in data):
            merged = {}
            for frag in data:
                frag_url = urljoin(AEM_HOST, frag.lstrip("/"))
                print(f"   ↳ Fetching fragment {frag_url}")
                fr = requests.get(frag_url, auth=AUTH, timeout=15)
                fr.raise_for_status()
                merged.update(fr.json())
            data = merged
        return data
    except Exception as e:
        print(f"⚠️  Skipping {path}: {e}")
        return {}

# ---------------------------------------------------
def flatten_jcr(node, path="", depth=0):
    """Recursively flatten node into (content, metadata) pairs."""
    if depth > MAX_DEPTH or not isinstance(node, dict):
        return []
    docs, text_parts = [], []
    for k, v in node.items():
        if isinstance(v, str) and v.strip():
            text_parts.append(f"{k}: {v}")
        elif isinstance(v, (int, float)):
            text_parts.append(f"{k}: {v}")
        elif isinstance(v, dict):
            docs.extend(flatten_jcr(v, f"{path}/{k}" if path else k, depth + 1))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    docs.extend(flatten_jcr(item, f"{path}/{k}[{i}]", depth + 1))
    if text_parts:
        docs.append({
            "content": "\n".join(text_parts),
            "metadata": {
                "path": path,
                "name": os.path.basename(path) or "(root)",
                "jcr:primaryType": node.get("jcr:primaryType", "")
            }
        })
    return docs

# ---------------------------------------------------
def crawl_path(path, depth=0):
    """Recurse into children (.1.json listings) and flatten discovered nodes."""
    if depth > MAX_DEPTH:
        return []
    docs = []
    list_url = f"{AEM_HOST}{path}.1.json"
    try:
        r = requests.get(list_url, auth=AUTH, timeout=15)
        r.raise_for_status()
        children = r.json()
    except Exception as e:
        print(f"⚠️  Could not list {path}: {e}")
        return docs

    for name in children.keys():
        if name.startswith("jcr:") or name.startswith(":"):
            continue
        child_path = f"{path}/{name}"
        data = fetch_json(child_path)
        if data:
            docs.extend(flatten_jcr(data, child_path, depth))
            # Recurse deeper
            docs.extend(crawl_path(child_path, depth + 1))
    return docs

# ---------------------------------------------------
def crawl_aem():
    all_docs = []
    for root in BASE_PATHS:
        print(f"\n🌲 Crawling {root} ...")
        data = fetch_json(root)
        if data:
            all_docs.extend(flatten_jcr(data, root))
        all_docs.extend(crawl_path(root))
    non_empty = [d for d in all_docs if d.get("content","").strip()]
    print(f"\n💾 Writing {len(non_empty)} flattened docs → {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(non_empty, f, ensure_ascii=False, indent=2)
    print("✅ Crawl complete — ready for indexing.")

# ---------------------------------------------------
if __name__ == "__main__":
    crawl_aem()
