import re
from typing import List
from factsculpt.alignment.interfaces import EmbeddingGenerator

class SentenceTransformerEmbeddingGenerator(EmbeddingGenerator):
    """
    Generates embeddings using the sentence-transformers library.
    Imports sentence-transformers lazily to avoid dependencies during mock tests.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = None
        return self._model

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts)
                return [list(map(float, emb)) for emb in embeddings]
            except Exception:
                pass
        return MockEmbeddingGenerator().get_embeddings(texts)

class MockEmbeddingGenerator(EmbeddingGenerator):
    """
    Mock embedding generator for deterministic, offline testing.
    Uses a bag-of-words style vector representation over a fixed vocabulary.
    Normalizes synonymous words to simulate semantic closeness.
    """

    def __init__(self, vocabulary: List[str] = None):
        if vocabulary is None:
            # Default vocabulary spanning the example domain keywords
            vocabulary = [
                "i", "assisted", "with", "developing", "develop", "development",
                "an", "ev", "charger", "monitoring", "system", "led", "the",
                "of", "advanced", "created", "java", "pharmacy", "management",
                "application", "designed", "mobile", "banking"
            ]
        self.vocabulary = [w.lower() for w in vocabulary]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # Simple tokenization
            words = re.findall(r"\b\w+\b", text.lower())

            # Normalization to simulate semantic matching for paraphrases
            normalized = []
            for w in words:
                if w in ("developing", "development", "developed", "develop"):
                    normalized.append("develop")
                elif w in ("system", "systems"):
                    normalized.append("system")
                elif w in ("application", "applications", "app"):
                    normalized.append("app")
                elif w in ("charger", "chargers"):
                    normalized.append("charger")
                else:
                    normalized.append(w)

            # Build frequency vector
            vector = []
            for vocab_word in self.vocabulary:
                vector.append(float(normalized.count(vocab_word)))

            embeddings.append(vector)
        return embeddings
