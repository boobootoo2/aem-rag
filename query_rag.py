#!/usr/bin/env python3
"""
AEM Hybrid RAG Server (LangChain 1.x, OpenAI, FAISS + BM25)
-----------------------------------------------------------
Runs a hybrid retrieval-augmented generation (RAG) pipeline combining
semantic (FAISS) and keyword (BM25) retrievers over AEM content.

Usage:
  python query_rag.py serve
"""

import os, json, faiss
from flask import Flask, request, jsonify
from flask_cors import CORS
from markdown2 import markdown


from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------------------------
# 1️⃣  Environment / Embeddings
# ---------------------------------------------------------------------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ Missing environment variable OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key)

# ---------------------------------------------------------------------
# 2️⃣  Load FAISS vector store
# ---------------------------------------------------------------------
if os.path.isdir("aem_index_store"):
    vectorstore = FAISS.load_local("aem_index_store", embeddings, allow_dangerous_deserialization=True)
elif os.path.exists("aem_index.faiss"):
    index = faiss.read_index("aem_index.faiss")
    with open("aem_index_meta.json", "r", encoding="utf-8") as f:
        docs_meta = json.load(f)
    docs = [Document(page_content=d.get("content", ""), metadata=d) for d in docs_meta]
    vectorstore = FAISS.from_documents(docs, embeddings)
else:
    raise FileNotFoundError("❌ No FAISS index found (expected aem_index_store/ or aem_index.faiss)")

semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

# ---------------------------------------------------------------------
# 3️⃣  BM25 keyword retriever
# ---------------------------------------------------------------------
if os.path.exists("aem_index_meta.json"):
    with open("aem_index_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    texts = [d.get("content", "") for d in meta if d.get("content")]
    keyword_retriever = BM25Retriever.from_texts(texts)
else:
    keyword_retriever = None

# ---------------------------------------------------------------------
# 4️⃣  Hybrid retrieval logic
# ---------------------------------------------------------------------
def hybrid_retrieve(query: str):
    """Retrieve semantically + keyword matched docs and merge."""
    sem_docs = semantic_retriever.invoke(query)
    kw_docs = []
    if keyword_retriever:
        try:
            kw_docs = keyword_retriever.invoke(query)
        except AttributeError:
            kw_docs = keyword_retriever.get_relevant_documents(query)
    all_docs = sem_docs + kw_docs
    print(f"🔍 Retrieved {len(all_docs)} docs (semantic={len(sem_docs)}, keyword={len(kw_docs)})")
    return all_docs

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

# ---------------------------------------------------------------------
# 5️⃣  Dynamic Prompt Builder
# ---------------------------------------------------------------------
def wants_table(question: str) -> bool:
    """Detects if the query implies tabular or list-style output."""
    keywords = ["list", "table", "components", "enumerate", "show", "paths"]
    return any(k in question.lower() for k in keywords)

def build_prompt(question: str, output_json: bool = False) -> ChatPromptTemplate:
    """Builds an appropriate prompt template based on query intent."""
    if output_json:
        return ChatPromptTemplate.from_template("""
You are an assistant returning structured JSON describing Adobe Experience Manager (AEM) components.

Context:
{context}

Question: {question}

Return only valid JSON. Output an array of objects like:
[
  {"name": "componentName", "type": "cq:Component", "path": "/content/we-retail/..."},
  ...
]
""")

    if wants_table(question):
        return ChatPromptTemplate.from_template("""
You are an assistant that extracts structured data about Adobe Experience Manager (AEM) components.

Use the context below to identify relevant items and output a markdown table 
with columns **Name**, **Type**, and **Path** (and any additional fields you can infer).

Context:
{context}

Question: {question}

Output the answer as a Markdown table with headers and no extra commentary.
""")
    else:
        return ChatPromptTemplate.from_template("""
You are an assistant answering questions about Adobe Experience Manager (AEM) content.
Use the context below to answer clearly and concisely.

Context:
{context}

Question: {question}
""")

# ---------------------------------------------------------------------
# 6️⃣  LLM
# ---------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
print("✅ AEM Hybrid RAG system ready (LangChain 1.x).")

# ---------------------------------------------------------------------
# 7️⃣  Flask API
# ---------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------
# Serve static index.html
# ---------------------------------------------------------------------
from flask import send_from_directory

@app.route("/", methods=["GET"])
def serve_index():
    """
    Serves the front-end index.html file (must exist in same folder
    or a 'frontend'/'static' subdirectory).
    """
    possible_paths = ["index.html", "frontend/index.html", "static/index.html"]
    for path in possible_paths:
        if os.path.exists(path):
            directory = os.path.dirname(os.path.abspath(path)) or "."
            filename = os.path.basename(path)
            return send_from_directory(directory, filename)
    return "❌ index.html not found. Place it in project root or ./frontend", 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "gpt-4o-mini"})

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    output_format = data.get("format", "markdown").lower()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    docs = hybrid_retrieve(question)
    context_text = format_docs(docs)
    output_json = (output_format == "json")

    prompt = build_prompt(question, output_json=output_json)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    # Try JSON if requested
    if output_json:
        try:
            parsed = json.loads(answer)
            return jsonify({"answer": parsed})
        except Exception:
            pass

    # ✅ Convert markdown (tables, lists, etc.) to HTML
    html_answer = markdown(answer, extras=["tables"])

    return jsonify({
        "answer": answer,        # raw markdown (optional)
        "html": html_answer      # rendered HTML table
    })
# ---------------------------------------------------------------------
# 8️⃣  CLI Entry Point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        print("🌐 Starting Flask API on http://localhost:8000")
        app.run(host="0.0.0.0", port=8000, debug=True)
    else:
        while True:
            q = input("Ask about AEM content (or 'exit'): ")
            if q.lower() in {"exit", "quit"}:
                break
            docs = hybrid_retrieve(q)
            context_text = format_docs(docs)
            prompt = build_prompt(q)
            chain = prompt | llm | StrOutputParser()
            print("\n🧠", chain.invoke({"context": context_text, "question": q}), "\n")
