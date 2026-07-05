import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import PendingFAQ
from app.rag.llm import llm_client

class FAQSynthesizer:
    async def synthesize_and_queue(self, db: AsyncSession, tenant_id: str, clusters: dict):
        """
        Takes clustered queries and generates a single FAQ (question and answer) per cluster.
        Queues them in the PendingFAQ table.
        """
        for cluster_id, data in clusters.items():
            queries = data["queries"]
            size = data["size"]
            
            # Use LLM to synthesize
            prompt = f"""
            Analyze the following cluster of user queries that all relate to the same issue.
            Queries:
            {chr(10).join(queries)}
            
            1. Formulate a single, clear, generalized Question that represents all of these.
            2. Draft a concise, helpful Answer to this question based on general knowledge (this will be reviewed by an admin).
            
            Format your response exactly as:
            QUESTION: <your question>
            ANSWER: <your answer>
            """
            
            # We don't have context here, just asking LLM to summarize/draft
            response = await llm_client.generate(prompt, context="")
            
            # Parse output
            question = "Generated Question"
            answer = "Generated Answer"
            
            for line in response.split("\n"):
                if line.startswith("QUESTION:"):
                    question = line.replace("QUESTION:", "").strip()
                elif line.startswith("ANSWER:"):
                    answer = line.replace("ANSWER:", "").strip()
                    
            # Insert into pending queue
            pending_faq = PendingFAQ(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                cluster_size=str(size),
                question=question,
                suggested_answer=answer
            )
            db.add(pending_faq)
            
        await db.commit()

synthesizer = FAQSynthesizer()
