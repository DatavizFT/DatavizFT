"""
EmbeddingService - Service singleton pour les embeddings sémantiques
Utilise sentence-transformers pour encoder textes en vecteurs
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend_v2.shared import logger


class EmbeddingService:
    """
    Service singleton pour la génération d'embeddings sémantiques.

    Charge le modèle une seule fois et expose des méthodes pour :
    - Encoder des textes en vecteurs
    - Calculer la similarité entre vecteurs
    """

    _instance = None
    MODEL_NAME = "distiluse-base-multilingual-cased-v2"
    EMBEDDING_DIM = 512  # Dimension du modèle distiluse

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._logger = logger.bind(service="EmbeddingService")
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        """Charge le modèle de manière lazy (au premier appel)"""
        if self._model is None:
            self._logger.info(
                "[EmbeddingService] Chargement du modèle",
                model_name=self.MODEL_NAME
            )
            self._model = SentenceTransformer(self.MODEL_NAME)
            self._logger.info(
                "[EmbeddingService] Modèle chargé",
                embedding_dim=self._model.get_sentence_embedding_dimension()
            )
        return self._model

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Encode un ou plusieurs textes en vecteurs d'embeddings.

        Args:
            texts: Texte unique ou liste de textes à encoder
            batch_size: Taille des batches pour le traitement
            show_progress: Afficher une barre de progression

        Returns:
            np.ndarray: Vecteur(s) d'embeddings (shape: [n, dim] ou [dim])
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False

        self._logger.debug(
            "[EmbeddingService] Encodage de textes",
            nb_texts=len(texts),
            batch_size=batch_size
        )

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        if single_input:
            return embeddings[0]
        return embeddings

    def similarity(
        self,
        embedding1: Union[np.ndarray, List[float]],
        embedding2: Union[np.ndarray, List[float]]
    ) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.

        Args:
            embedding1: Premier vecteur
            embedding2: Second vecteur

        Returns:
            float: Score de similarité entre 0 et 1
        """
        e1 = np.array(embedding1).reshape(1, -1)
        e2 = np.array(embedding2).reshape(1, -1)
        return float(cosine_similarity(e1, e2)[0][0])

    def batch_similarity(
        self,
        query_embedding: Union[np.ndarray, List[float]],
        candidate_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Calcule la similarité entre un embedding et plusieurs candidats.

        Args:
            query_embedding: Vecteur de requête
            candidate_embeddings: Matrice de vecteurs candidats (n, dim)

        Returns:
            np.ndarray: Scores de similarité pour chaque candidat
        """
        query = np.array(query_embedding).reshape(1, -1)
        similarities = cosine_similarity(query, candidate_embeddings)[0]
        return similarities

    def is_loaded(self) -> bool:
        """Vérifie si le modèle est chargé en mémoire"""
        return self._model is not None

    def preload(self) -> None:
        """Force le chargement du modèle (utile au démarrage de l'app)"""
        _ = self.model
