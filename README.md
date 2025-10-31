# 🧠 AEM RAG Indexer

This project builds a **Retrieval-Augmented Generation (RAG)** system on top of **Adobe Experience Manager (AEM)** content.  
It extracts page text from AEM’s JSON (`.infinity.json`) or rendered HTML, flattens it, and indexes it into a vector database for semantic and keyword-based retrieval.

---

## 🚀 Features

- ✅ Extracts all text nodes from AEM’s JCR (via `.infinity.json`)
- 🧩 Supports recursive flattening of nested components (e.g. `contentfragment/text`)
- 🧠 Builds semantic embeddings using **OpenAI** or **HuggingFace**
- 🔍 Hybrid retrieval (Semantic + BM25 keyword search)
- 💬 Query interface powered by **LangChain** and **FAISS**
- 💾 Stores and loads FAISS vector indexes locally (`aem_vector_index`)

---

## 📦 Requirements

- Python **3.9+**
- An OpenAI API key (for embeddings and chat)
- An AEM instance (local or remote) accessible via HTTP
- Installed dependencies:

```bash
pip install -U langchain langchain-community langchain-openai faiss-cpu rank-bm25 requests beautifulsoup4
```

---

## ⚙️ Environment Setup

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

*(Windows PowerShell)*:
```powershell
setx OPENAI_API_KEY "sk-your-key-here"
```

---

## 🧩 Project Structure

```
aem-rag/
│
├── fetch_and_flatten_infinity.py   # Extracts and flattens AEM content
├── build_rag_index.py              # Builds local FAISS vector index
├── query_rag.py                    # Interactive Q&A using hybrid retriever
├── flattened_docs.json             # Output of text extraction
├── aem_vector_index/               # Saved FAISS index
└── README.md                       # You are here
```

---

## 🧠 How It Works

### 1️⃣ Fetch AEM Content
Extract text directly from your AEM instance:

```bash
python3 fetch_and_flatten_infinity.py
```

This script:
- Pulls from `/content/.../infinity.json`
- Recursively walks all nested nodes
- Saves all human-readable strings to `flattened_docs.json`

---

### 2️⃣ Build the RAG Index

```bash
python3 build_rag_index.py
```

This step:
- Splits text into overlapping chunks
- Embeds them using `OpenAIEmbeddings`
- Saves the FAISS vector index to `aem_vector_index/`

Output example:
```
✅ Indexed 69 chunks from 51 AEM nodes.
💾 Saved local FAISS index: aem_vector_index
```

---

### 3️⃣ Query Your AEM Knowledge Base

Run the retrieval chatbot:
```bash
python3 query_rag.py
```

Sample session:
```
✅ AEM Hybrid RAG system ready.

Ask about AEM content (or type 'exit'): Where can I find "Sometimes it can be difficult"?

🧠 That text appears on /content/we-retail/us/en/experience/hours-of-wilderness.html
```

---

## 🔍 How Hybrid Retrieval Works

| Retriever | Strength | Purpose |
|------------|-----------|----------|
| **FAISS (Semantic)** | Finds conceptually similar chunks | Great for paraphrased queries |
| **BM25 (Keyword)** | Finds literal phrase matches | Great for verbatim text |
| **Ensemble (Hybrid)** | Combines both | Most reliable overall |

---

## 🧰 Troubleshooting

| Problem | Cause | Fix |
|----------|--------|-----|
| ❌ “I don’t know.” | Text missing from JSON | Use `fetch_and_flatten_infinity.py` recursive version |
| `ImportError: faiss not found` | Missing FAISS library | Run `pip install faiss-cpu` |
| `401 Invalid API key` | API key missing | Export your OpenAI key via `export OPENAI_API_KEY` |
| No results for literal search | Semantic miss | Use hybrid retriever (already built-in) |

---

## 🧪 Example: Query Output

```
Ask about AEM content (or type 'exit'): What does the 48 hours of wilderness page describe?

🧠 It’s an article about two brothers exploring the Uintas mountain range,
featuring fishing, camping, and photography across a 48-hour trip.
```

---

## 🧭 Future Enhancements

- 🔄 Auto-crawl all child AEM pages under a base path
- 🌐 Index rendered HTML for HTL-driven components
- 💡 Optional embeddings using local Hugging Face models
- 🧰 Integration with Streamlit or Gradio for UI

---

## 🧑‍💻 Author

**John G. Shultz**  