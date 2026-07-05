import hmac
import hashlib
from fastapi import Request, HTTPException
from app.config import settings

async def verify_n8n_signature(request: Request):
    """
    Dependency to verify HMAC signature from n8n webhook.
    n8n should send an X-N8N-Signature header.
    """
    signature = request.headers.get("X-N8N-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    
    expected_signature = hmac.new(
        settings.N8N_WEBHOOK_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

async def verify_meta_signature(request: Request):
    """
    Dependency to verify X-Hub-Signature-256 from Meta (WhatsApp).
    Used if backend proxies the webhook instead of n8n directly.
    """
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing Meta signature")
        
    try:
        signature = signature_header.split("sha256=")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid signature format")
        
    body = await request.body()
    
    expected_signature = hmac.new(
        settings.WHATSAPP_CLOUD_API_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid Meta signature")
