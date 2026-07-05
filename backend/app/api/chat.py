from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
import httpx

from app.db.session import get_db
from app.db.models import Escalation
from app.rag.memory import memory_manager
from app.security.pii_masking import pii_masker
from app.security.guardrails import guardrails
# Assume a global vector store for now, in a real app this would be injected
# from app.rag.pipeline import vector_store

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: str

async def trigger_n8n_escalation(escalation_data: dict):
    from app.config import settings
    # Hit the n8n webhook URL
    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.N8N_WEBHOOK_URL, json=escalation_data)
        except Exception as e:
            print(f"Failed to trigger n8n escalation: {e}")

async def check_escalation(confidence_score: float, llm_response: str) -> bool:
    """Check if the query needs human escalation."""
    if confidence_score < 0.5: # Example threshold
        return True
    if "I have forwarded this to our human expert" in llm_response:
        return True
    return False

@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    x_tenant_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Main chat endpoint with streaming response.
    Requires X-Tenant-Id header for data isolation.
    """
    tenant_id = x_tenant_id
    
    # 1. Input Filtering / PII Masking
    if not guardrails.check_input(request.query):
        rejection_msg = guardrails.sanitize_rejected_input()
        async def rejected_response():
            yield rejection_msg
        return StreamingResponse(rejected_response(), media_type="text/plain")
        
    sanitized_query = pii_masker.mask(request.query)

    if len(sanitized_query) > 500:
        raise HTTPException(status_code=400, detail="Query too long. Max 500 characters.")

    # 2. Get or create session
    session_id = await memory_manager.get_or_create_session(db, request.session_id, tenant_id, request.user_id)
    
    # 5 & 6. Generate Response via LangChain
    from app.rag.chain import get_chain_for_session
    
    # We use a UUID for the session if none provided
    actual_session_id = request.session_id or str(uuid.uuid4())
    
    chain = get_chain_for_session(actual_session_id)
    
    # Since the frontend expects a streaming response (SSE/chunks), but ConversationalRetrievalChain
    # doesn't support async streaming out of the box trivially without callbacks,
    # we'll execute it and yield the full answer as one chunk for now, or simulate streaming
    # if it's too fast. Actually, we'll just yield the full answer.
    
    # Run the chain
    result = chain.invoke({"question": sanitized_query})
    answer = result["answer"]
    
    # Extract sources
    source_docs = result.get("source_documents", [])
    sources = [doc.metadata.get("source") for doc in source_docs if "source" in doc.metadata]
    
    # Check fallback condition
    if "I have forwarded this to our human expert" in answer:
        escalation_id = str(uuid.uuid4())
        
        # We don't save escalation to DB anymore since models changed, just trigger n8n
        # (Assuming Escalation model was simplified or we can just send webhook)
        background_tasks.add_task(trigger_n8n_escalation, {
            "escalation_id": escalation_id,
            "tenant_id": tenant_id,
            "user_id": request.user_id,
            "query": sanitized_query,
            "context": "N/A"
        })
        
    async def generate_response():
        # Yielding the full string at once. The frontend handles chunk parsing so a single large chunk is fine.
        yield answer

    return StreamingResponse(generate_response(), media_type="text/plain", headers={"X-Session-Id": actual_session_id})
