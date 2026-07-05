import pandas as pd
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Escalation

class DataExtractor:
    async def extract_resolved_escalations(self, db: AsyncSession, tenant_id: str) -> pd.DataFrame:
        """
        Extracts all resolved escalations for a tenant to be used for clustering.
        """
        result = await db.execute(
            select(Escalation)
            .where(Escalation.tenant_id == tenant_id, Escalation.status == "resolved")
        )
        escalations = result.scalars().all()
        
        data = []
        for esc in escalations:
            data.append({
                "id": esc.id,
                "query": esc.query,
                "context": esc.context
            })
            
        return pd.DataFrame(data)

extractor = DataExtractor()
