"""
DeduplicationService - Détection de doublons sémantiques
=========================================================

Utilise une approche en 2 étapes pour détecter les doublons :
1. Filtrage rapide par métadonnées (entreprise, ville)
2. Comparaison sémantique par embeddings (coûteux, si nécessaire)
"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from backend_v2.infrastructure.ml import EmbeddingService
from backend_v2.domain.entities.job import Job
from backend_v2.shared import logger


def normalize_string(s: Optional[str]) -> str:
    """Normalise une chaîne pour comparaison (lowercase, strip, sans accents)"""
    if not s:
        return ""
    # Lowercase et strip
    result = s.lower().strip()
    # Remplacements basiques d'accents
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c',
    }
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def extract_company_name(job: Job) -> str:
    """Extrait et normalise le nom de l'entreprise"""
    entreprise = job.entreprise or {}
    nom = entreprise.get("nom") or entreprise.get("name") or ""
    return normalize_string(nom)


def extract_city(job: Job) -> str:
    """Extrait et normalise la ville"""
    lieu = job.lieu_travail or {}
    # Essayer différents champs possibles
    ville = (
        lieu.get("libelle") or
        lieu.get("commune") or
        lieu.get("city") or
        ""
    )
    # Extraire juste la ville si format "75 - Paris"
    if " - " in ville:
        ville = ville.split(" - ")[-1]
    return normalize_string(ville)


