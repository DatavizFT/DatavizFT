"""
Text Processor - Traitement et nettoyage de texte
Extraction, nettoyage et préparation de texte pour l'analyse
"""

import re
import unicodedata
from typing import Any


def normaliser_unicode(texte: str) -> str:
    """
    Normalise les caractères Unicode problématiques

    Args:
        texte: Texte contenant potentiellement des caractères Unicode problématiques

    Returns:
        Texte avec caractères Unicode normalisés
    """
    if not texte:
        return ""

    # Remplacements des caractères problématiques courants
    remplacements = {
        "\u00a0": " ",  # Espace insécable → espace normal
        "\u2013": "-",  # Tiret moyen → tiret normal
        "\u2014": "-",  # Tiret long → tiret normal
        "\u2018": "'",  # Apostrophe courbe gauche → apostrophe simple
        "\u2019": "'",  # Apostrophe courbe droite → apostrophe simple
        "\u201c": '"',  # Guillemet double gauche → guillemet double
        "\u201d": '"',  # Guillemet double droite → guillemet double
        "\u2026": "...",  # Points de suspension → trois points
        "\u00ab": '"',  # Guillemet français gauche
        "\u00bb": '"',  # Guillemet français droite
    }

    # Appliquer les remplacements
    texte_normalise = texte
    for unicode_char, remplacement in remplacements.items():
        texte_normalise = texte_normalise.replace(unicode_char, remplacement)

    # Normalisation Unicode (décomposition puis recomposition)
    texte_normalise = unicodedata.normalize("NFKC", texte_normalise)

    return texte_normalise


def nettoyer_texte(texte: str) -> str:
    """
    Nettoie le texte pour l'analyse en supprimant caractères spéciaux

    Args:
        texte: Texte à nettoyer

    Returns:
        Texte nettoyé et normalisé
    """
    if not texte:
        return ""

    # 1. Normaliser les caractères Unicode problématiques
    texte_normalise = normaliser_unicode(texte)

    # 2. Conversion en minuscules et suppression des caractères spéciaux
    texte_clean = re.sub(r"[^\w\s\.\-\+#]", " ", texte_normalise.lower())

    # 3. Normalisation des espaces
    texte_clean = re.sub(r"\s+", " ", texte_clean)

    return texte_clean.strip()


def extraire_texte_offre(offre: dict[str, Any]) -> str:
    """
    Extrait et combine l'intitulé, la description et les compétences requises d'une offre

    Args:
        offre: Dictionnaire représentant une offre d'emploi

    Returns:
        Texte combiné et nettoyé de l'offre
    """
    intitule = offre.get("intitule", "")
    description = offre.get("description", "")
    
    # Extraction des compétences requises (champ France Travail)
    competences_requises_texte = ""
    competences_requises = offre.get("competences_requises", [])
    if competences_requises and isinstance(competences_requises, list):
        libelles_competences = []
        for comp in competences_requises:
            if isinstance(comp, dict) and "libelle" in comp:
                libelles_competences.append(comp["libelle"])
        competences_requises_texte = " ".join(libelles_competences)

    # Combinaison et nettoyage de tous les champs
    texte_complet = f"{intitule} {description} {competences_requises_texte}"
    return nettoyer_texte(texte_complet)


def extraire_competences_offre(offre: dict[str, Any]) -> list[str]:
    """
    Extrait les compétences mentionnées dans une offre

    Args:
        offre: Dictionnaire représentant une offre d'emploi

    Returns:
        Liste des compétences trouvées dans l'offre
    """
    competences_trouvees = []

    # Vérifier si l'offre a des compétences explicitement listées
    competences_field = offre.get("competences", [])
    if competences_field:
        for comp in competences_field:
            if isinstance(comp, dict) and "libelle" in comp:
                competences_trouvees.append(comp["libelle"])
            elif isinstance(comp, str):
                competences_trouvees.append(comp)

    return competences_trouvees


def creer_patterns_recherche(competence: str) -> list[str]:
    """
    Crée les patterns regex pour rechercher une compétence dans le texte

    Args:
        competence: Nom de la compétence

    Returns:
        Liste des patterns regex à utiliser
    """
    competence_lower = competence.lower()

    # Compétences qui utilisent SEULEMENT les patterns spéciaux (pas de pattern automatique)
    competences_patterns_seulement = {"c#", ".net", "asp.net", "c++"}

    # Patterns spécialisés pour améliorer la détection
    patterns_speciaux = {
        "javascript": [r"\bjs\b", r"\bjavascript\b"],
        "typescript": [r"\bts\b(?!\s*(?:test|tests))", r"\btypescript\b"],
        ".net": [
            r"\.net\b",
            r"\bdotnet\b",
            r"\bnet framework\b",
            r"\bnet core\b",
            r"\bnet 5\b",
            r"\bnet 6\b",
            r"\bnet 7\b",
            r"\bnet 8\b",
        ],
        "c#": [
            r"\bc#(?=\s|$)",  # C# suivi d'un espace ou fin de ligne
            r"(?<=\s)c#",  # C# précédé d'un espace
            r"\bc sharp\b",
            r"\bcsharp\b",
        ],
        "asp.net": [
            r"\basp\.net\b",
            r"\basp net\b",
            r"\baspnet\b",
            r"\bblazor\b",
            r"\bmvc\b(?=.*(?:asp|\.net))",  # MVC seulement si associé à ASP ou .NET
            r"\bweb api\b",
        ],
        "c++": [r"\bc\+\+\b", r"\bcpp\b", r"\bc plus plus\b"],
        "sql": [
            r"\bsql\b",
            r"\bt-sql\b",
            r"\btsql\b",
            r"\bpl\/sql\b",
            r"\bplsql\b",
            r"\bsql server\b",
            r"\bmssql\b",
        ],
        "html": [r"\bhtml\b", r"\bhtml5\b", r"\bxhtml\b"],
        "css": [r"\bcss\b", r"\bcss3\b"],
        "linux": [
            r"\blinux\b",
            r"\bunix\b",
            r"\bcentos\b",
            r"\bubuntu\b",
            r"\bdebian\b",
            r"\bred hat\b",
            r"\brhel\b",
        ],
        "windows": [
            r"\bwindows\b",
            r"\bwin\b(?!\s*(?:dev|developer))",
            r"\bmicrosoft windows\b",
        ],
        "vue.js": [r"\bvue\.js\b", r"\bvue\b(?!\s*(?:view|views))", r"\bvuejs\b"],
        "spring boot": [r"\bspring boot\b", r"\bspringboot\b"],
        "postgresql": [r"\bpostgresql\b", r"\bpostgres\b", r"\bpsql\b"],
        "mysql": [r"\bmysql\b", r"\bmy sql\b"],
        "mongodb": [r"\bmongodb\b", r"\bmongo db\b", r"\bmongo\b"],
        "agile": [r"\bagile\b", r"\bagility\b", r"\bmethodologie agile\b"],
        "scrum": [r"\bscrum\b", r"\bscrum master\b"],
        "devops": [r"\bdevops\b", r"\bdev ops\b"],
        "microservices": [
            r"\bmicroservices\b",
            r"\bmicro services\b",
            r"\bmicro-services\b",
        ],
        "docker": [r"\bdocker\b", r"\bcontainer\b", r"\bcontainerisation\b"],
        "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "git": [
            r"\bgit\b(?!\s*(?:hub|lab))",
            r"\bversion control\b",
            r"\bcontrole de version\b",
        ],
        "github": [r"\bgithub\b", r"\bgit hub\b"],
        "gitlab": [r"\bgitlab\b", r"\bgit lab\b"],
        "windev": [r"\bwindev\b", r"\bwin dev\b", r"\bpc soft\b"],
        "webdev": [r"\bwebdev\b", r"\bweb dev\b(?!\s*(?:eloper|elopment))"],
        "android": [r"\bandroid\b", r"\bmobile android\b"],
        "ios": [r"\bios\b", r"\biphone\b", r"\bipad\b", r"\bswift ios\b"],
        "react native": [r"\breact native\b", r"\breactnative\b"],
        "flutter": [r"\bflutter\b", r"\bdart flutter\b"],
    }

    # Initialiser la liste des patterns
    if competence_lower in competences_patterns_seulement:
        # Pour ces compétences, utiliser SEULEMENT les patterns spéciaux
        patterns = []
    else:
        # Pour les autres, commencer par le pattern automatique
        patterns = [rf"\b{re.escape(competence_lower)}\b"]

    if competence_lower in patterns_speciaux:
        patterns.extend(patterns_speciaux[competence_lower])

    return patterns


def rechercher_competence_dans_texte(texte: str, competence: str) -> bool:
    """
    Recherche une compétence dans un texte en utilisant les patterns regex

    Args:
        texte: Texte dans lequel chercher
        competence: Compétence à rechercher

    Returns:
        True si la compétence est trouvée, False sinon
    """
    if not texte or not competence:
        return False

    patterns = creer_patterns_recherche(competence)
    texte_lower = texte.lower()

    for pattern in patterns:
        if re.search(pattern, texte_lower):
            return True

    return False


def extraire_mots_cles(texte: str, min_longueur: int = 3) -> list[str]:
    """
    Extrait les mots-clés d'un texte

    Args:
        texte: Texte à analyser
        min_longueur: Longueur minimale des mots à conserver

    Returns:
        Liste des mots-clés uniques
    """
    if not texte:
        return []

    # Nettoyage et extraction des mots
    texte_clean = nettoyer_texte(texte)
    mots = texte_clean.split()

    # Filtrage par longueur et suppression des doublons
    mots_cles = list(
        {mot for mot in mots if len(mot) >= min_longueur and mot.isalpha()}
    )

    return sorted(mots_cles)


def normaliser_competence(competence: str) -> str:
    """
    Normalise le nom d'une compétence

    Args:
        competence: Nom de la compétence à normaliser

    Returns:
        Nom de compétence normalisé
    """
    if not competence:
        return ""

    # Suppression des espaces en trop et normalisation de la casse
    competence_norm = competence.strip()

    # Normalisation de certaines compétences courantes
    normalisations = {
        "js": "JavaScript",
        "ts": "TypeScript",
        "c sharp": "C#",
        "csharp": "C#",
        "cpp": "C++",
        "c plus plus": "C++",
        "html5": "HTML",
        "css3": "CSS",
        "postgres": "PostgreSQL",
        "psql": "PostgreSQL",
        "my sql": "MySQL",
        "mongo": "MongoDB",
        "k8s": "Kubernetes",
        "win dev": "WinDev",
        "web dev": "WebDev",
    }

    competence_lower = competence_norm.lower()
    return normalisations.get(competence_lower, competence_norm)


def nettoyer_offre_pour_json(offre: dict[str, Any]) -> dict[str, Any]:
    """
    Nettoie une offre d'emploi pour éliminer les caractères Unicode problématiques
    avant la sauvegarde JSON

    Args:
        offre: Dictionnaire d'offre d'emploi

    Returns:
        Offre nettoyée avec caractères Unicode normalisés
    """
    if not isinstance(offre, dict):
        return offre

    offre_nettoyee: dict[str, Any] = {}

    for cle, valeur in offre.items():
        if isinstance(valeur, str):
            # Nettoyer les chaînes de caractères
            offre_nettoyee[cle] = normaliser_unicode(valeur)
        elif isinstance(valeur, dict):
            # Récursion pour les dictionnaires imbriqués
            result = nettoyer_offre_pour_json(valeur)
            offre_nettoyee[cle] = result
        elif isinstance(valeur, list):
            # Traiter les listes
            items_nettoyes: list[Any] = []
            for item in valeur:
                if isinstance(item, str):
                    items_nettoyes.append(normaliser_unicode(item))
                elif isinstance(item, dict):
                    items_nettoyes.append(nettoyer_offre_pour_json(item))
                else:
                    items_nettoyes.append(item)
            offre_nettoyee[cle] = items_nettoyes
        else:
            # Garder les autres types tels quels
            offre_nettoyee[cle] = valeur

    return offre_nettoyee


def nettoyer_offres_pour_json(offres: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Nettoie une liste d'offres pour éliminer les caractères Unicode problématiques

    Args:
        offres: Liste des offres d'emploi

    Returns:
        Liste des offres nettoyées
    """
    return [nettoyer_offre_pour_json(offre) for offre in offres]
