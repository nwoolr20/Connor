"""
Vector Memory Module for Connor System
Provides vector-based memory operations for enhanced cognitive capabilities
"""

from typing import List, Dict, Any, Optional
import numpy as np


class VectorMemory:
    """Vector-based memory storage and retrieval system"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.vectors = {}
        self.metadata = {}
    
    def store_vector(self, key: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Store a vector with associated metadata"""
        self.vectors[key] = np.array(vector)
        self.metadata[key] = metadata or {}
    
    def retrieve_similar(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most similar vectors to query"""
        if not self.vectors:
            return []
        
        query_vec = np.array(query_vector)
        similarities = {}
        
        for key, vec in self.vectors.items():
            similarity = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
            similarities[key] = similarity
        
        sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return [
            {"key": key, "similarity": sim, "metadata": self.metadata.get(key, {})}
            for key, sim in sorted_results[:top_k]
        ]
    
    def clear(self):
        """Clear all stored vectors"""
        self.vectors.clear()
        self.metadata.clear()