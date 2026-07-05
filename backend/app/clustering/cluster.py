import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from app.rag.embeddings import embeddings_client

class QueryClusterer:
    def determine_optimal_k(self, embeddings: np.ndarray, max_k: int = 10) -> int:
        """
        Determines the optimal number of clusters using the Silhouette Score.
        """
        if len(embeddings) < 3:
            return 1 # Not enough data for meaningful clustering
            
        best_k = 2
        best_score = -1
        
        # Max K cannot exceed number of samples - 1
        max_possible_k = min(max_k, len(embeddings) - 1)
        
        for k in range(2, max_possible_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
            cluster_labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, cluster_labels)
            
            if score > best_score:
                best_score = score
                best_k = k
                
        return best_k

    def cluster_queries(self, df: pd.DataFrame) -> dict:
        """
        Clusters the queries and returns groups.
        """
        if df.empty:
            return {}
            
        # 1. Vectorize queries
        queries = df['query'].tolist()
        embeddings_list = embeddings_client.embed_documents(queries)
        embeddings_np = np.array(embeddings_list)
        
        # 2. Determine K
        k = self.determine_optimal_k(embeddings_np)
        
        # 3. Cluster
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        df['cluster'] = kmeans.fit_predict(embeddings_np)
        
        # Group by cluster
        clusters = {}
        for cluster_id, group in df.groupby('cluster'):
            clusters[int(cluster_id)] = {
                "size": len(group),
                "queries": group['query'].tolist()
            }
            
        return clusters

clusterer = QueryClusterer()
