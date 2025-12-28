"""
Script de génération de données de test pour le competence_processor
====================================================================

Récupère des offres de l'API France Travail, extrait les compétences
et génère :
- Un fichier JSON avec les offres au format BDD
- Une page HTML de comparaison description vs compétences extraites
"""

import json
import sys
import random
from pathlib import Path
from datetime import datetime

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ajouter le chemin du projet au path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.infrastructure.clients.france_travail_api import FranceTravailAPIClient
from backend_v2.domain.entities.job import Job
from backend_v2.domain.services.competence_analyzer import CompetenceAnalyzer


def collect_jobs_random(nb_offres: int = 100, pool_size: int = 500) -> list[dict]:
    """Collecte des offres aléatoires depuis l'API France Travail

    Args:
        nb_offres: Nombre d'offres à retourner
        pool_size: Taille du pool dans lequel piocher aléatoirement
    """
    print(f"🚀 Collecte de {pool_size} offres depuis l'API France Travail...")

    client = FranceTravailAPIClient()
    # Code ROME M1805 = Études et développement informatique
    all_jobs = client.collect_offres_by_rome("M1805", max_offres=pool_size)

    print(f"   Pool de {len(all_jobs)} offres disponibles")

    # Sélection aléatoire
    if len(all_jobs) <= nb_offres:
        selected = all_jobs
    else:
        selected = random.sample(all_jobs, nb_offres)

    print(f"✅ {len(selected)} offres sélectionnées aléatoirement")
    return selected


def convert_to_db_format(raw_jobs: list[dict], analyzer: CompetenceAnalyzer) -> list[dict]:
    """Convertit les offres API au format BDD avec extraction des compétences"""
    print("🔄 Conversion au format BDD et extraction des compétences...")

    db_jobs = []
    for i, raw_job in enumerate(raw_jobs, 1):
        try:
            # Convertir en entité Job
            job = Job.from_api(raw_job)
            job.source = "France_Travail"

            # Extraire les compétences
            matches = analyzer.analyze_job(job.intitule, job.description)
            job.competences_extraites = [m.nom for m in matches]
            job.competences_scores = {m.nom: m.score for m in matches}
            job.traite = True
            job.date_de_traitement = datetime.now()

            # Convertir en dict pour JSON
            job_dict = job.to_dict()

            # Sérialiser les dates pour JSON
            for key in ['date_creation', 'date_actualisation', 'date_suppression', 'date_de_traitement']:
                if job_dict.get(key) is not None:
                    job_dict[key] = job_dict[key].isoformat()

            db_jobs.append(job_dict)
            nb_comp = len(matches)
            status = "🔴" if nb_comp == 0 else "🟢"
            print(f"   {status} [{i}/{len(raw_jobs)}] {job.intitule[:50]}... → {nb_comp} compétences")

        except Exception as e:
            print(f"   ⚠️ Erreur pour offre {raw_job.get('id', '?')}: {e}")

    print(f"✅ {len(db_jobs)} offres converties")
    return db_jobs


def generate_json(db_jobs: list[dict], output_path: Path):
    """Génère le fichier JSON"""
    print(f"📝 Génération du fichier JSON: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db_jobs, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier JSON généré ({len(db_jobs)} offres)")


