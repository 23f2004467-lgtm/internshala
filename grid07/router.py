"""Phase 1: route a post to the bots whose persona facets match."""
from dataclasses import dataclass
from typing import List
import os
import chromadb
from chromadb.config import Settings
from .personas import PERSONAS, Persona
from .embeddings import embed

_client = chromadb.Client(Settings(anonymized_telemetry=False))
_collection = None

@dataclass
class RouteMatch:
    bot_id: str
    name: str
    score: float
    matched_facet: str

def _ensure_collection():
    """Build the in-memory facet collection on first call."""
    global _collection
    if _collection is not None:
        return _collection
    _collection = _client.get_or_create_collection(
        name="bot_facets",
        metadata={"hnsw:space": "cosine"},
    )
    if _collection.count() == 0:
        ids, docs, metas = [], [], []
        for p in PERSONAS:
            for i, facet in enumerate(p.facets):
                ids.append(f"{p.bot_id}:{i}")
                docs.append(facet)
                metas.append({"bot_id": p.bot_id, "name": p.name, "facet_index": i})
        embeddings = embed(docs).tolist()
        _collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)
    return _collection

def route_post_to_bots(
    post_content: str,
    threshold: float | None = None,
) -> List[RouteMatch]:
    """Returns one RouteMatch per bot whose top-matching facet exceeds threshold.

    ChromaDB with `hnsw:space=cosine` returns distance = 1 - cosine_similarity,
    so we recover similarity as `1 - dist`.
    """
    if threshold is None:
        threshold = float(os.getenv("ROUTING_THRESHOLD", "0.62"))
    col = _ensure_collection()
    query_emb = embed([post_content]).tolist()
    # Pull top facet per bot — we have 15 facets total, just fetch all.
    res = col.query(query_embeddings=query_emb, n_results=15, include=["distances", "metadatas", "documents"])

    best_per_bot: dict[str, RouteMatch] = {}
    for dist, meta, doc in zip(res["distances"][0], res["metadatas"][0], res["documents"][0]):
        cos_sim = 1.0 - float(dist)  # ChromaDB cosine "distance" = 1 - cos_sim
        bot_id = meta["bot_id"]
        if bot_id not in best_per_bot or cos_sim > best_per_bot[bot_id].score:
            best_per_bot[bot_id] = RouteMatch(
                bot_id=bot_id,
                name=meta["name"],
                score=cos_sim,
                matched_facet=doc,
            )
    matches = [m for m in best_per_bot.values() if m.score >= threshold]
    matches.sort(key=lambda m: m.score, reverse=True)
    return matches
