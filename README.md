# 📊 DatavizFT

> **Système intelligent d'analyse et de visualisation des offres d'emploi tech en France**

[![CI/CD Pipeline](https://github.com/DatavizFT/DatavizFT/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/DatavizFT/DatavizFT/actions)
[![CodeQL](https://github.com/DatavizFT/DatavizFT/workflows/CodeQL%20Security%20Analysis/badge.svg)](https://github.com/DatavizFT/DatavizFT/actions)
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

## 📊 **Résultats d'analyse**

### **Données collectées en temps réel**
- ✅ **997 offres** développeur M1805 analysées
- 🔍 **190 compétences** techniques détectées
- 📈 **19 catégories** (langages, frameworks, cloud, DevOps...)
- ⏰ **Mise à jour quotidienne** automatique

### **Top technologies détectées**
```yaml
Langages:        Java (23.2%), SQL (20.2%), JavaScript (15.2%)
Frameworks:      Angular (12.4%), React (6.5%), Spring Boot (7.2%)
DevOps:          Docker (10.9%), Kubernetes (8.1%), Jenkins (6.5%)
Cloud:           Azure (7.2%), AWS (3.9%), Google Cloud (0.3%)
Méthodologies:   Agile (21.6%), DevOps (13.2%), Scrum (10.9%)
```

## 🔧 **Développement**

### **Qualité du code**
```bash
# Pipeline de qualité complet (Windows)
.\quality.bat                   # Black, Ruff, MyPy, Bandit

# Ou commandes individuelles
python -m black backend/        # Formatage
python -m ruff check backend/   # Linting

# Tests avec couverture
python -m pytest --cov=backend --cov-report=html

# Vérification sécurité locale
bandit -r backend/
safety check

# Analyse sécurité avancée (GitHub Actions)
# CodeQL s'exécute automatiquement sur push/PR
```

### **Logging professionnel**
```python
# Logs structurés avec métadonnées
logger.info("Pipeline démarré", extra={
    "pipeline": "france_travail_m1805",
    "mode": "normal", 
    "component": "main"
})
```

### **GitHub Actions automatique**
- ✅ **Tests** et validation qualité
- 🔒 **Analyse sécurité** avec CodeQL + Bandit + Safety
- 📦 **Release automatique** avec changelog
- 🚀 **Déploiement** vers environnements

## 📚 **Documentation**

| Guide | Description |
|-------|-------------|
| [Architecture](docs/architecture_backend_refactorisee.md) | Design patterns et structure |
| [Logging](docs/logging_system.md) | Système de logs professionnel |
| [Tests](docs/tests_guide.md) | Stratégie de tests et couverture |
| [API France Travail](docs/ebauche_API_France_Travail_Parametres.md) | Intégration API officielle |

## 🤝 **Contribution**

1. **Fork** le projet
2. **Créez** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Committez** vos changements (`git commit -m 'Add amazing feature'`)
4. **Push** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrez** une Pull Request

### **Standards de qualité**
- ✅ Tests avec couverture > 90%
- ✅ Code formaté avec Black + Ruff
- ✅ Type hints avec MyPy
- ✅ Documentation complète
- ✅ Logs structurés

## 🏆 **Performances**

```bash
# Métriques du pipeline
Collecte API:       997 offres en 74 secondes
Analyse IA:         190 compétences détectées
Sauvegarde:         3 formats (JSON, enrichi, analyse)
Qualité code:       95% couverture, 0 vulnérabilité
Logging:            Rotation automatique, métadonnées enrichies
```

## 📄 **Licence**

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">
  <strong>Fait avec ❤️ pour la communauté tech française</strong><br>
  <sub>Contribuez à l'amélioration continue du marché de l'emploi tech !</sub>
</div>