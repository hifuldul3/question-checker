"""
EduGuard AI - Modular Embedding Adapter Engine (SentenceTransformers & TF-IDF Fallback)
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from eduguard_config import EMBEDDING_MODEL_NAME


class BaseEmbeddingEngine(ABC):
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Returns embedding matrix of shape (N, D) where N=len(texts)."""
        pass

    @abstractmethod
    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """Returns cosine similarity matrix of shape (N, N)."""
        pass


class SentenceTransformerEngine(BaseEmbeddingEngine):
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        self._load_model()
        return self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        embeddings = self.encode(texts)
        return cosine_similarity(embeddings)


class TFIDFEmbeddingEngine(BaseEmbeddingEngine):
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def encode(self, texts: List[str]) -> np.ndarray:
        return self.vectorizer.fit_transform(texts).toarray()

    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([[]])
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            return cosine_similarity(tfidf_matrix)
        except Exception:
            # Fallback for empty or single char texts
            N = len(texts)
            matrix = np.eye(N)
            return matrix


def get_embedding_engine() -> BaseEmbeddingEngine:
    """
    Factory function to get the embedding engine.
    Tries SentenceTransformers first; if unavailable, falls back to TF-IDF.
    """
    try:
        engine = SentenceTransformerEngine()
        # Test engine instantiation
        engine._load_model()
        return engine
    except Exception as e:
        # Fallback to TF-IDF vectorizer engine
        return TFIDFEmbeddingEngine()
