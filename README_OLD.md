# 📊 DatavizFT

> **Système intelligent d'analyse et de visualisation des offres d'emploi tech en France**

[![CI/CD Pipeline](https://github.com/DatavizFT/DatavizFT/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/DatavizFT/DatavizFT/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](./htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-green.svg)](./quality.bat)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**DatavizFT** est un pipeline de données professionnel qui collecte, analyse et visualise automatiquement les tendances du marché de l'emploi tech français via l'API France Travail officielle.

## ✨ **Fonctionnalités**

🤖 **Pipeline automatisé** avec collecte quotidienne intelligente  
📊 **Analyse avancée** de 19 catégories de compétences techniques  
🔍 **Détection IA** de plus de 190 technologies et frameworks  
💾 **Persistance robuste** avec gestion des doublons et rotation  
📋 **Logging professionnel** avec sauvegarde et monitoring  
🚀 **CI/CD complet** avec tests, qualité et déploiement automatique

## 🚀 **Installation rapide**

```bash
# Clone et configuration
git clone https://github.com/DatavizFT/DatavizFT.git
cd DatavizFT

# Installation des dépendances
pip install -r requirements.txt

# Configuration de l'environnement
cp .env.example .env
# Éditez .env avec vos clés API France Travail

# Lancement du pipeline
python backend/main.py
```

## 📋 **Utilisation**

### **Collecte automatique**
```bash
# Collecte normale (respecte la limite 24h)
python backend/main.py

# Collecte forcée (ignore la limite)
python backend/main.py --force
```

### **Résultats générés**
```
data/
├── offres_M1805_FRANCE_20251015_065538.json     # 997 offres collectées
├── competences_extraites_20251015_065538.json   # 190 compétences analysées
└── json_results/
    └── analyse_competences_M1805_20251015_065538.json  # Analyse détaillée
```

## 🏗️ **Architecture technique**

### **Backend moderne**
```
backend/
├── main.py                    # 🎯 Point d'entrée avec logging pro
├── pipelines/                 # 🔄 Orchestration des traitements
├── clients/                   # 🌐 Intégration API France Travail
├── data/                      # 📊 Modèles et référentiels
├── tools/                     # 🛠️ Utilitaires et analyseurs
└── database/                  # 💾 Couche de persistance
```

### **Stack technologique**
| Composant | Technologies |
|-----------|--------------|
| **Pipeline** | Python 3.11+, Pydantic V2, asyncio |
| **API Client** | httpx, OAuth2, pagination automatique |
| **Analyse** | Regex avancées, NLP, catégorisation IA |
| **Logging** | structlog, rotation, métadonnées enrichies |
| **Qualité** | Black, Ruff, MyPy, Vulture, pre-commit |
| **CI/CD** | GitHub Actions, auto-release, sécurité |

---

## Fonctionnalités

- Cartes choroplèthes interactives avec filtres temporels
- Indicateurs dynamiques (à définir)
- API REST
- CI/CD
- Tests unitaires et d’intégration (backend et frontend)
- Sécurité : validation des entrées, protection SQL, monitoring

---

## Planification des sprints

| Sprint | Objectifs clés | Livrables attendus |
|----------|----------------|---------------------|
| **Sprint 1** | Définition du périmètre, architecture technique, setup du mono-repo, accès à l’API France Travail | Cahier des charges, arborescence initiale, accès API fonctionnel |
| **Sprint 2** | Collecte exploratoire via API, enrichissement des données | Module de collecte, détection des stacks, géolocalisation, validation des champs |
| **Sprint 3** | Modélisation et stockage | Schéma SQL, base PostgreSQL/PostGIS opérationnelle, tests d’insertion |
| **Sprint 4** | Interface et visualisation | Squelette React, comparaison des librairies dataviz, premiers composants fonctionnels |
| **Sprint 5** | DevOps et automatisation | Docker Compose, CI/CD GitHub Actions, gestion des environnements, .env standardisé |
| **Sprint 6** | Tests et qualité | Couverture backend/frontend, tests E2E, monitoring, alerting automatisé |

---

### Intégration des tests

- **Sprint 1** : Configuration des outils (`pytest`, `Jest`, `MSW`, `httpx`)
- **Sprint 2–3** : Tests unitaires backend (collecte, enrichissement, modèles)
- **Sprint 4** : Tests React (composants, hooks, appels API mockés)
- **Sprint 5–6** : Tests d’intégration et end-to-end (Playwright ou Cypress)

---

## Licence

A définir
