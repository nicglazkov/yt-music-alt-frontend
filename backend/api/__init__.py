from .library import router as library_router
from .liked import router as liked_router
from .search import router as search_router

__all__ = ["library_router", "liked_router", "search_router"]
