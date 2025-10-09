"""
Modèles Compétences - Structures de données pour les compétences techniques
Définit les modèles Pydantic pour les compétences et statistiques
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class NiveauExigence(str, Enum):
    """Niveaux d'exigence pour les compétences"""

    DEBUTANT = "debutant"
    CONFIRME = "confirme"
    EXPERT = "expert"
    SOUHAITABLE = "souhaitable"
    OBLIGATOIRE = "obligatoire"


class TendanceEvolution(str, Enum):
    """Tendances d'évolution des compétences"""

    CROISSANTE = "croissante"
    STABLE = "stable"
    DECLINANTE = "declinante"
    EMERGENTE = "emergente"


class CategorieCompetence(str, Enum):
    """Catégories de compétences techniques"""

    LANGAGES_PROGRAMMATION = "langages_programmation"
    FRAMEWORKS_LIBRARIES = "frameworks_libraries"
    BASES_DONNEES = "bases_donnees"
    CLOUD_DEVOPS = "cloud_devops"
    OUTILS_DEVELOPPEMENT = "outils_developpement"
    SYSTEMES_OS = "systemes_os"
    METHODOLOGIES = "methodologies"
    SOFT_SKILLS = "soft_skills"


class CompetenceModel(BaseModel):
    """Modèle de base pour une compétence"""

    nom: str = Field(description="Nom de la compétence")
    nom_normalise: str | None = Field(
        None, description="Nom normalisé (auto-généré si non fourni)"
    )
    categorie: CategorieCompetence
    synonymes: list[str] = Field(
        default_factory=list, description="Synonymes et variantes"
    )
    description: str | None = None

    # Métadonnées
    popularite: float | None = Field(None, ge=0.0, le=1.0)
    difficulte: int | None = Field(None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)

    @validator("nom_normalise", pre=True, always=True)
    def generate_nom_normalise(cls, v, values):
        """Génère automatiquement le nom normalisé si pas fourni"""
        if not v and "nom" in values:
            return values["nom"].lower().strip().replace(" ", "_")
        return v.lower().strip().replace(" ", "_")

    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Python",
                "nom_normalise": "python",
                "categorie": "langages_programmation",
                "synonymes": ["python3", "py"],
                "popularite": 0.9,
                "difficulte": 3,
            }
        }


class CompetenceDetectee(BaseModel):
    """Compétence détectée dans une offre avec contexte"""

    competence: str
    contexte: str = Field(description="Extrait du texte où la compétence a été trouvée")
    confiance: float = Field(
        ge=0.0, le=1.0, description="Score de confiance de la détection"
    )
    position: int | None = Field(None, description="Position dans le texte")


class StatistiqueCompetence(BaseModel):
    """Statistiques d'usage d'une compétence"""

    competence: str
    nb_offres: int = Field(ge=0)
    pourcentage: float = Field(ge=0.0, le=100.0)
    evolution_mensuelle: dict[str, int] = Field(default_factory=dict)
    salaire_moyen: float | None = None
    secteurs_principaux: list[str] = Field(default_factory=list)

    # Analyse géographique
    repartition_regions: dict[str, int] = Field(default_factory=dict)
    departements_top: list[str] = Field(default_factory=list)

    # Tendances
    tendance: TendanceEvolution | None = None
    croissance_annuelle: float | None = None


class CompetenceStats(BaseModel):
    """Modèle complet pour les statistiques de compétences"""

    # Métadonnées de l'analyse
    date_analyse: datetime = Field(default_factory=datetime.now)
    periode_analysee: str = Field(description="ex: '2025-01' ou '2025-Q1'")
    nb_offres_analysees: int = Field(ge=0)

    # Statistiques par compétence
    competences_stats: list[StatistiqueCompetence] = Field(default_factory=list)

    # Agrégations globales
    top_competences: list[str] = Field(default_factory=list, max_items=20)
    competences_emergentes: list[str] = Field(default_factory=list)
    competences_declinantes: list[str] = Field(default_factory=list)

    # Analyses croisées
    combinaisons_populaires: list[dict[str, Any]] = Field(default_factory=list)
    correlations_salaires: dict[str, float] = Field(default_factory=dict)

    def get_competence_stats(self, competence: str) -> StatistiqueCompetence | None:
        """Récupère les stats d'une compétence spécifique"""
        for stat in self.competences_stats:
            if stat.competence.lower() == competence.lower():
                return stat
        return None

    def get_top_n_competences(self, n: int = 10) -> list[StatistiqueCompetence]:
        """Récupère le top N des compétences par nombre d'offres"""
        return sorted(self.competences_stats, key=lambda x: x.nb_offres, reverse=True)[
            :n
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "periode_analysee": "2025-10",
                "nb_offres_analysees": 1500,
                "top_competences": ["python", "javascript", "react"],
                "competences_emergentes": ["rust", "tensorflow"],
            }
        }


class EvolutionCompetence(BaseModel):
    """Modèle pour suivre l'évolution temporelle d'une compétence"""

    competence: str
    evolution_points: list[dict[str, Any]] = Field(
        default_factory=list, description="Points d'évolution temporelle"
    )

    # Métriques calculées
    taux_croissance_mensuel: float | None = None
    volatilite: float | None = None
    saisonnalite: dict[str, float] | None = None

    # Prédictions
    prediction_6mois: dict[str, Any] | None = None
    confiance_prediction: float | None = Field(None, ge=0.0, le=1.0)

    def ajouter_point_evolution(
        self, date: datetime, nb_offres: int, contexte: dict = None
    ):
        """Ajoute un point d'évolution"""
        point = {
            "date": date.isoformat(),
            "nb_offres": nb_offres,
            "contexte": contexte or {},
        }
        self.evolution_points.append(point)

    class Config:
        json_schema_extra = {
            "example": {
                "competence": "python",
                "evolution_points": [
                    {"date": "2025-10-01", "nb_offres": 150},
                    {"date": "2025-10-15", "nb_offres": 165},
                ],
                "taux_croissance_mensuel": 0.15,
            }
        }
