import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.session import get_db
from app.db.models import Escalation
from app.security.webhook_auth import verify_n8n_signature

router = APIRouter()

@router.post("/n8n", dependencies=[Depends(verify_n8n_signature)])
async def n8n_callback(request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Receives callbacks from n8n after an admin responds on WhatsApp.
    Payload should contain { "escalation_id": "...", "admin_response": "..." }
    """
    data = await request.json()
    
    escalation_id = data.get("escalation_id")
    admin_response = data.get("admin_response")
    
    if not escalation_id or not admin_response:
        return {"status": "error", "message": "Missing escalation_id or admin_response"}
        
    # Find escalation
    result = await db.execute(select(Escalation).where(Escalation.id == escalation_id))
    escalation = result.scalars().first()
    
    if not escalation:
        return {"status": "error", "message": "Escalation not found"}
        
    # Update escalation status
    escalation.status = "resolved"
    escalation.resolved_at = datetime.utcnow()
    
    # Normally we would also send this response back to the user via WebSocket
    # or write it to the chat memory so they see it.
    
    await db.commit()
    return {"status": "success"}

# We also need an endpoint for Meta's verification GET request if we expose this API directly
@router.get("/meta-webhook")
async def verify_meta_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    from app.config import settings
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    return {"status": "error", "message": "Verification failed"}
