# 📦 Guide des Exports des Modules - API Simplifiée

## 🎯 Vue d'ensemble

Tous les fichiers `__init__.py` ont maintenant été enrichis pour exposer une API claire et intuitive. Voici comment utiliser efficacement les nouveaux exports.

## 🚀 Import depuis le module principal `backend`

### API simplifiée (recommandée pour la plupart des cas)

```python
from backend import (
    # Référentiel de compétences
    COMPETENCES_REFERENTIEL,
    NB_CATEGORIES, 
    NB_COMPETENCES_TOTAL,
    
    # Pipeline principal
    PipelineM1805,
    run_pipelineFT,
    
    # Outils essentiels
    FranceTravailAPIClient,
    CompetenceAnalyzer,
    FileManager,
    
    # Informations système
    info_systeme
)

# Utilisation immédiate
info = info_systeme()
print(f"DatavizFT v{info['version']} - {info['nb_competences_total']} compétences")
```

## 🛠️ Import depuis `backend.tools` (outils spécialisés)

```python
from backend.tools import (
    # Classes principales
    FranceTravailAPIClient,
    CompetenceAnalyzer,
    FileManager,
    
    # Fonctions utilitaires
    nettoyer_texte,
    extraire_texte_offre,
    charger_config_pipeline,
    valider_referentiel_competences
)

# Exemple d'utilisation
texte_propre = nettoyer_texte("  Développeur Python  ")
config = charger_config_pipeline("france_travail_m1805")
```

## 🚀 Import depuis `backend.pipelines` (pipelines disponibles)

```python
from backend.pipelines import (
    # Classes de pipelines
    PipelineM1805,
    
    # Fonctions d'exécution
    run_pipelineFT,
    run_pipeline_avec_limite,
    
    # Gestion des pipelines
    lister_pipelines_disponibles,
    obtenir_pipeline,
    PIPELINES_DISPONIBLES
)

# Utilisation
pipelines = lister_pipelines_disponibles()
PipelineClass = obtenir_pipeline("M1805")
pipeline = PipelineClass()
```

## 📋 Import depuis `backend.models` (données de référence)

```python
from backend.models import (
    # Référentiel complet
    COMPETENCES_REFERENTIEL,
    
    # Métadonnées
    CATEGORIES_COMPETENCES,
    NB_CATEGORIES,
    NB_COMPETENCES_TOTAL,
    
    # Fonction de rechargement
    charger_referentiel_competences
)

# Utilisation
langages = COMPETENCES_REFERENTIEL['langages']
nb_langages = len(langages)
```

## 🎯 Cas d'usage pratiques

### 1. **Développement d'un nouveau pipeline**

```python
# Import simplifié
from backend import (
    COMPETENCES_REFERENTIEL,
    FranceTravailAPIClient,
    CompetenceAnalyzer,
    FileManager
)

class MonNouveauPipeline:
    def __init__(self):
        self.client = FranceTravailAPIClient()
        self.analyzer = CompetenceAnalyzer(COMPETENCES_REFERENTIEL)
        self.file_manager = FileManager()
```

### 2. **Script d'analyse rapide**

```python
# Import direct des éléments nécessaires
from backend import COMPETENCES_REFERENTIEL, CompetenceAnalyzer

# Analyse immédiate
analyzer = CompetenceAnalyzer(COMPETENCES_REFERENTIEL)
# ... utilisation
```

### 3. **Configuration et monitoring**

```python
from backend import info_systeme
from backend.pipelines import lister_pipelines_disponibles
from backend.tools import valider_referentiel_competences

# Vérifications système
info = info_systeme()
pipelines = lister_pipelines_disponibles()
validation_ok = valider_referentiel_competences(COMPETENCES_REFERENTIEL)
```

## 🔍 Comparaison Avant/Après

### ❌ Avant (imports complexes)
```python
from backend.models import COMPETENCES_REFERENTIEL
from backend.tools.api_client import FranceTravailAPIClient
from backend.tools.competence_analyzer import CompetenceAnalyzer
from backend.tools.file_manager import FileManager
from backend.pipelines.france_travail_m1805 import PipelineM1805
```

### ✅ Après (imports simplifiés)
```python
from backend import (
    COMPETENCES_REFERENTIEL,
    FranceTravailAPIClient,
    CompetenceAnalyzer,
    FileManager,
    PipelineM1805
)
```

## 🏗️ Structure des exports

```
backend/
├── __init__.py          # 📦 API principale simplifiée
├── models/
│   └── __init__.py      # 📋 Référentiel de compétences
├── tools/
│   └── __init__.py      # 🛠️ Tous les outils disponibles
└── pipelines/
    └── __init__.py      # 🚀 Tous les pipelines disponibles
```

## 💡 Bonnes pratiques

1. **Utiliser l'import principal** `from backend import ...` pour les cas courants
2. **Importer depuis les sous-modules** pour un contrôle plus fin
3. **Utiliser `__all__`** pour découvrir les exports disponibles
4. **Consulter `info_systeme()`** pour les informations de version

## 🚀 Avantages obtenus

- ✅ **API cohérente** : Imports logiques et prévisibles
- ✅ **Documentation intégrée** : `__all__` liste tous les exports
- ✅ **Découvrabilité** : Facile de voir ce qui est disponible
- ✅ **Flexibilité** : Import global ou spécialisé selon les besoins
- ✅ **Maintenance** : Modifications centralisées dans les `__init__.py`