from fastapi import APIRouter

from . import community, document, graph, index, query, realtime, summarize

api_router = APIRouter()

api_router.include_router(index.router, prefix="/index", tags=["index"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(summarize.router, prefix="/summarize", tags=["summarize"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(document.router, prefix="/documents", tags=["document"])
api_router.include_router(realtime.router, prefix="/realtime", tags=["realtime"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
