from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

def ingest_docs():
    print("Loading documents from ./docs...")
    loader = DirectoryLoader("./docs", glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()
    
    if not docs:
        print("No documents found in ./docs")
        return
        
    print(f"Loaded {len(docs)} documents.")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")
    
    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Saving to Chroma DB...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Ingestion complete! Chroma DB persisted to ./chroma_db")

if __name__ == "__main__":
    ingest_docs()
