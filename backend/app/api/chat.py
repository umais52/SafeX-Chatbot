from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
import re
import httpx

from app.db.session import get_db
from app.db.models import BotAnsweredQuestion
from app.rag.memory import memory_manager
from app.security.pii_masking import pii_masker
from app.security.guardrails import guardrails
from sqlalchemy import select, func
from app.config import settings
from app.clustering.pipeline import run_clustering_pipeline

router = APIRouter()

# ── Escalation trigger phrase (must match the LLM prompt in chain.py) ──
ESCALATION_TRIGGER = "The answer to this question is not available in the context provided by SafeX"

# ── Per-session pending escalation storage ──
# Maps session_id -> the original question that the bot could not answer
_pending_escalations: Dict[str, str] = {}

# Simple email regex
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: str


async def trigger_n8n_escalation(escalation_data: dict):
    from app.config import settings
    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.N8N_WEBHOOK_URL, json=escalation_data, timeout=30.0)
        except Exception as e:
            print(f"Failed to trigger n8n escalation: {e}")


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
    actual_session_id = request.session_id or str(uuid.uuid4())

    # 1. Input Filtering / PII Masking
    if not guardrails.check_input(request.query):
        rejection_msg = guardrails.sanitize_rejected_input()
        async def rejected_response():
            yield rejection_msg
        return StreamingResponse(rejected_response(), media_type="text/plain")

    sanitized_query = pii_masker.mask(request.query)

    if len(sanitized_query) > 500:
        raise HTTPException(status_code=400, detail="Query too long. Max 500 characters.")

    # 2. Check if this session has a pending escalation waiting for an email
    if actual_session_id in _pending_escalations:
        email_match = EMAIL_RE.search(sanitized_query)
        if email_match:
            user_email = email_match.group(0)
            original_question = _pending_escalations.pop(actual_session_id)
            escalation_id = str(uuid.uuid4())

            # Trigger n8n webhook in background
            background_tasks.add_task(trigger_n8n_escalation, {
                "escalation_id": escalation_id,
                "tenant_id": tenant_id,
                "user_id": request.user_id,
                "user_email": user_email,
                "original_question": original_question,
            })

            confirmation = (
                f"Your question has been sent to our admin team. "
                f"The response will be sent to your email at **{user_email}**. "
                f"Thanks for your patience! 🙏"
            )

            async def escalation_confirmed():
                yield confirmation
            return StreamingResponse(escalation_confirmed(), media_type="text/plain",
                                     headers={"X-Session-Id": actual_session_id})

    # 3. Get or create session
    session_id = await memory_manager.get_or_create_session(db, request.session_id, tenant_id, request.user_id)

    # 4. Generate Response via LangChain
    from app.rag.chain import get_chain_for_session

    chain = get_chain_for_session(actual_session_id)
    result = chain.invoke({"question": sanitized_query})
    answer = result["answer"]

    # 5. Check if the answer is an escalation (bot couldn't answer)
    if ESCALATION_TRIGGER in answer:
        # Store the original question so we can pick it up when the user provides email
        _pending_escalations[actual_session_id] = sanitized_query
    else:
        # Successful answer: store for clustering
        new_q = BotAnsweredQuestion(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            session_id=actual_session_id,
            question=sanitized_query,
            answer=answer
        )
        db.add(new_q)
        await db.commit()
        
        # Check threshold
        count_result = await db.execute(
            select(func.count())
            .select_from(BotAnsweredQuestion)
            .where(BotAnsweredQuestion.tenant_id == tenant_id, BotAnsweredQuestion.is_clustered == False)
        )
        unclustered_count = count_result.scalar()
        
        if unclustered_count >= settings.CLUSTERING_QUESTION_THRESHOLD:
            # Trigger clustering pipeline in background
            background_tasks.add_task(run_clustering_pipeline, tenant_id)

    async def generate_response():
        yield answer

    return StreamingResponse(generate_response(), media_type="text/plain",
                             headers={"X-Session-Id": actual_session_id})
