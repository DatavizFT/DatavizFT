"""
MongoDB Documents - Classes de documents pour MongoEngine (optionnel)
Alternative orientée objet pour l'accès MongoDB
"""

from datetime import datetime
from typing import Dict, List, Optional

from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    ListField,
    DictField,
    FloatField,
    IntField,
    BooleanField,
)


class OffreDocument(Document):
    """Document MongoDB pour les offres d'emploi"""
    
    # Identifiants
    source_id = StringField(required=True, unique=True)
    intitule = StringField(required=True, max_length=200)
    description = StringField()
    
    # Dates
    date_creation = DateTimeField(required=True)
    date_actualisation = DateTimeField()
    date_collecte = DateTimeField(default=datetime.now)
    
    # Entreprise
    entreprise_nom = StringField(max_length=100)
    entreprise_description = StringField()
    secteur_activite = StringField(max_length=100)
    
    # Localisation (dict flexible)
    localisation = DictField()
    
    # Compétences
    competences_brutes = StringField()
    competences_extraites = ListField(StringField(max_length=50))
    
    # Informations contractuelles
    type_contrat = StringField(max_length=50)
    experience_requise = StringField(max_length=50)
    formation_requise = ListField(StringField(max_length=100))
    
    # Salaire
    salaire_min = FloatField(min_value=0)
    salaire_max = FloatField(min_value=0)
    salaire_info = StringField(max_length=200)
    
    # Métadonnées
    version_extraction = StringField(default="1.0")
    qualite_score = FloatField(min_value=0.0, max_value=1.0)
    
    meta = {
        'collection': 'offres',
        'indexes': [
            'source_id',
            'date_creation',
            'competences_extraites',
            ('localisation.departement', 'date_creation'),
        ]
    }
    
    def __str__(self):
        return f"{self.intitule} - {self.entreprise_nom}"


class CompetenceDocument(Document):
    """Document MongoDB pour les compétences"""
    
    # Identité
    nom = StringField(required=True, max_length=100)
    nom_normalise = StringField(required=True, unique=True, max_length=100)
    categorie = StringField(required=True, max_length=50)
    
    # Variantes
    synonymes = ListField(StringField(max_length=100))
    description = StringField()
    
    # Métriques
    popularite = FloatField(min_value=0.0, max_value=1.0)
    difficulte = IntField(min_value=1, max_value=5)
    tags = ListField(StringField(max_length=30))
    
    # Métadonnées
    date_creation = DateTimeField(default=datetime.now)
    date_mise_a_jour = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'competences',
        'indexes': [
            'nom_normalise',
            'categorie',
            'popularite',
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save pour mettre à jour la date de modification"""
        self.date_mise_a_jour = datetime.now()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nom} ({self.categorie})"


class StatsDocument(Document):
    """Document MongoDB pour les statistiques de compétences"""
    
    # Métadonnées temporelles
    periode_analysee = StringField(required=True, unique=True, max_length=20)
    date_analyse = DateTimeField(default=datetime.now)
    nb_offres_analysees = IntField(min_value=0)
    
    # Statistiques (dict flexible pour compatibilité avec Pydantic)
    competences_stats = ListField(DictField())
    top_competences = ListField(StringField(max_length=50))
    competences_emergentes = ListField(StringField(max_length=50))
    competences_declinantes = ListField(StringField(max_length=50))
    
    # Analyses avancées
    combinaisons_populaires = ListField(DictField())
    correlations_salaires = DictField()
    
    # Métadonnées
    version_analyse = StringField(default="1.0")
    qualite_donnees = FloatField(min_value=0.0, max_value=1.0)
    
    meta = {
        'collection': 'stats_competences',
        'indexes': [
            'periode_analysee', 
            'date_analyse',
        ]
    }
    
    def get_competence_stats(self, competence: str) -> Optional[Dict]:
        """Récupère les stats d'une compétence spécifique"""
        for stat in self.competences_stats:
            if stat.get("competence", "").lower() == competence.lower():
                return stat
        return None
    
    def __str__(self):
        return f"Stats {self.periode_analysee} - {len(self.competences_stats)} compétences"


class DetectionCompetenceDocument(Document):
    """Document pour logger les détections de compétences"""
    
    # Référence offre
    offre_id = StringField(required=True)
    
    # Détections
    competences = ListField(DictField())  # Liste des CompetenceDetectee
    nb_competences = IntField(min_value=0)
    
    # Métadonnées détection
    date_detection = DateTimeField(default=datetime.now)
    algorithme_version = StringField(default="1.0")
    confiance_moyenne = FloatField(min_value=0.0, max_value=1.0)
    
    meta = {
        'collection': 'competences_detections',
        'indexes': [
            'offre_id',
            'date_detection',
        ]
    }
    
    def __str__(self):
        return f"Détection {self.offre_id} - {self.nb_competences} compétences"