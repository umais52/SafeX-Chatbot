from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import GeneratedFAQ

router = APIRouter()

@router.get("/")
async def get_faqs(tenant_id: str = "default-tenant", db: AsyncSession = Depends(get_db)):
    """
    Returns all auto-generated FAQs for a tenant.
    """
    result = await db.execute(
        select(GeneratedFAQ)
        .where(GeneratedFAQ.tenant_id == tenant_id)
        .order_by(GeneratedFAQ.created_at.desc())
    )
    faqs = result.scalars().all()
    
    return [
        {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "source_cluster_size": faq.source_cluster_size,
            "created_at": faq.created_at
        }
        for faq in faqs
    ]
