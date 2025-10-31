import requests, json

def fetch_infinity_json(url):
    print(f"🔍 Fetching {url}")
    resp = requests.get(url, auth=("admin", "admin"))
    resp.raise_for_status()
    return resp.json()

def flatten_jcr(obj, path=""):
    """Recursively flatten **all** nested text and capture long multiline values."""
    docs = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}/{k}" if path else k
            if isinstance(v, str):
                # Trim and store all strings (even multiline)
                text = v.strip()
                if text:
                    docs.append({"path": new_path, "content": text})
            elif isinstance(v, (dict, list)):
                docs.extend(flatten_jcr(v, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            docs.extend(flatten_jcr(item, f"{path}[{i}]"))
    return docs


if __name__ == "__main__":
    url = "http://localhost:4502/content/we-retail/us/en/experience/hours-of-wilderness.infinity.json"
    data = fetch_infinity_json(url)
    flattened = flatten_jcr(data)
    print(f"✅ Extracted {len(flattened)} flattened text fields.")
    with open("flattened_docs.json", "w") as f:
        json.dump(flattened, f, indent=2)
    print("💾 Saved flattened_docs.json")
