"""Singleton embedding model wrapper. bge-small is small, fast, no API needed."""
import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)

def embed(texts: list[str]) -> np.ndarray:
    """Returns L2-normalized embeddings as a (N, D) array."""
    model = get_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)
