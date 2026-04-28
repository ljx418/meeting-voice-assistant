"""
Knowledge base tools for search and ingestion.
"""

import uuid
from datetime import datetime
from typing import Any


# In-memory knowledge store for Phase 0
_kb_store: dict[str, dict[str, Any]] = {}


def kb_search(query: str, top_k: int = 5) -> str:
    """Search the knowledge base for relevant information.

    Args:
        query: Search query string
        top_k: Maximum number of results to return

    Returns:
        Search results as formatted string
    """
    if not query:
        return "Empty query. Please provide a search term."

    query_lower = query.lower()

    # Simple keyword matching for Phase 0
    results = []
    for doc_id, doc in _kb_store.items():
        content_lower = doc["content"].lower()
        # Calculate simple relevance score
        query_words = query_lower.split()
        score = sum(1 for word in query_words if word in content_lower)

        if score > 0:
            results.append({
                "id": doc_id,
                "title": doc.get("title", "Untitled"),
                "score": score,
                "snippet": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        return f"No results found for: {query}\n\nKnowledge base is empty. Use kb_ingest to add documents."

    output = [f"Search results for '{query}' ({len(results)} found):\n"]
    for i, result in enumerate(results[:top_k], 1):
        output.append(f"{i}. [{result['title']}] (score: {result['score']})")
        output.append(f"   ID: {result['id']}")
        output.append(f"   {result['snippet']}\n")

    return "\n".join(output)


def kb_ingest(document: str, title: str = "") -> str:
    """Ingest a document into the knowledge base.

    Args:
        document: Document content to ingest
        title: Optional title for the document

    Returns:
        Success message with document ID
    """
    if not document:
        return "Empty document. Please provide content to ingest."

    doc_id = str(uuid.uuid4())[:8]

    _kb_store[doc_id] = {
        "id": doc_id,
        "title": title or f"Document-{doc_id}",
        "content": document,
        "ingested_at": datetime.now().isoformat(),
    }

    return f"Document ingested successfully.\nID: {doc_id}\nTitle: {title or 'Untitled'}\nCharacters: {len(document)}"


def kb_list() -> str:
    """List all documents in the knowledge base.

    Returns:
        List of document IDs and titles
    """
    if not _kb_store:
        return "Knowledge base is empty."

    output = [f"Knowledge base ({len(_kb_store)} documents):\n"]
    for doc_id, doc in _kb_store.items():
        output.append(f"- {doc_id}: {doc['title']} (ingested: {doc['ingested_at'][:10]})")

    return "\n".join(output)


def kb_get(doc_id: str) -> str:
    """Get a specific document by ID.

    Args:
        doc_id: Document ID

    Returns:
        Document content or error
    """
    if doc_id not in _kb_store:
        return f"Document not found: {doc_id}"

    doc = _kb_store[doc_id]
    return f"Title: {doc['title']}\nID: {doc['id']}\nIngested: {doc['ingested_at']}\n\n{doc['content']}"


def kb_delete(doc_id: str) -> str:
    """Delete a document from the knowledge base.

    Args:
        doc_id: Document ID to delete

    Returns:
        Success or error message
    """
    if doc_id not in _kb_store:
        return f"Document not found: {doc_id}"

    del _kb_store[doc_id]
    return f"Document deleted: {doc_id}"
