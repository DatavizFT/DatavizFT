"""
Pipeline DatavizFT - Collecte et analyse complète des offres M1805
Intégré dans le backend pour une gestion centralisée
"""

import os
import json
import re
import time
import httpx
from datetime import datetime
from pathlib import Path
from .auth import get_token
from .config import API_BASE_URL

# Configuration
CODE_ROME = "M1805"

def charger_competences_referentiel():
    """Charge le référentiel de compétences depuis le fichier JSON"""
    try:
        chemin_competences = Path(__file__).parent.parent / "data" / "json_results" / "competences.json"
        with open(chemin_competences, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fichier competences.json non trouvé")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return {}

# Chargement du référentiel de compétences
COMPETENCES_REFERENTIEL = charger_competences_referentiel()

def collecter_toutes_offres():
    """Collecte toutes les offres M1805 en France"""
    print("🚀 DÉBUT COLLECTE COMPLÈTE DES OFFRES M1805")
    print("=" * 60)
    
    try:
        token = get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "DatavizFT-Collector/1.0"
        }
        
        url = f"{API_BASE_URL}/offres/search"
        params_base = {"codeROME": CODE_ROME}
        
        # Récupérer le total d'offres disponibles
        print("📊 Récupération du nombre total d'offres...")
        response = httpx.get(url, headers=headers, params={**params_base, "range": "0-0"})
        
        if response.status_code not in [200, 206]:
            raise Exception(f"Erreur API: {response.status_code}")
        
        content_range = response.headers.get('Content-Range', '')
        if content_range:
            total_offres = int(content_range.split('/')[-1])
            print(f"✅ {total_offres} offres disponibles au total")
        else:
            raise Exception("Impossible de déterminer le nombre total d'offres")
        
        # Collecte par pagination
        toutes_offres = []
        page_size = 150
        nb_pages = (total_offres + page_size - 1) // page_size
        
        print(f"📄 Collecte en {nb_pages} pages de {page_size} offres")
        
        for page in range(nb_pages):
            start = page * page_size
            end = min(start + page_size - 1, total_offres - 1)
            range_param = f"{start}-{end}"
            
            print(f"   📄 Page {page + 1}/{nb_pages}: range={range_param}")
            
            params = {**params_base, "range": range_param}
            response = httpx.get(url, headers=headers, params=params)
            
            if response.status_code in [200, 206]:
                data = response.json()
                offres_page = data.get('resultats', [])
                toutes_offres.extend(offres_page)
                print(f"   ✅ {len(offres_page)} offres collectées (total: {len(toutes_offres)})")
            else:
                print(f"   ❌ Erreur page {page + 1}: {response.status_code}")
            
            time.sleep(0.12)  # Rate limiting
        
        print(f"\n🎯 COLLECTE TERMINÉE: {len(toutes_offres)} offres")
        return toutes_offres
        
    except Exception as e:
        print(f"❌ Erreur collecte: {e}")
        raise

