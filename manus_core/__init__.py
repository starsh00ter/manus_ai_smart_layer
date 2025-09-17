"""
Manus Core Library

Shared components for both Manus AI projects:
- Database client and connection management
- Caching logic and optimization
- Embedding storage and retrieval
- Routing and coordination logic
- Migration management
- Utility functions

This library ensures consistency and reduces code duplication between projects.
"""

__version__ = "1.0.0"
__author__ = "Manus AI Team"

# Core imports for easy access
from .db.client import get_shared_client, SharedDBClient
from .cache.manager import CacheManager, get_cache_manager
from .embeddings.store import EmbeddingStore, get_embedding_store
from .routing.coordinator import ProjectCoordinator, get_coordinator
from .utils.credits import CreditManager, check_credits, update_credits

__all__ = [
    "get_shared_client",
    "SharedDBClient", 
    "CacheManager",
    "get_cache_manager",
    "EmbeddingStore",
    "get_embedding_store",
    "ProjectCoordinator",
    "get_coordinator",
    "CreditManager",
    "check_credits",
    "update_credits"
]

