from .library import router as library_router
from .liked import router as liked_router
from .search import router as search_router
from .playlists import router as playlists_router

__all__ = ["library_router", "liked_router", "search_router", "playlists_router"]
