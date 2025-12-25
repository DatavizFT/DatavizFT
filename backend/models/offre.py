"""
Modèles Offres d'Emploi - Structures de données pour les offres France Travail
Définit les modèles Pydantic pour validation et sérialisation des offres
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


class SalaireModel(BaseModel):
    """Modèle pour les informations salariales"""

    libelle: str | None = None
    commentaire: str | None = None
    complement1: str | None = None
    complement2: str | None = None
    listeComplements: str | None = None


class EntrepriseModel(BaseModel):
    """Modèle pour les informations d'entreprise"""

    nom: str | None = None
    description: str | None = None
    logo: str | None = None
    url: str | None = None
    entrepriseAdaptee: bool | None = None


class LocalisationModel(BaseModel):
    """Modèle pour la localisation du poste"""

    libelle: str
    latitude: float | None = None
    longitude: float | None = None
    codePostal: str | None = None
    commune: str | None = None

    @validator("codePostal")
    def validate_code_postal(cls, v):
        """Valide le format du code postal français"""
        if v and not (len(v) == 5 and v.isdigit()):
            raise ValueError("Code postal doit être 5 chiffres")
        return v


class QualitesProfessionnellesModel(BaseModel):
    """Modèle pour les qualités professionnelles"""

    libelle: str
    description: str | None = None


class CompetenceRequiseModel(BaseModel):
    """Modèle pour les compétences requises"""

    code: str | None = None
    libelle: str
    exigence: str | None = None


class FormationModel(BaseModel):
    """Modèle pour les formations"""

    codeFormation: str | None = None
    domaineLibelle: str
    niveauLibelle: str | None = None
    commentaire: str | None = None
    exigence: str | None = None


class LangueModel(BaseModel):
    """Modèle pour les langues"""

    libelle: str
    exigence: str | None = None


class PermisModel(BaseModel):
    """Modèle pour les permis"""

    libelle: str
    exigence: str | None = None


class ContactModel(BaseModel):
    """Modèle pour les informations de contact"""

    nom: str | None = None
    coordonnees1: str | None = None
    coordonnees2: str | None = None
    coordonnees3: str | None = None
    telephone: str | None = None
    courriel: str | None = None
    commentaire: str | None = None
    urlRecruteur: str | None = None
    urlPostulation: str | None = None


class AgenceModel(BaseModel):
    """Modèle pour les informations de l'agence"""

    telephone: str | None = None
    courriel: str | None = None


class PartenaireModel(BaseModel):
    """Modèle pour un partenaire dans l'origine de l'offre"""

    nom: str | None = None
    url: str | None = None
    logo: str | None = None


class OrigineOffreModel(BaseModel):
    """Modèle pour l'origine de l'offre"""

    origine: str | None = None
    urlOrigine: str | None = None
    partenaires: list[PartenaireModel] = Field(default_factory=list)


class ContexteTravailModel(BaseModel):
    """Modèle pour le contexte de travail"""

    horaires: str | None = None
    conditionsExercice: str | None = None


class OffreFranceTravail(BaseModel):
    """
    Modèle complet pour les offres d'emploi de l'API France Travail
    Mappe exactement la structure JSON retournée par l'API
    Inclut TOUS les champs disponibles dans la réponse API
    """

    # Identifiants
    id: str
    intitule: str
    description: str
    dateCreation: datetime
    dateActualisation: datetime

    # Localisation
    lieuTravail: LocalisationModel

    # Rome (métier)
    romeCode: str | None = None
    romeLibelle: str | None = None
    appellationlibelle: str | None = None

    # Entreprise
    entreprise: EntrepriseModel

    # Informations contractuelles
    typeContrat: str | None = None
    typeContratLibelle: str | None = None
    natureContrat: str | None = None
    experienceExige: str | None = None
    experienceLibelle: str | None = None
    experienceCommentaire: str | None = None

    # Compétences et qualifications
    formations: list[FormationModel] = Field(default_factory=list)
    langues: list[LangueModel] = Field(default_factory=list)
    competences: list[CompetenceRequiseModel] = Field(default_factory=list)
    qualitesProfessionnelles: list[QualitesProfessionnellesModel] = Field(
        default_factory=list
    )
    permis: list[PermisModel] = Field(default_factory=list)

    # Outils bureautiques
    outilsBureautiques: str | None = None

    # Salaire
    salaire: SalaireModel | None = None

    # Conditions de travail
    dureeTravailLibelle: str | None = None
    dureeTravailLibelleConverti: str | None = None
    complementExercice: str | None = None
    conditionExercice: str | None = None
    alternance: bool | None = None

    # Contact et agence
    contact: ContactModel | None = None
    agence: AgenceModel | None = None

    # Métadonnées de l'offre
    nombrePostes: int | None = 1
    accessibleTH: bool | None = None
    deplacementCode: str | None = None
    deplacementLibelle: str | None = None

    # Secteur d'activité
    codeNAF: str | None = None
    secteurActivite: str | None = None
    secteurActiviteLibelle: str | None = None

    # Qualification
    qualificationCode: str | None = None
    qualificationLibelle: str | None = None

    # Informations entreprise étendue
    trancheEffectifEtab: str | None = None
    entrepriseAdaptee: bool | None = None
    employeurHandiEngage: bool | None = None

    # Origine de l'offre
    origineOffre: OrigineOffreModel | None = None
    offresManqueCandidats: bool | None = None

    # Contexte de travail
    contexteTravail: ContexteTravailModel | None = None

    class Config:
        """Configuration Pydantic"""

        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class OffreEmploiModel(BaseModel):
    """
    Modèle normalisé pour usage interne de l'application
    Version simplifiée et enrichie des offres pour stockage MongoDB
    """

    # Identifiants
    source_id: str = Field(description="ID de l'offre dans le système source")
    intitule: str
    description: str

    # Dates
    date_creation: datetime
    date_actualisation: datetime
    date_collecte: datetime = Field(default_factory=datetime.now)

    # Entreprise (simplifié)
    entreprise_nom: str | None = None
    entreprise_description: str | None = None
    secteur_activite: str | None = None

    # Localisation (enrichie)
    localisation: dict[str, Any] = Field(description="Infos géographiques complètes")

    # Compétences (extraites et normalisées)
    competences_brutes: str = Field(description="Texte brut pour extraction")
    competences_extraites: list[str] = Field(
        default_factory=list, description="Compétences détectées et normalisées"
    )

    # Informations contractuelles
    type_contrat: str | None = None
    experience_requise: str | None = None
    formation_requise: list[str] = Field(default_factory=list)

    # Salaire (normalisé)
    salaire_min: float | None = None
    salaire_max: float | None = None
    salaire_info: str | None = None

    # Métadonnées de traitement
    version_extraction: str = "1.0"
    qualite_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Score qualité de l'extraction (0-1)"
    )

    @validator("competences_extraites")
    def normalize_competences(cls, v):
        """Normalise les compétences (lowercase, trim)"""
        return [comp.strip().lower() for comp in v if comp.strip()]

    class Config:
        """Configuration Pydantic"""

        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "source_id": "123FRANCE456",
                "intitule": "Développeur Full Stack",
                "description": "Développement d'applications web...",
                "localisation": {"departement": "75", "region": "11", "ville": "Paris"},
                "competences_extraites": ["python", "react", "postgresql"],
                "salaire_min": 45000,
                "salaire_max": 55000,
            }
        }
