"""
Modèles Offres d'Emploi - Structures de données pour les offres France Travail
Définit les modèles Pydantic pour validation et sérialisation des offres
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class SalaireModel(BaseModel):
    """Modèle pour les informations salariales"""
    
    libelle: Optional[str] = None
    commentaire: Optional[str] = None
    complement1: Optional[str] = None
    complement2: Optional[str] = None


class EntrepriseModel(BaseModel):
    """Modèle pour les informations d'entreprise"""
    
    nom: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    url: Optional[str] = None
    entrepriseAdaptee: Optional[bool] = None


class LocalisationModel(BaseModel):
    """Modèle pour la localisation du poste"""
    
    libelle: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    codePostal: Optional[str] = None
    commune: Optional[str] = None
    
    @validator('codePostal')
    def validate_code_postal(cls, v):
        """Valide le format du code postal français"""
        if v and not (len(v) == 5 and v.isdigit()):
            raise ValueError('Code postal doit être 5 chiffres')
        return v


class QualitesProfessionnellesModel(BaseModel):
    """Modèle pour les qualités professionnelles"""
    
    libelle: str
    description: Optional[str] = None


class CompetenceRequiseModel(BaseModel):
    """Modèle pour les compétences requises"""
    
    code: Optional[str] = None
    libelle: str
    exigence: Optional[str] = None


class FormationModel(BaseModel):
    """Modèle pour les formations"""
    
    codeFormation: Optional[str] = None
    domaineLibelle: str
    niveauLibelle: Optional[str] = None
    exigence: Optional[str] = None


class LangueModel(BaseModel):
    """Modèle pour les langues"""
    
    libelle: str
    exigence: Optional[str] = None


class PermisModel(BaseModel):
    """Modèle pour les permis"""
    
    libelle: str
    exigence: Optional[str] = None


class OffreFranceTravail(BaseModel):
    """
    Modèle complet pour les offres d'emploi de l'API France Travail
    Mappe exactement la structure JSON retournée par l'API
    """
    
    # Identifiants
    id: str
    intitule: str
    description: str
    dateCreation: datetime
    dateActualisation: datetime
    
    # Entreprise
    entreprise: EntrepriseModel
    
    # Localisation
    lieuTravail: LocalisationModel
    
    # Informations contractuelles
    typeContrat: Optional[str] = None
    typeContratLibelle: Optional[str] = None
    natureTravail: Optional[str] = None
    experienceExige: Optional[str] = None
    experienceLibelle: Optional[str] = None
    
    # Compétences et qualifications
    formations: List[FormationModel] = Field(default_factory=list)
    langues: List[LangueModel] = Field(default_factory=list)
    competences: List[CompetenceRequiseModel] = Field(default_factory=list)
    qualitesProfessionnelles: List[QualitesProfessionnellesModel] = Field(default_factory=list)
    permis: List[PermisModel] = Field(default_factory=list)
    
    # Salaire
    salaire: Optional[SalaireModel] = None
    
    # Conditions de travail
    dureeTravailLibelle: Optional[str] = None
    dureeTravailLibelleConverti: Optional[str] = None
    alternance: Optional[bool] = None
    
    # Contact
    contact: Optional[Dict[str, Any]] = None
    
    # Métadonnées
    nombrePostes: Optional[int] = 1
    accessibleTH: Optional[bool] = None
    deplacementCode: Optional[str] = None
    deplacementLibelle: Optional[str] = None
    
    # Secteur d'activité  
    secteurActivite: Optional[str] = None
    secteurActiviteLibelle: Optional[str] = None
    
    # Qualification
    qualificationCode: Optional[str] = None
    qualificationLibelle: Optional[str] = None
    
    class Config:
        """Configuration Pydantic"""
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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
    entreprise_nom: Optional[str] = None
    entreprise_description: Optional[str] = None
    secteur_activite: Optional[str] = None
    
    # Localisation (enrichie)
    localisation: Dict[str, Any] = Field(description="Infos géographiques complètes")
    
    # Compétences (extraites et normalisées)
    competences_brutes: str = Field(description="Texte brut pour extraction")
    competences_extraites: List[str] = Field(
        default_factory=list,
        description="Compétences détectées et normalisées"
    )
    
    # Informations contractuelles
    type_contrat: Optional[str] = None
    experience_requise: Optional[str] = None
    formation_requise: List[str] = Field(default_factory=list)
    
    # Salaire (normalisé)
    salaire_min: Optional[float] = None
    salaire_max: Optional[float] = None
    salaire_info: Optional[str] = None
    
    # Métadonnées de traitement
    version_extraction: str = "1.0"
    qualite_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Score qualité de l'extraction (0-1)"
    )
    
    @validator('competences_extraites')
    def normalize_competences(cls, v):
        """Normalise les compétences (lowercase, trim)"""
        return [comp.strip().lower() for comp in v if comp.strip()]
    
    class Config:
        """Configuration Pydantic"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "source_id": "123FRANCE456",
                "intitule": "Développeur Full Stack",
                "description": "Développement d'applications web...",
                "localisation": {
                    "departement": "75",
                    "region": "11",
                    "ville": "Paris"
                },
                "competences_extraites": ["python", "react", "postgresql"],
                "salaire_min": 45000,
                "salaire_max": 55000
            }
        }