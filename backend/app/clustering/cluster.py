import numpy as np
import math
from sklearn.cluster import KMeans
from app.rag.chain import embeddings
from typing import List

class QueryClusterer:
    def get_largest_cluster(self, queries: List[str]) -> List[str]:
        """
        Clusters a list of query strings and returns the queries in the largest cluster.
        """
        n = len(queries)
        if n == 0:
            return []
        
        # 1. Vectorize queries
        embeddings_list = embeddings.embed_documents(queries)
        embeddings_np = np.array(embeddings_list)
        
        # 2. Determine K = floor(sqrt(n))
        k = max(1, math.floor(math.sqrt(n)))
        if n < 3:
            k = 1
        
        # 3. Cluster
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(embeddings_np)
        
        # Group by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(queries[i])
            
        # 4. Find largest cluster
        largest_cluster = []
        max_size = -1
        for cluster_id, cluster_queries in clusters.items():
            if len(cluster_queries) > max_size:
                max_size = len(cluster_queries)
                largest_cluster = cluster_queries
                
        return largest_cluster

clusterer = QueryClusterer()
