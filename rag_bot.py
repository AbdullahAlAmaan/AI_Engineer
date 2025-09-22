# 1. Imports
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()  

# 2. Load document
loader = PyPDFLoader("ROADMAP.pdf")
docs = loader.load()

# 3. Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(docs)

# 4. Create embeddings
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 5. Create FAISS vector store 
vectorstore = FAISS.from_documents(chunks, embedding=embedding)

# Save FAISS index to disk
vectorstore.save_local("FAISS_store")

# Reload FAISS index from disk
vectorstore = FAISS.load_local(
    "FAISS_store",
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

# 6. Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 7. Connect retriever + LLM into a QA chain
llm = ChatOllama(model="wizardlm2:latest")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff" 
)

# 8. Test the chatbot
while True:
    query = input("\nAsk me questions: ")
    if query.lower() == "exit":
        break
    answer = qa_chain.invoke(query)
    print("\CHATBOT:", answer)

