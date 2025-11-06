import json

def flatten_jcr(json_obj, path=""):
    docs = []

    # If the object is a dictionary
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            new_path = f"{path}/{key}" if path else key
            if isinstance(value, dict):
                # Check if it looks like a content node
                if any(k in value for k in ["jcr:primaryType", "text", "title", "description"]):
                    text_snippet = []
                    for k, v in value.items():
                        if isinstance(v, str) and v.strip():
                            text_snippet.append(f"{k}: {v}")
                    if text_snippet:
                        docs.append({
                            "path": new_path,
                            "content": "\n".join(text_snippet)
                        })
                docs.extend(flatten_jcr(value, new_path))
            elif isinstance(value, list):
                docs.extend(flatten_jcr(value, new_path))

    # If the object is a list
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            docs.extend(flatten_jcr(item, f"{path}[{i}]"))

    return docs


if __name__ == "__main__":
    with open("we-retail.json", "r") as f:
        data = json.load(f)

    docs = flatten_jcr(data)
    print(f"Extracted {len(docs)} content fragments.")
    with open("flattened_docs.json", "w") as f:
        json.dump(docs, f, indent=2)
    print("✅ Saved flattened_docs.json")
