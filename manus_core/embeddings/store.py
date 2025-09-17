#!/usr/bin/env python3

"""
Embedding Store for Manus AI Projects

Provides shared embedding storage and retrieval functionality
for both projects with caching and vector similarity search.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..db.client import get_shared_client
from ..cache.manager import get_cache_manager

class EmbeddingStore:
    """Shared embedding store for both projects"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.db_client = get_shared_client(project_name)
        self.cache = get_cache_manager(project_name)
        
    def store_embedding(self, content: str, embedding: List[float], 
                       model_name: str = "text-embedding-3-small") -> bool:
        """Store an embedding with its content"""
        try:
            # Generate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check if already exists
            existing = self.get_embedding(content_hash)
            if existing:
                return True
            
            # Store in database
            embedding_data = {
                "content_hash": content_hash,
                "content": content,
                "embedding": embedding,
                "model_name": model_name,
                "created_by": self.project_name
            }
            
            result = self.db_client.insert("embeddings_cache", embedding_data, "shared")
            
            if result:
                # Cache for quick access
                self.cache.set(f"embedding_{content_hash}", {
                    "embedding": embedding,
                    "content": content,
                    "model_name": model_name
                }, namespace="embeddings")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error storing embedding: {e}")
            return False
    
    def get_embedding(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get embedding by content hash"""
        try:
            # Check cache first
            cached = self.cache.get(f"embedding_{content_hash}", namespace="embeddings")
            if cached:
                return cached
            
            # Check database
            results = self.db_client.select(
                table="embeddings_cache",
                columns="*",
                filters={"content_hash": content_hash},
                schema="shared",
                limit=1
            )
            
            if results:
                embedding_data = results[0]
                
                # Cache for future use
                self.cache.set(f"embedding_{content_hash}", {
                    "embedding": embedding_data.get("embedding", []),
                    "content": embedding_data.get("content", ""),
                    "model_name": embedding_data.get("model_name", "")
                }, namespace="embeddings")
                
                return embedding_data
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return None
    
    def search_similar(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        try:
            # Use vector search if available
            results = self.db_client.vector_search(
                table="embeddings_cache",
                embedding=query_embedding,
                limit=limit,
                schema="shared"
            )
            
            return results or []
            
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []

# Global embedding store instance
_embedding_stores = {}

def get_embedding_store(project_name: str = "smart_layer") -> EmbeddingStore:
    """Get an embedding store instance"""
    if project_name not in _embedding_stores:
        _embedding_stores[project_name] = EmbeddingStore(project_name)
    
    return _embedding_stores[project_name]

if __name__ == "__main__":
    # Test embedding store
    store = get_embedding_store("test_project")
    
    print("🔍 Testing Embedding Store...")
    
    # Test store and retrieve
    test_content = "This is a test document"
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]  # Dummy embedding
    
    stored = store.store_embedding(test_content, test_embedding)
    print(f"Store embedding: {'✅' if stored else '❌'}")
    
    if stored:
        content_hash = hashlib.md5(test_content.encode()).hexdigest()
        retrieved = store.get_embedding(content_hash)
        print(f"Retrieve embedding: {'✅' if retrieved else '❌'}")
    
    print("✅ Embedding store test complete")

