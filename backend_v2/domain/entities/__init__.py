"""
Domain Entities - Entités Métier
================================

Entités riches contenant la logique métier pure.
Chaque entité encapsule ses données et comportements.

Entités disponibles :
- Job : Offre d'emploi avec validation et règles métier
- Competence : Compétence professionnelle avec normalisation
- Statistics : Statistiques et métriques avec calculs métier
"""


from .job import Job
# from .competence import Competence  
# from .statistics import Statistics

__all__ = [
    "Job",
    # "Competence", 
    # "Statistics",
]