def sauvegarder_offres(offres):
    """Sauvegarde les offres en JSON"""
    try:
        os.makedirs("data", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fichier = f"data/offres_M1805_FRANCE_{timestamp}.json"
        
        # Analyser les offres pour métadonnées
        villes = set()
        entreprises = set()
        
        for offre in offres:
            lieu = offre.get('lieuTravail', {})
            if isinstance(lieu, dict):
                ville = lieu.get('libelle', 'N/A')
                villes.add(ville)
            
            entreprise = offre.get('entreprise', {})
            if isinstance(entreprise, dict):
                nom_entreprise = entreprise.get('nom', 'N/A')
                entreprises.add(nom_entreprise)
        
        donnees = {
            "metadata": {
                "nb_offres_total": len(offres),
                "timestamp_collecte": datetime.now().isoformat(),
                "code_rome": CODE_ROME,
                "scope": "FRANCE_ENTIERE",
                "nb_villes_uniques": len(villes),
                "nb_entreprises_uniques": len(entreprises)
            },
            "resultats": offres
        }
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Offres sauvegardées: {fichier}")
        print(f"   📊 {len(offres)} offres")
        print(f"   🏙️ {len(villes)} villes")
        print(f"   🏢 {len(entreprises)} entreprises")
        
        return fichier
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        raise

def nettoyer_texte(texte):
    """Nettoie le texte pour l'analyse"""
    if not texte:
        return ""
    
    texte_clean = re.sub(r'[^\w\s\.\-\+#]', ' ', texte.lower())
    texte_clean = re.sub(r'\s+', ' ', texte_clean)
    return texte_clean

def extraire_texte_offre(offre):
    """Extrait intitulé + description d'une offre"""
    intitule = offre.get('intitule', '')
    description = offre.get('description', '')
    return nettoyer_texte(f" {intitule} {description} ")

def creer_patterns_recherche(competence):
    """Crée les patterns de recherche pour une compétence"""
    patterns = [rf'\b{re.escape(competence.lower())}\b']
    
    competence_lower = competence.lower()
    
    # Patterns spécialisés
    patterns_speciaux = {
        'javascript': [r'\bjs\b', r'\bjavascript\b'],
        'typescript': [r'\bts\b(?!\s*(?:test|tests))', r'\btypescript\b'],
        'c#': [r'\bc#\b', r'\bc sharp\b', r'\bcsharp\b', r'\.net\b', r'\bdotnet\b', r'\bnet framework\b', r'\bnet core\b'],
        'c++': [r'\bc\+\+\b', r'\bcpp\b', r'\bc plus plus\b'],
        'sql': [r'\bsql\b', r'\bt-sql\b', r'\btsql\b', r'\bpl\/sql\b', r'\bplsql\b', r'\bsql server\b', r'\bmssql\b'],
        'html': [r'\bhtml\b', r'\bhtml5\b', r'\bxhtml\b'],
        'css': [r'\bcss\b', r'\bcss3\b'],
        'linux': [r'\blinux\b', r'\bunix\b', r'\bcentos\b', r'\bubuntu\b', r'\bdebian\b', r'\bred hat\b', r'\brhel\b'],
        'vue.js': [r'\bvue\.js\b', r'\bvue\b(?!\s*(?:view|views))', r'\bvuejs\b'],
        'spring boot': [r'\bspring boot\b', r'\bspringboot\b'],
        'postgresql': [r'\bpostgresql\b', r'\bpostgres\b', r'\bpsql\b'],
        'agile': [r'\bagile\b', r'\bagility\b', r'\bmethodologie agile\b'],
        'scrum': [r'\bscrum\b', r'\bscrum master\b'],
        'devops': [r'\bdevops\b', r'\bdev ops\b'],
        'microservices': [r'\bmicroservices\b', r'\bmicro services\b', r'\bmicro-services\b']
    }
    
    if competence_lower in patterns_speciaux:
        patterns.extend(patterns_speciaux[competence_lower])
    
    return patterns

def analyser_competences(offres):
    """Analyse les compétences dans les offres"""
    print("\n🔍 ANALYSE DES COMPÉTENCES")
    print("=" * 60)
    
    nb_offres_total = len(offres)
    resultats_par_categorie = {}
    
    for categorie, liste_competences in COMPETENCES_REFERENTIEL.items():
        print(f"📂 {categorie.replace('_', ' ').title()}")
        resultats_categorie = []
        
        for competence in liste_competences:
            patterns = creer_patterns_recherche(competence)
            offres_avec_competence = 0
            
            for offre in offres:
                texte_offre = extraire_texte_offre(offre)
                
                # Tester les patterns
                if any(re.search(pattern, texte_offre, re.IGNORECASE) for pattern in patterns):
                    offres_avec_competence += 1
            
            pourcentage = (offres_avec_competence / nb_offres_total) * 100
            
            resultats_categorie.append({
                'competence': competence,
                'nb_offres': offres_avec_competence,
                'pourcentage': round(pourcentage, 1)
            })
            
            if pourcentage >= 1.0:
                print(f"   ✅ {competence:<20} : {pourcentage:>5.1f}%")
        
        # Trier par pourcentage décroissant
        resultats_categorie.sort(key=lambda x: x['pourcentage'], reverse=True)
        resultats_par_categorie[categorie] = resultats_categorie
    
    return resultats_par_categorie

def sauvegarder_competences(resultats_par_categorie, nb_offres_total):
    """Sauvegarde les résultats d'analyse des compétences"""
    try:
        os.makedirs("data", exist_ok=True)
        
        # Créer le top global
        toutes_competences = []
        for categorie, competences in resultats_par_categorie.items():
            for comp in competences:
                if comp['nb_offres'] > 0:
                    toutes_competences.append({
                        **comp,
                        'categorie': categorie
                    })
        
        toutes_competences.sort(key=lambda x: x['pourcentage'], reverse=True)
        
        # Structure finale
        donnees_finales = {
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "nb_offres_analysees": nb_offres_total,
                "code_rome": CODE_ROME,
                "scope": "FRANCE_ENTIERE",
                "champs_analyses": ["intitule", "description"],
                "format": "competences_par_categorie_avec_pourcentages"
            },
            "competences_par_categorie": {
                categorie.replace('_', ' ').title(): {
                    comp['competence']: {
                        "pourcentage": comp['pourcentage'],
                        "nb_offres": comp['nb_offres']
                    }
                    for comp in competences
                }
                for categorie, competences in resultats_par_categorie.items()
            },
            "top_10_global": toutes_competences[:10],
            "statistiques_globales": {
                "nb_categories": len(resultats_par_categorie),
                "nb_competences_total": sum(len(cat) for cat in resultats_par_categorie.values()),
                "nb_competences_trouvees": len(toutes_competences)
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fichier = f"data/competences_extraites_{timestamp}.json"
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees_finales, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Compétences sauvegardées: {fichier}")
        print(f"   🏆 Top 3:")
        for i, comp in enumerate(toutes_competences[:3], 1):
            print(f"   {i}. {comp['competence']} ({comp['pourcentage']}%)")
        
        return fichier
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde compétences: {e}")
        raise

def run_pipeline():
    """Pipeline complet - Point d'entrée principal"""
    print("🚀 DATAVIZFT - PIPELINE COMPLET M1805")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 1. Collecter toutes les offres
        print("\n📋 ÉTAPE 1: COLLECTE DES OFFRES")
        offres = collecter_toutes_offres()
        
        # 2. Sauvegarder les offres
        print("\n💾 ÉTAPE 2: SAUVEGARDE DES OFFRES")
        fichier_offres = sauvegarder_offres(offres)
        
        # 3. Analyser les compétences
        print(f"\n🔍 ÉTAPE 3: ANALYSE DES COMPÉTENCES")
        resultats_competences = analyser_competences(offres)
        
        # 4. Sauvegarder l'analyse des compétences
        print(f"\n📊 ÉTAPE 4: SAUVEGARDE DE L'ANALYSE")
        fichier_competences = sauvegarder_competences(resultats_competences, len(offres))
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("✅ PIPELINE TERMINÉ AVEC SUCCÈS !")
        print("=" * 80)
        print(f"📁 Fichiers générés:")
        print(f"   • Offres: {os.path.basename(fichier_offres)}")
        print(f"   • Compétences: {os.path.basename(fichier_competences)}")
        print(f"📊 Résultats:")
        print(f"   • {len(offres)} offres M1805 collectées")
        print(f"   • Analyse complète des compétences effectuée")
        print(f"⏱️  Terminé à {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            "success": True,
            "nb_offres": len(offres),
            "fichier_offres": fichier_offres,
            "fichier_competences": fichier_competences
        }
        
    except Exception as e:
        print(f"❌ ERREUR PIPELINE: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }