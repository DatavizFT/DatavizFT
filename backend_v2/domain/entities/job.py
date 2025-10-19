"""
Entité Job (Offre d'emploi) - DatavizFT Backend v2
==================================================

Représente une offre d'emploi telle que reçue de l'API France Travail.
Inclut toutes les informations pertinentes pour l'analyse métier.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from backend_v2.shared import InvalidJobDataException

class Job:
    """
    Entité métier représentant une offre d'emploi complète.
    Tous les champs de l'API France Travail sont présents.
    """
    def __init__(
        self,
        job_id: str,
        intitule: str,
        description: str,
        date_creation: datetime,
        date_actualisation: Optional[datetime],
        lieu_travail: Dict[str, Any],
        entreprise: Dict[str, Any],
        type_contrat: str,
        nature_contrat: str,
        experience_exigee: Optional[str],
        niveau_formation: Optional[str],
        salaire: Optional[Dict[str, Any]],
        competences: Optional[List[Dict[str, Any]]],
        langues: Optional[List[Dict[str, Any]]],
        permis: Optional[List[Dict[str, Any]]],
        avantages: Optional[List[str]],
        secteurs: Optional[List[str]],
        source: Optional[str] = None,
        url_offre: Optional[str] = None,
        origine: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        competences_extraites: Optional[List[str]] = None,
        date_suppression: Optional[datetime] = None,
    ):
        self.job_id = job_id
        self.intitule = intitule
        self.description = description
        self.date_creation = date_creation
        self.date_actualisation = date_actualisation
        self.lieu_travail = lieu_travail
        self.entreprise = entreprise
        self.type_contrat = type_contrat
        self.nature_contrat = nature_contrat
        self.experience_exigee = experience_exigee
        self.niveau_formation = niveau_formation
        self.salaire = salaire
        self.competences = competences or []
        self.langues = langues or []
        self.permis = permis or []
        self.avantages = avantages or []
        self.secteurs = secteurs or []
        self.source = source
        self.url_offre = url_offre
        self.origine = origine
        self.raw_data = raw_data or {}
        self.competences_extraites = competences_extraites or []
        self.date_suppression = date_suppression

        self._validate()

    def _validate(self):
        if not self.job_id or not self.intitule or not self.description:
            raise InvalidJobDataException(
                message="Champs obligatoires manquants (job_id, intitule, description)",
                job_data={
                    "job_id": self.job_id,
                    "intitule": self.intitule,
                    "description": self.description,
                },
            )

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Job":
        """Crée une entité Job à partir d'un dict brut de l'API France Travail"""
        try:
            return cls(
                job_id=str(data.get("id") or data.get("idOffre")),
                intitule=data.get("intitule", ""),
                description=data.get("description", ""),
                date_creation=datetime.fromisoformat(data["dateCreation"]),
                date_actualisation=datetime.fromisoformat(data["dateActualisation"]) if data.get("dateActualisation") else None,
                lieu_travail=data.get("lieuTravail", {}),
                entreprise=data.get("entreprise", {}),
                type_contrat=data.get("typeContrat", ""),
                nature_contrat=data.get("natureContrat", ""),
                experience_exigee=data.get("experienceExigee"),
                niveau_formation=data.get("niveauFormation"),
                salaire=data.get("salaire"),
                competences=data.get("competences"),
                langues=data.get("langues"),
                permis=data.get("permis"),
                avantages=data.get("avantages"),
                secteurs=data.get("secteurs"),
                source=data.get("source"),
                url_offre=data.get("origineOffre", {}).get("urlOrigine") or data.get("urlOffre"),
                origine=data.get("origineOffre", {}).get("origine") or data.get("origine"),
                raw_data=data,
                competences_extraites=[],
                date_suppression=None,
            )
        except Exception as e:
            raise InvalidJobDataException(
                message=f"Erreur parsing offre: {e}",
                job_data=data,
            )

    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'entité Job en dict (pour DB, API, logs)"""
        return {
            "job_id": self.job_id,
            "intitule": self.intitule,
            "description": self.description,
            "date_creation": self.date_creation.isoformat(),
            "date_actualisation": self.date_actualisation.isoformat() if self.date_actualisation else None,
            "lieu_travail": self.lieu_travail,
            "entreprise": self.entreprise,
            "type_contrat": self.type_contrat,
            "nature_contrat": self.nature_contrat,
            "experience_exigee": self.experience_exigee,
            "niveau_formation": self.niveau_formation,
            "salaire": self.salaire,
            "competences": self.competences,
            "langues": self.langues,
            "permis": self.permis,
            "avantages": self.avantages,
            "secteurs": self.secteurs,
            "source": self.source,
            "url_offre": self.url_offre,
            "origine": self.origine,
            "competences_extraites": self.competences_extraites,
            "date_suppression": self.date_suppression.isoformat() if self.date_suppression else None,
            "raw_data": self.raw_data,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Job):
            return False
        return self.job_id == other.job_id

    def __hash__(self) -> int:
        return hash(self.job_id)

    def __repr__(self) -> str:
        return f"<Job {self.job_id} - {self.intitule}>"
