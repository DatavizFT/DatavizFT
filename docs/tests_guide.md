# Tests pour DatavizFT

## 📊 **État actuel des tests**

- **31 tests** collectés au total
- **20 tests** qui passent ✅
- **11 tests** en échec (à corriger) ⚠️
- **Coverage** : 30% du code testé

## Structure des tests réelle

```
tests/
├── __init__.py
├── conftest.py                 # Configuration pytest et fixtures globales
├── test_config.py             # Tests de configuration (5 tests)
├── test_integration.py        # Tests d'intégration fonctionnels (8 tests)
└── test_tools/                # Tests des outils backend
    ├── __init__.py
    ├── test_competence_analyzer.py  # Tests analyseur (6 tests)
    └── test_file_manager.py         # Tests gestionnaire fichiers (12 tests)
```

## Types de tests implémentés

### 1. **Tests d'intégration** ✅ (8/8 passent)
- `test_integration.py` : Tests du workflow complet
- Simulation du pipeline données → analyse → sauvegarde
- Tests avec données réelles mais mockées
- Validation de l'interaction entre modules

### 2. **Tests unitaires** ⚠️ (13/18 passent)
- `test_config.py` : Tests de configuration (4/5 passent)
- `test_competence_analyzer.py` : Tests analyseur (3/6 passent)  
- `test_file_manager.py` : Tests gestionnaire fichiers (6/12 passent)

### 3. **Tests de régression**
- Pas encore implémentés
- À ajouter pour chaque bug fix identifié

## Commandes de test disponibles

```bash
# Dans l'environnement virtuel (.venv activé)
# Tous les tests avec coverage
.venv\Scripts\python.exe -m pytest tests/ --cov=backend

# Tests spécifiques qui passent
.venv\Scripts\python.exe -m pytest tests/test_integration.py -v

# Coverage détaillée avec rapport HTML
.venv\Scripts\python.exe -m pytest tests/ --cov=backend --cov-report=html
# Ouvre htmlcov/index.html pour voir le détail

# Tests en mode verbose pour debug
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# Tests sans capture d'output (voir les prints)
.venv\Scripts\python.exe -m pytest tests/ -s
```

## Métriques actuelles

- **Coverage actuel** : 30% (objectif : >85%)
- **Tests fonctionnels** : 20/31 (65% de réussite)
- **Modules couverts** : 4/7 modules principaux
- **Points forts** : Configuration (100%), intégration (100%)
- **Points faibles** : Clients API (14%), pipelines (18%)

## Fixtures disponibles

### Fixtures dans `conftest.py`
- `temp_dir` : Dossier temporaire pour tests
- `sample_competences_data` : Données de compétences d'exemple
- `sample_offre_data` : Données d'offre d'emploi type
- `mock_france_travail_client` : Mock du client API
- `sample_json_file` : Fichier JSON temporaire