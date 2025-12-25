"""
Entité Job (Offre d'emploi) - DatavizFT Backend v2
==================================================

Représente une offre d'emploi telle que reçue de l'API France Travail.
Inclut toutes les informations pertinentes pour l'analyse métier.
"""


from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend_v2.shared import InvalidJobDataException

class Job(BaseModel):
    source_id: str
    intitule: str
    description: str
    date_creation: datetime
    date_actualisation: Optional[datetime]
    lieu_travail: Dict[str, Any]
    entreprise: Dict[str, Any]
    agence: Dict[str, Any]
    type_contrat: str
    type_contrat_libelle: str
    qualification_code: str
    qualification_libelle: str
    code_NAF: str
    nature_contrat: str
    source: Optional[str]
    experience_exigee: Optional[str] = None
    experience_libelle: Optional[str] = None
    niveau_formation: Optional[str] = None
    salaire: Optional[Dict[str, Any]] = None
    competences: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    langues: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    permis: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    avantages: Optional[List[str]] = Field(default_factory=list)
    secteurs: Optional[List[str]] = Field(default_factory=list)
    contact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    secteur_activite: Optional[str] = None
    accessible_TH: Optional[bool] = None
    duree_travail_libelle: Optional[str] = None
    duree_travail_libelle_converti: Optional[str] = None
    code_rome: Optional[str] = None
    libelle_rome: Optional[str] = None
    appellation_libelle: Optional[str] = None
    url_offre: Optional[str] = None
    origine: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    competences_extraites: Optional[List[str]] = Field(default_factory=list)
    date_suppression: Optional[datetime] = None
    is_active: bool = True
    traite: bool = False
    alternance: Optional[bool] = False
    date_de_traitement: Optional[datetime] = None

    @field_validator('source_id', 'intitule', 'description')
    @classmethod
    def champs_obligatoires(cls, v, info):
        if not v:
            raise ValueError(f"Le champ {info.field_name} est obligatoire")
        return v

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Job":
        """Crée une entité Job à partir d'un dict brut de l'API France Travail ou Adzuna"""
        try:
            # Gestion de la date de création multi-source
            date_creation_str = data.get("dateCreation") or data.get("created")
            if not date_creation_str:
                raise ValueError("Champ dateCreation ou created manquant")
            # Support des formats ISO 8601 avec ou sans Z
            date_creation = datetime.fromisoformat(date_creation_str.replace("Z", "+00:00"))

            # Gestion de la date d'actualisation
            date_actualisation = None
            if data.get("dateActualisation"):
                date_actualisation = datetime.fromisoformat(data["dateActualisation"].replace("Z", "+00:00"))

            return cls(
                source_id=str(data.get("id") or data.get("idOffre")),
                intitule=data.get("intitule") or data.get("title", ""),
                description=data.get("description", ""),
                date_creation=date_creation,
                date_actualisation=date_actualisation,
                lieu_travail=data.get("lieuTravail") or data.get("location", {}),
                code_rome=data.get("romeCode"),
                libelle_rome=data.get("romeLibelle"),
                appellation_libelle=data.get("appellationLibelle"),
                entreprise=data.get("entreprise") or data.get("company", {}),
                agence=data.get("agence", {}),
                contact=data.get("contact", {}),
                accessible_TH=data.get("accessibleTH", None),
                type_contrat=data.get("typeContrat") or data.get("contract_time", ""),
                type_contrat_libelle=data.get("typeContratLibelle", ""),
                qualification_code=data.get("qualificationCode", ""),
                qualification_libelle=data.get("qualificationLibelle", ""),
                code_NAF=data.get("codeNAF", ""),
                secteur_activite=data.get("secteurActivite", ""),
                nature_contrat=data.get("natureContrat", ""),
                experience_exigee=data.get("experienceExigee"),
                experience_libelle=data.get("experienceLibelle"),
                niveau_formation=data.get("niveauFormation"),
                alternance=data.get("alternance", False),
                salaire=data.get("salaire"),
                competences=data.get("competences"),
                langues=data.get("langues"),
                permis=data.get("permis"),
                avantages=data.get("avantages"),
                secteurs=data.get("secteurs"),
                duree_travail_libelle=data.get("dureeTravailLibelle"),
                duree_travail_libelle_converti=data.get("dureeTravailLibelleConverti"),
                source=data.get("source"),
                url_offre=data.get("origineOffre", {}).get("urlOrigine") or data.get("urlOffre") or data.get("redirect_url"),
                origine=data.get("origineOffre", {}).get("origine") or data.get("origine"),
                raw_data=data,
                competences_extraites=[],
                date_suppression=None,
                traite=False,
                date_de_traitement=None,
                is_active=True,
            )
        except Exception as e:
            raise InvalidJobDataException(
                message=f"Erreur parsing offre: {e}",
                job_data=data,
            )

    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'entité Job en dict (pour DB, API, logs)"""
        return {
            "source_id": self.source_id,
            "intitule": self.intitule,
            "description": self.description,
            "date_creation": self.date_creation,  # Garder datetime pour MongoDB
            "date_actualisation": self.date_actualisation,  # Garder datetime pour MongoDB
            "lieu_travail": self.lieu_travail,
            "code_rome": self.code_rome,
            "libelle_rome": self.libelle_rome,
            "appellation_libelle": self.appellation_libelle,
            "entreprise": self.entreprise,
            "agence": self.agence,
            "contact": self.contact,
            "accessible_TH": self.accessible_TH,
            "type_contrat": self.type_contrat,
            "type_contrat_libelle": self.type_contrat_libelle,
            "qualification_code": self.qualification_code,
            "qualification_libelle": self.qualification_libelle,
            "code_NAF": self.code_NAF,
            "nature_contrat": self.nature_contrat,
            "alternance": self.alternance,
            "experience_exigee": self.experience_exigee,
            "experience_libelle": self.experience_libelle,
            "niveau_formation": self.niveau_formation,
            "salaire": self.salaire,
            "competences": self.competences,
            "langues": self.langues,
            "permis": self.permis,
            "avantages": self.avantages,
            "secteurs": self.secteurs,
            "duree_travail_libelle": self.duree_travail_libelle,
            "source": self.source,
            "url_offre": self.url_offre,
            "origine": self.origine,
            "competences_extraites": self.competences_extraites,
            "date_suppression": self.date_suppression,  # Garder datetime pour MongoDB
            "traite": self.traite,
            "date_de_traitement": self.date_de_traitement,  # Garder datetime pour MongoDB
            "is_active": self.is_active,
            "raw_data": self.raw_data,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Job):
            return False
        return self.source_id == other.source_id

    def __hash__(self) -> int:
        return hash(self.source_id)

    def __repr__(self) -> str:
        return f"<Job {self.source_id} - {self.intitule}>"
