import os, json
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.bm25 import BM25Retriever
from langchain.chains import RetrievalQA

# --- Load API key from environment ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ Missing environment variable OPENAI_API_KEY. Run: export OPENAI_API_KEY='sk-...'")

# --- Load FAISS vector index and embeddings ---
embeddings = OpenAIEmbeddings(api_key=openai_api_key)
vectorstore = FAISS.load_local("aem_vector_index", embeddings, allow_dangerous_deserialization=True)

# --- Build a keyword retriever from the raw text corpus ---
texts = [d["content"] for d in json.load(open("flattened_docs.json"))]
keyword_retriever = BM25Retriever.from_texts(texts)

# --- Build semantic retriever from the FAISS index ---
semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 12})

# --- Combine both (hybrid retrieval) ---
retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, keyword_retriever],
    weights=[0.6, 0.4]  # semantic + keyword
)

# --- Initialize LLM and RAG chain ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

print("✅ AEM Hybrid RAG system ready.\n")

while True:
    query = input("Ask about AEM content (or type 'exit'): ")
    if query.lower() in ["exit", "quit"]:
        break
    result = qa_chain.invoke({"query": query})
    print("\n🧠", result["result"], "\n")
