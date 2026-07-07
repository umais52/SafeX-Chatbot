"""
Escalation callback endpoint.
Called by n8n after admin replies on WhatsApp.
Updates the FAQ doc and re-ingests into the vector store.
Email sending to the user is handled entirely by n8n.
"""
import os
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter()

FAQ_DOC_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "safex_faq.txt")


def append_to_faq_doc(question: str, answer: str):
    """Append a new Q&A pair to the FAQ doc file."""
    faq_path = os.path.normpath(FAQ_DOC_PATH)
    with open(faq_path, "a", encoding="utf-8") as f:
        f.write(f"\n\nQ: {question}\nA: {answer}\n")
    print(f"INFO:     Appended new Q&A to {faq_path}")


def reingest_docs():
    """Re-ingest the docs directory into the Chroma vector store."""
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma

    docs_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "docs"))
    chroma_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"))

    print("INFO:     Re-ingesting docs into Chroma...")
    loader = DirectoryLoader(docs_dir, glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()

    if not docs:
        print("WARNING:  No documents found during re-ingestion.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_dir
    )
    print(f"INFO:     Re-ingestion complete. {len(chunks)} chunks indexed.")


@router.post("/resolve")
async def resolve_escalation(request: Request):
    """
    Called by n8n after admin answers on WhatsApp.
    Payload: { "escalation_id": "...", "admin_response": "...", "user_email": "...", "original_question": "..." }
    
    This endpoint:
    1. Appends the Q&A to the FAQ doc
    2. Re-ingests the doc into the vector store
    
    Email sending to the user is handled by n8n, NOT here.
    """
    data = await request.json()

    escalation_id = data.get("escalation_id")
    admin_response = data.get("admin_response")
    original_question = data.get("original_question")
    user_email = data.get("user_email")

    if not admin_response or not original_question:
        return {"status": "error", "message": "Missing admin_response or original_question"}

    # 1. Append new Q&A to the FAQ document
    append_to_faq_doc(original_question, admin_response)

    # 2. Re-ingest all docs into the vector store
    try:
        reingest_docs()
    except Exception as e:
        print(f"ERROR:    Re-ingestion failed: {e}")
        return {"status": "partial", "message": f"FAQ updated but re-ingestion failed: {e}"}

    return {
        "status": "success",
        "message": "FAQ doc updated and vector store re-ingested.",
        "escalation_id": escalation_id,
        "user_email": user_email
    }
