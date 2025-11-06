#!/usr/bin/env python3
import requests
import json
from urllib.parse import urljoin

AEM_HOST = "http://localhost:4502"
AUTH = ("admin", "admin")
OUTPUT_FILE = "aem_flattened_inventory.jsonl"
MAX_DEPTH = 6

# -----------------------------------
# CORE UTILITIES
# -----------------------------------

def fetch_infinity_json(path):
    """Fetch .infinity.json from AEM and return JSON if available."""
    url = urljoin(AEM_HOST, path.strip("/") + ".infinity.json")
    print(f"🔍 Fetching {url}")
    try:
        resp = requests.get(url, auth=AUTH, timeout=20)
        if "html" in resp.headers.get("Content-Type", ""):
            print(f"⚠️  {path} returned HTML (likely not accessible).")
            return {}
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️  Skipping {path}: {e}")
        return {}

def discover_content_roots():
    """Find valid content roots under /content."""
    resp = requests.get(f"{AEM_HOST}/content.1.json", auth=AUTH)
    roots = []
    if resp.ok:
        try:
            data = resp.json()
            for k in data.keys():
                roots.append(f"/content/{k}")
        except Exception as e:
            print(f"⚠️ Failed to parse /content.1.json: {e}")
    print(f"🧭 Discovered content roots: {roots}")
    return roots

def flatten_jcr(obj, path="", depth=0):
    """Recursively flatten all text and structural metadata."""
    if depth > MAX_DEPTH:
        return []
    docs = []

    if isinstance(obj, dict):
        # --- Always include structural properties ---
        structural_fields = [
            "sling:resourceType",
            "cq:template",
            "jcr:title",
            "componentGroup",
            "jcr:description"
        ]
        for key in structural_fields:
            if key in obj and isinstance(obj[key], str):
                docs.append({
                    "path": f"{path}/{key}" if path else key,
                    "content": obj[key]
                })

        # --- Traverse all other properties ---
        for k, v in obj.items():
            new_path = f"{path}/{k}" if path else k
            if isinstance(v, str) and v.strip():
                docs.append({"path": new_path, "content": v.strip()})
            elif isinstance(v, (dict, list)):
                docs.extend(flatten_jcr(v, new_path, depth + 1))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            docs.extend(flatten_jcr(item, f"{path}[{i}]", depth + 1))

    return docs



# -----------------------------------
# MAIN CRAWL
# -----------------------------------

def crawl_path(path, depth=0):
    """Recursively crawl a given AEM path for page content."""
    if depth > MAX_DEPTH:
        return []
    docs = []

    # Fetch immediate children list (.1.json) to discover subnodes
    listing_url = f"{AEM_HOST}{path}.1.json"
    resp = requests.get(listing_url, auth=AUTH)
    if not resp.ok:
        return docs

    try:
        children = resp.json()
    except Exception:
        return docs

    for name in children.keys():
        child_path = f"{path}/{name}"

        # If this looks like a page, crawl its jcr:content
        if not name.startswith("jcr:"):
            jc_path = f"{child_path}/jcr:content"
            data = fetch_infinity_json(jc_path)
            if data:
                flat = flatten_jcr(data, jc_path)
                docs.extend(flat)

            # Recurse deeper
            docs.extend(crawl_path(child_path, depth + 1))
    return docs


def crawl_aem():
    all_docs = []
    roots = discover_content_roots()
    for root in roots:
        print(f"🌲 Crawling {root} ...")
        all_docs.extend(crawl_path(root))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"💾 Saved {len(all_docs)} entries to {OUTPUT_FILE}")
    print("🎯 Ready for embedding + semantic indexing.")

# -----------------------------------
# ENTRY POINT
# -----------------------------------

if __name__ == "__main__":
    crawl_aem()
