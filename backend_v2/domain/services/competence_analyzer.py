"""
SemanticCompetenceAnalyzer - Analyseur de compétences par embeddings sémantiques
================================================================================

Utilise les embeddings pour détecter les compétences dans les textes d'offres.
Approche hybride : extraction de tokens + matching sémantique.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set
import numpy as np

from backend_v2.infrastructure.ml import EmbeddingService
from backend_v2.shared import logger


@dataclass
class CompetenceMatch:
    """Représente une compétence détectée avec son score de confiance"""
    nom: str
    score: float  # 0.0 - 1.0
    categorie: str

    def to_dict(self) -> Dict:
        return {
            "nom": self.nom,
            "score": round(self.score, 3),
            "categorie": self.categorie
        }


# Mots français/anglais courants à ignorer (stop words + faux positifs fréquents)
STOP_WORDS: Set[str] = {
    # Français
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "nous", "vous",
    "il", "elle", "ils", "elles", "ce", "cette", "ces", "son", "sa", "ses",
    "notre", "votre", "leur", "pour", "avec", "dans", "sur", "par", "en", "au",
    "aux", "qui", "que", "quoi", "dont", "est", "sont", "sera", "seront",
    "avoir", "être", "faire", "peut", "doit", "veut", "fait", "sont",
    # Anglais
    "the", "a", "an", "and", "or", "we", "you", "he", "she", "it", "they",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "can", "for", "with", "in", "on", "at", "to", "from", "by",
    # Mots métier non-techniques
    "cdi", "cdd", "stage", "alternance", "senior", "junior", "lead", "manager",
    "chef", "responsable", "equipe", "équipe", "projet", "mission", "poste",
    "experience", "expérience", "ans", "annees", "années", "mois",
    "recherchons", "recherche", "recrute", "recrutons", "rejoindre", "rejoignez",
    "candidat", "profil", "competences", "compétences", "techniques", "technique",
    "environnement", "stack", "outils", "outil", "technologies", "technologie",
}


class SemanticCompetenceAnalyzer:
    """
    Analyseur de compétences par similarité sémantique.

    Approche hybride :
    1. Extrait les tokens/n-grams du texte
    2. Compare chaque token aux embeddings du référentiel
    3. Filtre par seuil de similarité
    """

    DEFAULT_REFERENTIEL_PATH = Path(__file__).parent.parent.parent / "data" / "competences.json"

    def __init__(
        self,
        embedding_service: EmbeddingService,
        referentiel: Optional[Dict[str, List[str]]] = None,
        referentiel_path: Optional[Path] = None,
        seuil_similarite: float = 0.85
    ):
        """
        Initialise l'analyseur avec le référentiel de compétences.

        Args:
            embedding_service: Service d'embeddings
            referentiel: Dict {categorie: [competences]} (optionnel)
            referentiel_path: Chemin vers le JSON du référentiel (optionnel)
            seuil_similarite: Score minimum pour considérer un match (0.0-1.0)
        """
        self.embedding_service = embedding_service
        self.seuil = seuil_similarite
        self._logger = logger.bind(service="SemanticCompetenceAnalyzer")

        # Charger le référentiel
        if referentiel is not None:
            self._referentiel = referentiel
        else:
            path = referentiel_path or self.DEFAULT_REFERENTIEL_PATH
            self._referentiel = self._load_referentiel(path)

        # Pré-calculer les embeddings du référentiel
        self._competences_flat: List[str] = []
        self._competences_lower: Set[str] = set()  # Pour matching exact rapide
        self._categories: List[str] = []
        self._competence_embeddings: Optional[np.ndarray] = None

        self._build_embeddings_index()

    def _load_referentiel(self, path: Path) -> Dict[str, List[str]]:
        """Charge le référentiel depuis un fichier JSON"""
        self._logger.info(
            "[SemanticCompetenceAnalyzer] Chargement du référentiel",
            path=str(path)
        )
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_embeddings_index(self) -> None:
        """Construit l'index des embeddings pour toutes les compétences"""
        self._logger.info(
            "[SemanticCompetenceAnalyzer] Construction de l'index d'embeddings"
        )

        # Aplatir le référentiel
        for categorie, competences in self._referentiel.items():
            for comp in competences:
                self._competences_flat.append(comp)
                self._competences_lower.add(comp.lower())
                self._categories.append(categorie)

        self._logger.info(
            "[SemanticCompetenceAnalyzer] Encodage des compétences",
            nb_competences=len(self._competences_flat),
            nb_categories=len(set(self._categories))
        )

        # Encoder toutes les compétences en batch
        self._competence_embeddings = self.embedding_service.encode(
            self._competences_flat,
            batch_size=64,
            show_progress=False
        )

        self._logger.info(
            "[SemanticCompetenceAnalyzer] Index construit",
            embedding_shape=self._competence_embeddings.shape
        )

    def _extract_tokens(self, text: str) -> List[str]:
        """
        Extrait les tokens significatifs du texte.

        Inclut les mots simples et les bi-grams pour capturer
        des compétences comme "GitLab CI", "Machine Learning", etc.
        """
        # Extraire les mots (lettres, chiffres, ., +, #)
        words = re.findall(r'\b[A-Za-z][A-Za-z0-9\.\+\#]*\b', text)

        # Filtrer les stop words et mots trop courts
        tokens = []
        for word in words:
            if len(word) >= 2 and word.lower() not in STOP_WORDS:
                tokens.append(word)

        # Ajouter les bi-grams (pour "GitLab CI", "Spring Boot", etc.)
        bigrams = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if w1.lower() not in STOP_WORDS and w2.lower() not in STOP_WORDS:
                bigrams.append(f"{w1} {w2}")

        return list(set(tokens + bigrams))

    def analyze_text(self, text: str, top_k: Optional[int] = None) -> List[CompetenceMatch]:
        """
        Détecte les compétences dans un texte.

        Approche hybride :
        1. Matching exact (case-insensitive) pour les compétences présentes textuellement
        2. Matching sémantique pour les synonymes/variantes

        Args:
            text: Texte à analyser (description d'offre, etc.)
            top_k: Limiter aux top K résultats (optionnel)

        Returns:
            Liste des compétences détectées avec leurs scores
        """
        if not text or not text.strip():
            return []

        matches: Dict[str, CompetenceMatch] = {}

        # 1. Matching exact avec word boundaries (prioritaire, score = 1.0)
        text_lower = text.lower()
        for i, comp in enumerate(self._competences_flat):
            comp_lower = comp.lower()
            # Utiliser regex avec word boundaries pour éviter les sous-chaînes
            # Échapper les caractères spéciaux regex dans le nom de compétence
            pattern = r'\b' + re.escape(comp_lower) + r'\b'
            if re.search(pattern, text_lower):
                matches[comp] = CompetenceMatch(
                    nom=comp,
                    score=1.0,
                    categorie=self._categories[i]
                )

        # 2. Matching sémantique sur les tokens
        tokens = self._extract_tokens(text)

        if tokens:
            # Encoder tous les tokens en batch
            token_embeddings = self.embedding_service.encode(tokens)

            # Pour chaque token, trouver la meilleure compétence
            for i, token in enumerate(tokens):
                # Skip si le token est déjà une compétence exacte trouvée
                if token in matches:
                    continue

                similarities = self.embedding_service.batch_similarity(
                    token_embeddings[i],
                    self._competence_embeddings
                )

                best_idx = int(np.argmax(similarities))
                best_score = float(similarities[best_idx])

                if best_score >= self.seuil:
                    comp_name = self._competences_flat[best_idx]
                    # Ne pas écraser un match exact
                    if comp_name not in matches:
                        matches[comp_name] = CompetenceMatch(
                            nom=comp_name,
                            score=best_score,
                            categorie=self._categories[best_idx]
                        )

        # Convertir en liste et trier par score
        result = list(matches.values())
        result.sort(key=lambda m: m.score, reverse=True)

        # Limiter si demandé
        if top_k is not None:
            result = result[:top_k]

        return result

    def analyze_job(
        self,
        intitule: str,
        description: str,
        top_k: Optional[int] = None
    ) -> List[CompetenceMatch]:
        """
        Analyse une offre d'emploi complète.

        Combine intitulé et description pour une meilleure détection.

        Args:
            intitule: Titre du poste
            description: Description complète
            top_k: Limiter aux top K résultats

        Returns:
            Liste des compétences détectées
        """
        # Combiner intitulé et description
        full_text = f"{intitule}\n\n{description}"
        return self.analyze_text(full_text, top_k=top_k)

    def get_referentiel_stats(self) -> Dict:
        """Retourne des statistiques sur le référentiel chargé"""
        stats_by_category = {}
        for cat in set(self._categories):
            stats_by_category[cat] = self._categories.count(cat)

        return {
            "total_competences": len(self._competences_flat),
            "nb_categories": len(stats_by_category),
            "competences_par_categorie": stats_by_category,
            "seuil_similarite": self.seuil
        }

    @property
    def referentiel(self) -> Dict[str, List[str]]:
        """Accès au référentiel de compétences"""
        return self._referentiel

    @property
    def nb_competences(self) -> int:
        """Nombre total de compétences dans le référentiel"""
        return len(self._competences_flat)
