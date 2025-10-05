"""
Text Processor - Traitement et nettoyage de texte
Extraction, nettoyage et préparation de texte pour l'analyse
"""

import re
from typing import Dict, List, Any, Optional


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
    
    # Conversion en minuscules et suppression des caractères spéciaux
    texte_clean = re.sub(r'[^\w\s\.\-\+#]', ' ', texte.lower())
    # Normalisation des espaces
    texte_clean = re.sub(r'\s+', ' ', texte_clean)
    return texte_clean.strip()


def extraire_texte_offre(offre: Dict[str, Any]) -> str:
    """
    Extrait et combine l'intitulé et la description d'une offre
    
    Args:
        offre: Dictionnaire représentant une offre d'emploi
    
    Returns:
        Texte combiné et nettoyé de l'offre
    """
    intitule = offre.get('intitule', '')
    description = offre.get('description', '')
    
    # Combinaison et nettoyage
    texte_complet = f"{intitule} {description}"
    return nettoyer_texte(texte_complet)


def extraire_competences_offre(offre: Dict[str, Any]) -> List[str]:
    """
    Extrait les compétences mentionnées dans une offre
    
    Args:
        offre: Dictionnaire représentant une offre d'emploi
    
    Returns:
        Liste des compétences trouvées dans l'offre
    """
    competences_trouvees = []
    
    # Vérifier si l'offre a des compétences explicitement listées
    competences_field = offre.get('competences', [])
    if competences_field:
        for comp in competences_field:
            if isinstance(comp, dict) and 'libelle' in comp:
                competences_trouvees.append(comp['libelle'])
            elif isinstance(comp, str):
                competences_trouvees.append(comp)
    
    return competences_trouvees


def creer_patterns_recherche(competence: str) -> List[str]:
    """
    Crée les patterns regex pour rechercher une compétence dans le texte
    
    Args:
        competence: Nom de la compétence
    
    Returns:
        Liste des patterns regex à utiliser
    """
    patterns = [rf'\b{re.escape(competence.lower())}\b']
    
    competence_lower = competence.lower()
    
    # Patterns spécialisés pour améliorer la détection
    patterns_speciaux = {
        'javascript': [r'\bjs\b', r'\bjavascript\b'],
        'typescript': [r'\bts\b(?!\s*(?:test|tests))', r'\btypescript\b'],
        'c#': [r'\bc#\b', r'\bc sharp\b', r'\bcsharp\b', r'\.net\b', r'\bdotnet\b', r'\bnet framework\b', r'\bnet core\b'],
        'c++': [r'\bc\+\+\b', r'\bcpp\b', r'\bc plus plus\b'],
        'sql': [r'\bsql\b', r'\bt-sql\b', r'\btsql\b', r'\bpl\/sql\b', r'\bplsql\b', r'\bsql server\b', r'\bmssql\b'],
        'html': [r'\bhtml\b', r'\bhtml5\b', r'\bxhtml\b'],
        'css': [r'\bcss\b', r'\bcss3\b'],
        'linux': [r'\blinux\b', r'\bunix\b', r'\bcentos\b', r'\bubuntu\b', r'\bdebian\b', r'\bred hat\b', r'\brhel\b'],
        'windows': [r'\bwindows\b', r'\bwin\b(?!\s*(?:dev|developer))', r'\bmicrosoft windows\b'],
        'vue.js': [r'\bvue\.js\b', r'\bvue\b(?!\s*(?:view|views))', r'\bvuejs\b'],
        'spring boot': [r'\bspring boot\b', r'\bspringboot\b'],
        'postgresql': [r'\bpostgresql\b', r'\bpostgres\b', r'\bpsql\b'],
        'mysql': [r'\bmysql\b', r'\bmy sql\b'],
        'mongodb': [r'\bmongodb\b', r'\bmongo db\b', r'\bmongo\b'],
        'agile': [r'\bagile\b', r'\bagility\b', r'\bmethodologie agile\b'],
        'scrum': [r'\bscrum\b', r'\bscrum master\b'],
        'devops': [r'\bdevops\b', r'\bdev ops\b'],
        'microservices': [r'\bmicroservices\b', r'\bmicro services\b', r'\bmicro-services\b'],
        'docker': [r'\bdocker\b', r'\bcontainer\b', r'\bcontainerisation\b'],
        'kubernetes': [r'\bkubernetes\b', r'\bk8s\b'],
        'git': [r'\bgit\b(?!\s*(?:hub|lab))', r'\bversion control\b', r'\bcontrole de version\b'],
        'github': [r'\bgithub\b', r'\bgit hub\b'],
        'gitlab': [r'\bgitlab\b', r'\bgit lab\b'],
        'windev': [r'\bwindev\b', r'\bwin dev\b', r'\bpc soft\b'],
        'webdev': [r'\bwebdev\b', r'\bweb dev\b(?!\s*(?:eloper|elopment))'],
        'android': [r'\bandroid\b', r'\bmobile android\b'],
        'ios': [r'\bios\b', r'\biphone\b', r'\bipad\b', r'\bswift ios\b'],
        'react native': [r'\breact native\b', r'\breactnative\b'],
        'flutter': [r'\bflutter\b', r'\bdart flutter\b'],
    }
    
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


def extraire_mots_cles(texte: str, min_longueur: int = 3) -> List[str]:
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
    mots_cles = list(set([
        mot for mot in mots 
        if len(mot) >= min_longueur and mot.isalpha()
    ]))
    
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
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'c sharp': 'C#',
        'csharp': 'C#',
        'cpp': 'C++',
        'c plus plus': 'C++',
        'html5': 'HTML',
        'css3': 'CSS',
        'postgres': 'PostgreSQL',
        'psql': 'PostgreSQL',
        'my sql': 'MySQL',
        'mongo': 'MongoDB',
        'k8s': 'Kubernetes',
        'win dev': 'WinDev',
        'web dev': 'WebDev',
    }
    
    competence_lower = competence_norm.lower()
    return normalisations.get(competence_lower, competence_norm)