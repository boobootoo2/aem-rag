import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- Load API key from environment ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ Missing environment variable OPENAI_API_KEY. Run: export OPENAI_API_KEY='sk-...'")

# --- Load flattened docs from AEM ---
with open("flattened_docs.json") as f:
    docs = json.load(f)

texts = [d["content"] for d in docs]
paths = [d["path"] for d in docs]

# --- Split into manageable chunks ---
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
documents = splitter.create_documents(texts, metadatas=[{"source": p} for p in paths])

# --- Create embeddings and FAISS vector store ---
embeddings = OpenAIEmbeddings(api_key=openai_api_key)
vectorstore = FAISS.from_documents(documents, embeddings)

# --- Save local vector index ---
vectorstore.save_local("aem_vector_index")

print(f"✅ Indexed {len(documents)} chunks from {len(docs)} AEM nodes.")
print("💾 Saved local FAISS index: aem_vector_index")
