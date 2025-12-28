"""
CompetenceAnalyzer - Analyseur de compétences par matching exact + synonymes
=============================================================================

Détecte les compétences dans les textes d'offres d'emploi.
Approche : matching exact avec support des synonymes/variantes.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set

from backend_v2.shared import logger


@dataclass
class CompetenceMatch:
    """Représente une compétence détectée avec son score de confiance"""
    nom: str
    score: float  # 1.0 pour match exact
    categorie: str
    matched_variant: Optional[str] = None  # La variante qui a matché (si différente du nom)

    def to_dict(self) -> Dict:
        result = {
            "nom": self.nom,
            "score": round(self.score, 3),
            "categorie": self.categorie
        }
        if self.matched_variant and self.matched_variant.lower() != self.nom.lower():
            result["matched_variant"] = self.matched_variant
        return result


# Dictionnaire de synonymes : variante -> nom canonique
# Les clés sont en lowercase, les valeurs sont les noms officiels du référentiel
SYNONYMES: Dict[str, str] = {
    # JavaScript
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "es6": "JavaScript",
    "es2015": "JavaScript",
    "es2020": "JavaScript",
    "es2021": "JavaScript",
    "es2022": "JavaScript",
    "es2023": "JavaScript",

    # TypeScript
    "ts": "TypeScript",

    # Python
    "py": "Python",
    "python3": "Python",
    "python2": "Python",

    # C#
    "csharp": "C#",
    "c sharp": "C#",

    # C++
    "cpp": "C++",
    "cplusplus": "C++",
    "c plus plus": "C++",

    # Langage C
    " c ": "Langage C",  # C entouré d'espaces = langage C
    "langage c": "Langage C",
    "programmation c": "Langage C",
    "c programming": "Langage C",
    "c language": "Langage C",
    "ansi c": "Langage C",
    "c99": "Langage C",
    "c11": "Langage C",
    "c17": "Langage C",
    "c89": "Langage C",

    # .NET
    "dotnet": ".NET",
    "dot net": ".NET",
    ".net core": ".NET",
    ".net framework": ".NET",
    "net core": ".NET",
    "net framework": ".NET",
    "asp.net": "ASP.NET",
    "asp .net": "ASP.NET",

    # Node.js
    "node": "Node.js",
    "nodejs": "Node.js",

    # Vue.js
    "vue": "Vue.js",
    "vuejs": "Vue.js",

    # React
    "reactjs": "React",
    "react.js": "React",

    # Angular
    "angularjs": "Angular",
    "angular.js": "Angular",

    # Next.js
    "next": "Next.js",
    "nextjs": "Next.js",

    # Nuxt.js
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",

    # Express.js
    "express": "Express.js",
    "expressjs": "Express.js",

    # Kubernetes
    "k8s": "Kubernetes",
    "kube": "Kubernetes",

    # PostgreSQL
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "pgsql": "PostgreSQL",

    # MongoDB
    "mongo": "MongoDB",

    # Elasticsearch
    "elastic": "Elasticsearch",
    "es": "Elasticsearch",  # Attention: peut aussi être ES6

    # Amazon Web Services
    "amazon web services": "AWS",
    "amazon aws": "AWS",

    # Google Cloud Platform
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",

    # Microsoft Azure
    "ms azure": "Azure",
    "microsoft azure": "Azure",

    # CI/CD
    "ci cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "continuous delivery": "CI/CD",

    # GitLab CI
    "gitlab-ci": "GitLab CI",
    "gitlabci": "GitLab CI",

    # GitHub Actions
    "github-actions": "GitHub Actions",
    "gh actions": "GitHub Actions",

    # Machine Learning / IA
    "ml": "Machine Learning",
    "ia": "Intelligence Artificielle",
    "ai": "Intelligence Artificielle",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    # SQL Server
    "mssql": "SQL Server",
    "ms sql": "SQL Server",
    "microsoft sql server": "SQL Server",
    "sqlserver": "SQL Server",

    # Power BI
    "powerbi": "Power BI",

    # Visual Studio Code
    "vscode": "VS Code",
    "visual studio code": "VS Code",

    # IntelliJ
    "intellij": "IntelliJ IDEA",

    # Ruby on Rails
    "rails": "Ruby on Rails",
    "ror": "Ruby on Rails",

    # Spring
    "spring": "Spring Framework",
    "springboot": "Spring Boot",
    "spring-boot": "Spring Boot",

    # Hibernate / JPA
    "jpa": "JPA",
    "java persistence api": "JPA",
    "orm": "Hibernate",

    # React Native
    "react-native": "React Native",
    "reactnative": "React Native",
    "rn": "React Native",

    # Tailwind
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",

    # Material UI
    "mui": "Material UI",
    "material-ui": "Material UI",

    # REST API
    "restful": "REST",
    "rest api": "REST",
    "api rest": "REST",
    "api restful": "REST",
    "restful api": "REST",
    "webservice": "REST",
    "web service": "REST",
    "web services": "REST",

    # GraphQL
    "gql": "GraphQL",

    # WebSocket
    "ws": "WebSockets",
    "websocket": "WebSockets",

    # DevOps
    "dev ops": "DevOps",

    # Terraform
    "tf": "Terraform",

    # Ansible
    "ansible playbook": "Ansible",
    "ansible-playbook": "Ansible",

    # ELK Stack
    "elk": "ELK Stack",
    "elastic stack": "ELK Stack",

    # Scikit-learn
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",

    # TensorFlow
    "tf": "TensorFlow",

    # OpenCV
    "opencv": "OpenCV",
    "open cv": "OpenCV",

    # Pandas
    "pd": "Pandas",

    # NumPy
    "np": "NumPy",

    # Langage R (statistiques)
    " r ": "Langage R",  # R entouré d'espaces = langage R
    "rstudio": "Langage R",
    "r studio": "Langage R",
    "r-studio": "Langage R",
    "langage r": "Langage R",
    "programmation r": "Langage R",
    "r programming": "Langage R",
    "r language": "Langage R",
    "cran": "Langage R",
    "ggplot2": "Langage R",
    "ggplot": "Langage R",
    "tidyverse": "Langage R",
    "dplyr": "Langage R",
    "shiny": "Langage R",

    # Mainframe / AS400
    "as/400": "AS400",
    "iseries": "IBM i",
    "i series": "IBM i",

    # RPG (langage IBM)
    "rpgle": "RPG",
    "rpg iv": "RPG",
    "rpg/400": "RPG",

    # COBOL
    "cobol/400": "COBOL",

    # z/OS
    "zos": "z/OS",
    "mvs": "z/OS",

    # JCL
    "jcl": "JCL",

    # WinDev / WebDev
    "windev mobile": "WinDev",
    "webdev": "WebDev",

    # SAP
    "sap erp": "SAP",
    "sap hana": "SAP S/4HANA",
    "s4hana": "SAP S/4HANA",
    "s/4hana": "SAP S/4HANA",

    # Agile / Scrum
    "méthodologie agile": "Agile",
    "méthode agile": "Agile",
    "agilité": "Agile",
    "scrum master": "Scrum",
    "scrummaster": "Scrum",

    # Tests
    "unit test": "Tests unitaires",
    "unit tests": "Tests unitaires",
    "test unitaire": "Tests unitaires",
    "tdd": "TDD",
    "bdd": "BDD",

    # Protocoles
    "tcp ip": "TCP/IP",
    "tcp/ip": "TCP/IP",
    "ssl tls": "SSL/TLS",
    "ssl/tls": "SSL/TLS",
    "tls": "SSL/TLS",
    "ssl": "SSL/TLS",

    # Serveurs web
    "apache httpd": "Apache",
    "httpd": "Apache",
    "apache2": "Apache",
    "nginx-ingress": "Nginx",

    # Message queues
    "rabbitmq": "RabbitMQ",
    "rabbit mq": "RabbitMQ",
    "amqp": "RabbitMQ",
    "sqs": "Amazon SQS",

    # Assembleur
    "assembly": "Assembleur",
    "asm": "Assembleur",

    # Objective-C
    "objc": "Objective-C",
    "obj-c": "Objective-C",

    # Docker
    "docker-compose": "Docker Compose",
    "compose": "Docker Compose",

    # Qt Framework
    "qt5": "Qt",
    "qt6": "Qt",
    "qt4": "Qt",
    "pyqt": "Qt",
    "pyqt5": "Qt",
    "pyqt6": "Qt",
    "pyside": "Qt",
    "pyside2": "Qt",
    "pyside6": "Qt",
    "qml": "Qt",
    "qt creator": "Qt",
    "qtcreator": "Qt",

    # Electron
    "electronjs": "Electron",
    "electron.js": "Electron",
}


class CompetenceAnalyzer:
    """
    Analyseur de compétences par matching exact + synonymes.

    Approche :
    1. Matching exact des compétences du référentiel (case-insensitive)
    2. Matching des synonymes/variantes définis explicitement
    """

    DEFAULT_REFERENTIEL_PATH = Path(__file__).parent.parent.parent / "data" / "competences.json"

    def __init__(
        self,
        referentiel: Optional[Dict[str, List[str]]] = None,
        referentiel_path: Optional[Path] = None,
        synonymes: Optional[Dict[str, str]] = None,
    ):
        """
        Initialise l'analyseur avec le référentiel de compétences.

        Args:
            referentiel: Dict {categorie: [competences]} (optionnel)
            referentiel_path: Chemin vers le JSON du référentiel (optionnel)
            synonymes: Dict {variante: nom_canonique} (optionnel, utilise SYNONYMES par défaut)
        """
        self._logger = logger.bind(service="CompetenceAnalyzer")

        # Charger le référentiel
        if referentiel is not None:
            self._referentiel = referentiel
        else:
            path = referentiel_path or self.DEFAULT_REFERENTIEL_PATH
            self._referentiel = self._load_referentiel(path)

        # Synonymes
        self._synonymes = synonymes if synonymes is not None else SYNONYMES

        # Index pour recherche rapide
        self._competences_flat: List[str] = []
        self._competence_to_category: Dict[str, str] = {}
        self._competences_lower_set: Set[str] = set()

        self._build_index()

    def _load_referentiel(self, path: Path) -> Dict[str, List[str]]:
        """Charge le référentiel depuis un fichier JSON"""
        self._logger.info(
            "[CompetenceAnalyzer] Chargement du référentiel",
            path=str(path)
        )
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_index(self) -> None:
        """Construit l'index pour recherche rapide"""
        self._logger.info("[CompetenceAnalyzer] Construction de l'index")

        for categorie, competences in self._referentiel.items():
            for comp in competences:
                self._competences_flat.append(comp)
                self._competence_to_category[comp] = categorie
                self._competences_lower_set.add(comp.lower())

        self._logger.info(
            "[CompetenceAnalyzer] Index construit",
            nb_competences=len(self._competences_flat),
            nb_categories=len(self._referentiel),
            nb_synonymes=len(self._synonymes)
        )

    def _create_pattern(self, term: str) -> str:
        """
        Crée un pattern regex pour matcher un terme.
        Gère les cas spéciaux comme C#, C++, .NET, " R ", etc.
        """
        # Cas spécial : terme avec espaces (ex: " r " pour le langage R)
        # On cherche le terme tel quel, les espaces font partie du pattern
        if term.startswith(' ') or term.endswith(' '):
            return re.escape(term)

        term_escaped = re.escape(term)

        # Pour les termes commençant par un caractère spécial (.NET, #, etc.)
        if term[0] in '.#':
            return r'(?<![a-zA-Z0-9])' + term_escaped + r'(?![a-zA-Z0-9])'

        # Pour C#, C++, etc. - ne pas exiger de word boundary après les symboles
        if term_escaped.endswith(r'\#') or term_escaped.endswith(r'\+\+'):
            return r'\b' + term_escaped + r'(?![a-zA-Z0-9])'

        # Cas standard avec word boundaries
        return r'\b' + term_escaped + r'\b'

    def analyze_text(self, text: str, top_k: Optional[int] = None) -> List[CompetenceMatch]:
        """
        Détecte les compétences dans un texte.

        Args:
            text: Texte à analyser (description d'offre, etc.)
            top_k: Limiter aux top K résultats (optionnel)

        Returns:
            Liste des compétences détectées avec leurs scores
        """
        if not text or not text.strip():
            return []

        matches: Dict[str, CompetenceMatch] = {}
        text_lower = text.lower()

        # 1. Matching exact des compétences du référentiel
        for comp in self._competences_flat:
            comp_lower = comp.lower()
            pattern = self._create_pattern(comp_lower)

            if re.search(pattern, text_lower, re.IGNORECASE):
                matches[comp] = CompetenceMatch(
                    nom=comp,
                    score=1.0,
                    categorie=self._competence_to_category[comp]
                )

        # 2. Matching des synonymes
        for variante, nom_canonique in self._synonymes.items():
            # Skip si la compétence canonique est déjà trouvée
            if nom_canonique in matches:
                continue

            # Vérifier si la variante est dans le texte
            pattern = self._create_pattern(variante)
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Trouver la catégorie du nom canonique
                categorie = self._competence_to_category.get(nom_canonique, "autres")
                matches[nom_canonique] = CompetenceMatch(
                    nom=nom_canonique,
                    score=1.0,
                    categorie=categorie,
                    matched_variant=variante
                )

        # Convertir en liste et trier par nom
        result = list(matches.values())
        result.sort(key=lambda m: m.nom.lower())

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
        full_text = f"{intitule}\n\n{description}"
        return self.analyze_text(full_text, top_k=top_k)

    def get_referentiel_stats(self) -> Dict:
        """Retourne des statistiques sur le référentiel chargé"""
        stats_by_category = {}
        for cat, comps in self._referentiel.items():
            stats_by_category[cat] = len(comps)

        return {
            "total_competences": len(self._competences_flat),
            "nb_categories": len(self._referentiel),
            "competences_par_categorie": stats_by_category,
            "nb_synonymes": len(self._synonymes)
        }

    @property
    def referentiel(self) -> Dict[str, List[str]]:
        """Accès au référentiel de compétences"""
        return self._referentiel

    @property
    def nb_competences(self) -> int:
        """Nombre total de compétences dans le référentiel"""
        return len(self._competences_flat)

    @property
    def synonymes(self) -> Dict[str, str]:
        """Accès aux synonymes"""
        return self._synonymes


# Alias pour compatibilité avec l'ancien code
SemanticCompetenceAnalyzer = CompetenceAnalyzer
