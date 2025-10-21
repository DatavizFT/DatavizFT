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
        agence: Dict[str, Any],
        type_contrat: str,
        nombre_postes: int,
        type_contrat_libelle: str,
        qualification_code: str,
        qualification_libelle: str,
        code_NAF: str,
        nature_contrat: str,
        experience_exigee: Optional[str],
        experience_libelle: Optional[str],
        niveau_formation: Optional[str],
        salaire: Optional[Dict[str, Any]],
        competences: Optional[List[Dict[str, Any]]],
        langues: Optional[List[Dict[str, Any]]],
        permis: Optional[List[Dict[str, Any]]],
        avantages: Optional[List[str]],
        secteurs: Optional[List[str]],
        contact: Optional[Dict[str, Any]],
        secteur_activite: Optional[str] = None,
        accessible_TH: Optional[bool] = None,
        duree_travail_libelle: Optional[str] = None,
        duree_travail_libelle_converti: Optional[str] = None,
        code_rome: Optional[str] = None,
        libelle_rome: Optional[str] = None,
        appellation_libelle: Optional[str] = None,
        source: Optional[str] = None,
        url_offre: Optional[str] = None,
        origine: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        competences_extraites: Optional[List[str]] = None,
        date_suppression: Optional[datetime] = None,
        is_active: bool = True,
        traite: bool = False,
        alternance: Optional[bool] = False,
        date_de_traitement: Optional[datetime] = None,
    ):
        self.job_id = job_id
        self.intitule = intitule
        self.description = description
        self.date_creation = date_creation
        self.date_actualisation = date_actualisation
        self.lieu_travail = lieu_travail
        self.entreprise = entreprise
        self.agence = agence
        self.type_contrat = type_contrat
        self.qualification_code = qualification_code
        self.qualification_libelle = qualification_libelle
        self.code_NAF = code_NAF
        self.nombre_postes = nombre_postes
        self.type_contrat_libelle = type_contrat_libelle
        self.nature_contrat = nature_contrat
        self.experience_exigee = experience_exigee
        self.experience_libelle = experience_libelle
        self.niveau_formation = niveau_formation
        self.salaire = salaire
        self.alternance = alternance
        self.competences = competences or []
        self.langues = langues or []
        self.permis = permis or []
        self.avantages = avantages or []
        self.secteurs = secteurs or []
        self.contact = contact or {}
        self.accessible_TH = accessible_TH
        self.secteur_activite = secteur_activite
        self.duree_travail_libelle = duree_travail_libelle
        self.duree_travail_libelle_converti = duree_travail_libelle_converti
        self.code_rome = code_rome
        self.libelle_rome = libelle_rome
        self.appellation_libelle = appellation_libelle
        self.source = source
        self.url_offre = url_offre
        self.origine = origine
        self.raw_data = raw_data or {}

        self.competences_extraites = competences_extraites or []
        self.date_suppression = date_suppression
        self.is_active = is_active
        self.traite = traite
        self.date_de_traitement = date_de_traitement

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
                code_rome=data.get("romeCode"),
                libelle_rome=data.get("romeLibelle"),
                appellation_libelle=data.get("appellationLibelle"),
                nombre_postes=data.get("nombrePostes", 1),
                entreprise=data.get("entreprise", {}),
                agence=data.get("agence", {}),
                contact=data.get("contact", {}),
                accessible_TH=data.get("accessibleTH", None),
                type_contrat=data.get("typeContrat", ""),
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
                url_offre=data.get("origineOffre", {}).get("urlOrigine") or data.get("urlOffre"),
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
            "job_id": self.job_id,
            "intitule": self.intitule,
            "description": self.description,
            "date_creation": self.date_creation.isoformat(),
            "date_actualisation": self.date_actualisation.isoformat() if self.date_actualisation else None,
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
            "nombre_postes": self.nombre_postes,
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
            "date_suppression": self.date_suppression.isoformat() if self.date_suppression else None,
            "traite": self.traite,
            "date_de_traitement": self.date_de_traitement.isoformat() if self.date_de_traitement else None,
            "is_active": self.is_active,
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
