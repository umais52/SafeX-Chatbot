from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import BotAnsweredQuestion

class DataExtractor:
    async def extract_unclustered_questions(self, db: AsyncSession, tenant_id: str) -> List[BotAnsweredQuestion]:
        """
        Extracts all un-clustered bot-answered questions for a tenant.
        """
        result = await db.execute(
            select(BotAnsweredQuestion)
            .where(BotAnsweredQuestion.tenant_id == tenant_id, BotAnsweredQuestion.is_clustered == False)
        )
        return list(result.scalars().all())

extractor = DataExtractor()
