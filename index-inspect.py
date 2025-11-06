from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("aem_vector_index", embeddings, allow_dangerous_deserialization=True)

docs = vectorstore.similarity_search("Sometimes it can be difficult", k=5)
for d in docs:
    print(d.metadata.get("source"), "\n", d.page_content[:200], "\n---")