def generate_html(db_jobs: list[dict], output_path: Path):
    """Génère la page HTML de comparaison"""
    print(f"📝 Génération de la page HTML: {output_path}")

    # Stats
    total_competences = sum(len(j.get('competences_extraites', [])) for j in db_jobs)
    avg_competences = total_competences / len(db_jobs) if db_jobs else 0
    nb_sans_competences = sum(1 for j in db_jobs if len(j.get('competences_extraites', [])) == 0)

    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Competence Processor - Comparaison</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        header h1 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }

        header p {
            opacity: 0.9;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .stat {
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 8px;
        }

        .stat strong {
            display: block;
            font-size: 1.5rem;
        }

        .stat.warning {
            background: rgba(220, 53, 69, 0.3);
        }

        main {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1rem;
        }

        .job-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            overflow: hidden;
        }

        .job-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .job-id {
            font-family: monospace;
            background: #667eea;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        .job-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            flex: 1;
            margin-left: 1rem;
        }

        .competence-count {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }

        .competence-count.zero {
            background: #dc3545;
        }

        .job-card.no-match {
            border: 2px solid #dc3545;
        }

        .job-card.no-match .job-header {
            background: #fff5f5;
            border-bottom-color: #f5c6cb;
        }

        .job-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            padding: 1.5rem;
        }

        @media (max-width: 900px) {
            .job-content {
                grid-template-columns: 1fr;
            }
        }

        .section-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #666;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .section-title::before {
            content: '';
            width: 4px;
            height: 16px;
            background: #667eea;
            border-radius: 2px;
        }

        .description-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            font-size: 0.9rem;
            white-space: pre-wrap;
        }

        .competences-box {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .competence-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            background: #d4edda;
            color: #155724;
            padding: 0.4rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            transition: all 0.2s;
        }

        .competence-tag:hover {
            background: #28a745;
            color: white;
        }

        .no-competences {
            color: #999;
            font-style: italic;
        }

        footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>Test Competence Processor</h1>
        <p>Comparaison des descriptions vs compétences extraites (100 offres aléatoires)</p>
        <div class="stats">
            <div class="stat">
                <strong>""" + str(len(db_jobs)) + """</strong>
                Offres analysées
            </div>
            <div class="stat">
                <strong>""" + str(total_competences) + """</strong>
                Compétences détectées
            </div>
            <div class="stat">
                <strong>""" + f"{avg_competences:.1f}" + """</strong>
                Moyenne par offre
            </div>
            <div class="stat warning">
                <strong>""" + str(nb_sans_competences) + """</strong>
                Sans compétences
            </div>
        </div>
    </header>

    <main>
"""

    for job in db_jobs:
        source_id = job.get('source_id', 'N/A')
        intitule = job.get('intitule', 'Sans titre')
        description = job.get('description', 'Pas de description')
        competences = job.get('competences_extraites', [])

        # Échapper le HTML dans la description
        description_escaped = (description
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )

        # Générer les tags de compétences
        competence_tags = ""
        has_competences = len(competences) > 0
        if has_competences:
            for comp in competences:
                competence_tags += f'<span class="competence-tag">{comp}</span>\n'
        else:
            competence_tags = '<span class="no-competences">Aucune compétence détectée</span>'

        # Classes CSS conditionnelles
        card_class = "job-card" if has_competences else "job-card no-match"
        count_class = "competence-count" if has_competences else "competence-count zero"

        html_content += f"""
        <div class="{card_class}">
            <div class="job-header">
                <span class="job-id">{source_id}</span>
                <span class="job-title">{intitule}</span>
                <span class="{count_class}">{len(competences)} compétences</span>
            </div>
            <div class="job-content">
                <div class="description-section">
                    <h3 class="section-title">Description de l'offre</h3>
                    <div class="description-box">{description_escaped}</div>
                </div>
                <div class="competences-section">
                    <h3 class="section-title">Compétences extraites</h3>
                    <div class="competences-box">
                        {competence_tags}
                    </div>
                </div>
            </div>
        </div>
"""

    html_content += """
    </main>

    <footer>
        <p>Généré le """ + datetime.now().strftime("%d/%m/%Y à %H:%M") + """ | DatavizFT - Test Competence Processor</p>
    </footer>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Fichier HTML généré")


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("GÉNÉRATION DES DONNÉES DE TEST - COMPETENCE PROCESSOR")
    print("=" * 60)
    print()

    # Chemins de sortie
    output_dir = Path(__file__).parent
    json_path = output_dir / "offres_test.json"
    html_path = output_dir / "comparaison_competences.html"

    # Initialiser l'analyseur de compétences
    print("🔧 Initialisation de l'analyseur (matching exact + synonymes)...")
    analyzer = CompetenceAnalyzer()
    stats = analyzer.get_referentiel_stats()
    print(f"   Référentiel: {stats['total_competences']} compétences, {stats['nb_synonymes']} synonymes")
    print()

    # Collecter 100 offres aléatoires parmi 500
    raw_jobs = collect_jobs_random(nb_offres=100, pool_size=500)
    print()

    # Convertir au format BDD
    db_jobs = convert_to_db_format(raw_jobs, analyzer)
    print()

    # Générer les fichiers
    generate_json(db_jobs, json_path)
    generate_html(db_jobs, html_path)

    print()
    print("=" * 60)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 60)
    print(f"   📄 JSON: {json_path}")
    print(f"   🌐 HTML: {html_path}")
    print()
    print("Ouvrez le fichier HTML dans un navigateur pour visualiser les résultats.")


if __name__ == "__main__":
    main()
