"""
Memory Store Module for Connor System
Provides enhanced memory storage functionality
"""

from typing import Dict, Any, List, Optional
from .memstore import MemStore


class EnhancedMemoryStore:
    """Enhanced memory store with pattern recognition capabilities"""
    
    def __init__(self, store_path: str = "./memory_store"):
        self.store_path = store_path
        self.memory_cache = {}
        self.access_patterns = {}
    
    def store_memory(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None):
        """Store a memory with metadata"""
        self.memory_cache[key] = {
            "data": data,
            "metadata": metadata or {},
            "access_count": 0,
            "last_accessed": None
        }
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve a stored memory"""
        if key in self.memory_cache:
            self.memory_cache[key]["access_count"] += 1
            return self.memory_cache[key]["data"]
        return None
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories based on query"""
        results = []
        for key, memory in self.memory_cache.items():
            if query.lower() in str(memory["data"]).lower():
                results.append({
                    "key": key,
                    "data": memory["data"],
                    "metadata": memory["metadata"]
                })
        return results[:limit]
    
    def get_access_patterns(self) -> Dict[str, int]:
        """Get memory access patterns"""
        return {key: mem["access_count"] for key, mem in self.memory_cache.items()}
    
    def clear_cache(self):
        """Clear memory cache"""
        self.memory_cache.clear()
        self.access_patterns.clear()