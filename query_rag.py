import os, json
from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.bm25 import BM25Retriever
from langchain.chains import RetrievalQA
from flask_cors import CORS


# --- Load API key ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ Missing environment variable OPENAI_API_KEY. Run: export OPENAI_API_KEY='sk-...'")

# --- Load FAISS vector index ---
embeddings = OpenAIEmbeddings(api_key=openai_api_key)
vectorstore = FAISS.load_local("aem_vector_index", embeddings, allow_dangerous_deserialization=True)

# --- Build keyword retriever ---
texts = [d["content"] for d in json.load(open("flattened_docs.json"))]
keyword_retriever = BM25Retriever.from_texts(texts)

# --- Build semantic retriever ---
semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 12})

# --- Combine both (hybrid) ---
retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, keyword_retriever],
    weights=[0.6, 0.4]
)

# --- Initialize LLM + QA chain ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

print("✅ AEM Hybrid RAG system ready.")

# --- Flask setup ---
app = Flask(__name__)
CORS(app)


@app.route("/query", methods=["POST"])
def query():
    """POST endpoint for the HTML frontend"""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Missing 'question' in request"}), 400
        result = qa_chain.invoke({"query": question})
        return jsonify({
            "answer": result["result"],
            "sources": [],
            "confidence": "n/a"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Dual mode: CLI + Flask ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        print("🌐 Starting Flask API on http://localhost:8000")
        app.run(host="0.0.0.0", port=8000, debug=True)
    else:
        while True:
            query = input("Ask about AEM content (or type 'exit'): ")
            if query.lower() in ["exit", "quit"]:
                break
            result = qa_chain.invoke({"query": query})
            print("\n🧠", result["result"], "\n")