class DeduplicationService:
    """
    Service de détection de doublons avec optimisation par métadonnées.

    Approche en 2 étapes :
    1. Filtrage rapide : si entreprise OU ville différente → pas un doublon
    2. Comparaison sémantique : embeddings de la description (si étape 1 passe)
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        seuil_doublon: float = 0.95
    ):
        """
        Initialise le service de déduplication.

        Args:
            embedding_service: Service d'embeddings
            seuil_doublon: Score de similarité minimum pour considérer comme doublon (0.0-1.0)
        """
        self.embedding_service = embedding_service
        self.seuil = seuil_doublon
        self._logger = logger.bind(service="DeduplicationService")

    def _get_job_text(self, job: Job) -> str:
        """Extrait le texte représentatif d'une offre pour comparaison"""
        return f"{job.intitule}\n\n{job.description}"

    def _get_job_embedding(self, job: Job) -> np.ndarray:
        """Calcule ou récupère l'embedding d'une offre"""
        if job.embedding is not None:
            return np.array(job.embedding)
        return self.embedding_service.encode(self._get_job_text(job))

    def _get_job_metadata(self, job: Job) -> Tuple[str, str]:
        """Extrait les métadonnées pour le pré-filtrage (entreprise, ville)"""
        return extract_company_name(job), extract_city(job)

    def _metadata_match(self, job1: Job, job2: Job) -> bool:
        """
        Vérifie si deux offres ont les mêmes métadonnées (entreprise ET ville).

        Si l'une des deux est différente, ce n'est pas un doublon.
        """
        company1, city1 = self._get_job_metadata(job1)
        company2, city2 = self._get_job_metadata(job2)

        # Si l'entreprise est vide pour l'une des deux, on ne peut pas comparer
        # → on passe à la comparaison sémantique par sécurité
        if not company1 or not company2:
            return True  # Continuer avec la comparaison sémantique

        # Si l'entreprise est différente → pas un doublon
        if company1 != company2:
            return False

        # Si la ville est vide pour l'une des deux, on ne peut pas comparer
        # → on passe à la comparaison sémantique
        if not city1 or not city2:
            return True

        # Si la ville est différente → pas un doublon
        if city1 != city2:
            return False

        # Même entreprise ET même ville → potentiel doublon, vérifier sémantique
        return True

    def is_duplicate(
        self,
        job: Job,
        existing_embeddings: np.ndarray,
        existing_jobs: Optional[List[Job]] = None
    ) -> Tuple[bool, Optional[float]]:
        """
        Vérifie si une offre est un doublon d'une offre existante.

        Approche optimisée :
        1. Si existing_jobs fourni : pré-filtrage par métadonnées (entreprise, ville)
        2. Comparaison sémantique seulement sur les candidats filtrés

        Args:
            job: Offre à vérifier
            existing_embeddings: Matrice des embeddings existants
            existing_jobs: Liste des offres existantes (pour pré-filtrage métadonnées)

        Returns:
            Tuple (is_duplicate, max_similarity_score)
        """
        if len(existing_embeddings) == 0:
            return False, None

        # Si on a les jobs existants, faire le pré-filtrage par métadonnées
        if existing_jobs is not None and len(existing_jobs) == len(existing_embeddings):
            # Trouver les indices des jobs avec mêmes métadonnées
            candidate_indices = [
                i for i, existing_job in enumerate(existing_jobs)
                if self._metadata_match(job, existing_job)
            ]

            if not candidate_indices:
                # Aucun candidat avec mêmes métadonnées → pas de doublon
                self._logger.debug(
                    "[DeduplicationService] Pré-filtrage: aucun candidat",
                    job_id=job.source_id
                )
                return False, None

            # Filtrer les embeddings pour ne comparer que les candidats
            candidate_embeddings = existing_embeddings[candidate_indices]

            self._logger.debug(
                "[DeduplicationService] Pré-filtrage: candidats réduits",
                job_id=job.source_id,
                total=len(existing_embeddings),
                candidats=len(candidate_indices)
            )
        else:
            # Pas de pré-filtrage, comparer avec tous
            candidate_embeddings = existing_embeddings

        # Comparaison sémantique
        job_embedding = self._get_job_embedding(job)
        similarities = self.embedding_service.batch_similarity(
            job_embedding,
            candidate_embeddings
        )

        max_similarity = float(np.max(similarities))

        return max_similarity >= self.seuil, max_similarity

    def find_duplicates_in_batch(
        self,
        jobs: List[Job],
        existing_embeddings: Optional[np.ndarray] = None,
        existing_jobs: Optional[List[Job]] = None
    ) -> Tuple[List[Job], List[Job], np.ndarray]:
        """
        Filtre les doublons dans un batch d'offres.

        Approche optimisée :
        1. Pré-filtrage par métadonnées (entreprise, ville)
        2. Comparaison sémantique seulement si métadonnées identiques

        Args:
            jobs: Liste des offres à filtrer
            existing_embeddings: Embeddings des offres déjà en base (optionnel)
            existing_jobs: Offres existantes pour pré-filtrage (optionnel)

        Returns:
            Tuple (unique_jobs, duplicate_jobs, all_embeddings)
        """
        self._logger.info(
            "[DeduplicationService] Déduplication d'un batch",
            nb_jobs=len(jobs),
            nb_existing=len(existing_embeddings) if existing_embeddings is not None else 0
        )

        unique_jobs: List[Job] = []
        duplicate_jobs: List[Job] = []

        # Initialiser avec les embeddings existants ou tableau vide
        if existing_embeddings is not None and len(existing_embeddings) > 0:
            all_embeddings = existing_embeddings.copy()
            all_jobs_for_comparison = list(existing_jobs) if existing_jobs else []
        else:
            all_embeddings = np.empty((0, self.embedding_service.model.get_sentence_embedding_dimension()))
            all_jobs_for_comparison: List[Job] = []

        # Compteurs pour stats
        skipped_by_metadata = 0
        compared_semantically = 0

        for job in jobs:
            # Vérifier si c'est un doublon (avec pré-filtrage si possible)
            is_dup, similarity = self.is_duplicate(
                job,
                all_embeddings if len(all_embeddings) > 0 else np.empty((0, self.embedding_service.model.get_sentence_embedding_dimension())),
                existing_jobs=all_jobs_for_comparison if all_jobs_for_comparison else None
            )

            if is_dup:
                self._logger.debug(
                    "[DeduplicationService] Doublon détecté",
                    job_id=job.source_id,
                    similarity=similarity
                )
                duplicate_jobs.append(job)
            else:
                # Calculer et stocker l'embedding
                job_embedding = self._get_job_embedding(job)
                job.embedding = job_embedding.tolist()

                unique_jobs.append(job)
                # Ajouter à la matrice pour détecter les doublons internes au batch
                all_embeddings = np.vstack([all_embeddings, job_embedding])
                all_jobs_for_comparison.append(job)

        self._logger.info(
            "[DeduplicationService] Déduplication terminée",
            unique=len(unique_jobs),
            duplicates=len(duplicate_jobs)
        )

        return unique_jobs, duplicate_jobs, all_embeddings

    def compute_similarity_matrix(self, jobs: List[Job]) -> np.ndarray:
        """
        Calcule la matrice de similarité entre toutes les offres.

        Utile pour analyser les clusters d'offres similaires.

        Args:
            jobs: Liste des offres

        Returns:
            Matrice de similarité (n x n)
        """
        texts = [self._get_job_text(job) for job in jobs]
        embeddings = self.embedding_service.encode(texts)

        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(embeddings)

    def find_similar_jobs(
        self,
        job: Job,
        candidate_jobs: List[Job],
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Tuple[Job, float]]:
        """
        Trouve les offres les plus similaires à une offre donnée.

        Args:
            job: Offre de référence
            candidate_jobs: Liste des offres candidates
            top_k: Nombre de résultats maximum
            min_similarity: Score minimum de similarité

        Returns:
            Liste de tuples (job, similarity_score) triés par similarité
        """
        if not candidate_jobs:
            return []

        job_embedding = self._get_job_embedding(job)
        candidate_embeddings = np.array([
            self._get_job_embedding(c) for c in candidate_jobs
        ])

        similarities = self.embedding_service.batch_similarity(
            job_embedding,
            candidate_embeddings
        )

        # Filtrer et trier
        results = [
            (candidate_jobs[i], float(similarities[i]))
            for i in range(len(candidate_jobs))
            if similarities[i] >= min_similarity
        ]

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
