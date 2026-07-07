import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import GeneratedFAQ
from app.rag.chain import llm, retriever
from app.api.escalation import append_to_faq_doc, reingest_docs

class FAQSynthesizer:
    async def synthesize_faq(self, db: AsyncSession, tenant_id: str, cluster_questions: list[str], cluster_size: int):
        """
        Compresses a cluster of questions into a single FAQ, finds the answer via RAG,
        deduplicates, and saves it.
        """
        # 1. Compress into a single question
        prompt = f"""
        Analyze the following cluster of user queries that all relate to the same issue.
        Queries:
        {chr(10).join(cluster_questions)}
        
        Formulate a single, clear, generalized Question that represents all of these queries.
        Respond ONLY with the question string.
        """
        
        response = await llm.ainvoke(prompt)
        synthesized_question = response.content.strip()
        
        # 2. Get answer from RAG
        docs = await retriever.ainvoke(synthesized_question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        answer_prompt = f"""
        You are an expert customer support agent.
        Answer the following question using ONLY the provided context.
        Keep the answer concise and helpful.
        
        Question: {synthesized_question}
        Context:
        {context}
        """
        
        answer_response = await llm.ainvoke(answer_prompt)
        synthesized_answer = answer_response.content.strip()
        
        # 3. Deduplicate against GeneratedFAQ
        result = await db.execute(select(GeneratedFAQ).where(GeneratedFAQ.tenant_id == tenant_id))
        existing_faqs = result.scalars().all()
        
        if existing_faqs:
            existing_questions = "\n".join([f"- {faq.question}" for faq in existing_faqs])
            dedup_prompt = f"""
            Does the new question semantically match any of the existing questions?
            
            New Question: {synthesized_question}
            
            Existing Questions:
            {existing_questions}
            
            Reply ONLY with 'YES' if it matches, or 'NO' if it is a completely new topic.
            """
            
            dedup_response = await llm.ainvoke(dedup_prompt)
            if "YES" in dedup_response.content.upper():
                print(f"INFO:    FAQ '{synthesized_question}' already exists. Skipping.")
                return None
                
        # 4. Save to DB
        new_faq = GeneratedFAQ(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            question=synthesized_question,
            answer=synthesized_answer,
            source_cluster_size=cluster_size
        )
        db.add(new_faq)
        await db.commit()
        
        # 5. Append to safex_faq.txt and re-ingest
        append_to_faq_doc(synthesized_question, synthesized_answer)
        try:
            reingest_docs()
        except Exception as e:
            print(f"ERROR:    Re-ingestion failed during auto-FAQ generation: {e}")
            
        return new_faq

synthesizer = FAQSynthesizer()
