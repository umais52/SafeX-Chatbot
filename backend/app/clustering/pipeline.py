import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.db.session import AsyncSessionLocal
from app.db.models import BotAnsweredQuestion
from app.clustering.extract import extractor
from app.clustering.cluster import clusterer
from app.clustering.synthesize import synthesizer

async def run_clustering_pipeline(tenant_id: str):
    """
    Orchestrates the FAQ clustering pipeline:
    1. Extract un-clustered questions
    2. Cluster them and find the largest cluster
    3. Synthesize the cluster into a single FAQ
    4. Mark all extracted questions as clustered
    """
    async with AsyncSessionLocal() as db:
        try:
            print(f"INFO:    Starting clustering pipeline for tenant {tenant_id}")
            
            # 1. Extract
            unclustered_qs = await extractor.extract_unclustered_questions(db, tenant_id)
            if not unclustered_qs:
                print("INFO:    No un-clustered questions found. Aborting.")
                return

            # Capture IDs before any commits that could detach the objects
            question_ids = [q.id for q in unclustered_qs]
            question_texts = [q.question for q in unclustered_qs]
            
            # 2. Cluster
            largest_cluster_texts = clusterer.get_largest_cluster(question_texts)
            if not largest_cluster_texts:
                print("INFO:    Could not form a valid cluster. Aborting.")
                return

            print(f"INFO:    Found largest cluster with {len(largest_cluster_texts)} questions.")

            # 3. Synthesize
            await synthesizer.synthesize_faq(
                db=db, 
                tenant_id=tenant_id, 
                cluster_questions=largest_cluster_texts, 
                cluster_size=len(largest_cluster_texts)
            )
            
            # 4. Mark ALL extracted questions as clustered via bulk update
            #    This avoids DetachedInstanceError from expired ORM objects
            await db.execute(
                update(BotAnsweredQuestion)
                .where(BotAnsweredQuestion.id.in_(question_ids))
                .values(is_clustered=True)
            )
            await db.commit()
            print("INFO:    Clustering pipeline completed successfully.")
            
        except Exception as e:
            print(f"ERROR:   Clustering pipeline failed for tenant {tenant_id}: {e}")
            await db.rollback()

if __name__ == "__main__":
    # For testing manually
    asyncio.run(run_clustering_pipeline("default-tenant"))
