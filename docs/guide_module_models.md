# 📋 Module Models - Guide d'utilisation

## 🎯 Objectif

Le module `backend.models` expose le référentiel de compétences de manière propre et facilite son utilisation dans toute l'application.

## 📦 Exports disponibles

### 1. **Référentiel complet**
```python
from backend.models import COMPETENCES_REFERENTIEL

# Utilisation
langages = COMPETENCES_REFERENTIEL['langages']
```

### 2. **Métadonnées utiles**
```python
from backend.models import (
    CATEGORIES_COMPETENCES,    # Liste des noms de catégories
    NB_CATEGORIES,            # Nombre total de catégories (19)
    NB_COMPETENCES_TOTAL      # Nombre total de compétences (258)
)

# Utilisation
for categorie in CATEGORIES_COMPETENCES:
    competences = COMPETENCES_REFERENTIEL[categorie]
    print(f"{categorie}: {len(competences)} compétences")
```

### 3. **Fonction de rechargement**
```python
from backend.models import charger_referentiel_competences

# Utile pour les tests ou rechargements dynamiques
competences = charger_referentiel_competences()
```

## 🚀 Bonnes pratiques

### ✅ **À FAIRE**

```python
# Import direct du référentiel (rapide, en cache)
from backend.models import COMPETENCES_REFERENTIEL

# Import des métadonnées pour les statistiques
from backend.models import NB_CATEGORIES, NB_COMPETENCES_TOTAL

# Utilisation dans une fonction
def analyser_competence(nom_competence):
    for categorie, competences in COMPETENCES_REFERENTIEL.items():
        if nom_competence in competences:
            return categorie
    return None
```

### ❌ **À ÉVITER**

```python
# N'importez plus directement depuis data_loader (déprécie)
from backend.tools.data_loader import charger_competences_referentiel

# N'accédez plus directement au fichier JSON
import json
with open("backend/models/competences.json") as f:
    competences = json.load(f)
```

## 🔄 Migration depuis l'ancien système

### Avant (ancien)
```python
from backend.tools.data_loader import charger_competences_referentiel
competences = charger_competences_referentiel()
```

### Après (nouveau)
```python
from backend.models import COMPETENCES_REFERENTIEL
competences = COMPETENCES_REFERENTIEL  # Plus rapide, déjà en mémoire
```

## 🛡️ Gestion d'erreurs

Le module gère automatiquement les erreurs :
- **FileNotFoundError** : Si `competences.json` est absent
- **JSONDecodeError** : Si le JSON est malformé
- **ImportError** : Si le module ne peut pas être importé

## 📊 Structure des données

```python
COMPETENCES_REFERENTIEL = {
    "langages": ["Python", "Java", "JavaScript", "WinDev", ...],
    "frameworks_frontend": ["Angular", "React", "Vue.js", ...],
    "bases_de_donnees": ["PostgreSQL", "MySQL", "HFSQL", ...],
    # ... 19 catégories au total
}
```

## 🎯 Cas d'usage fréquents

### Recherche d'une compétence
```python
from backend.models import COMPETENCES_REFERENTIEL

def trouver_categorie_competence(competence: str) -> str:
    for categorie, competences in COMPETENCES_REFERENTIEL.items():
        if competence in competences:
            return categorie
    return "non_trouvee"
```

### Statistiques globales
```python
from backend.models import NB_CATEGORIES, NB_COMPETENCES_TOTAL, CATEGORIES_COMPETENCES

print(f"📊 {NB_CATEGORIES} catégories")
print(f"🎯 {NB_COMPETENCES_TOTAL} compétences")
print(f"📝 Catégories: {', '.join(CATEGORIES_COMPETENCES[:3])}...")
```

### Validation de compétences
```python
from backend.models import COMPETENCES_REFERENTIEL

def valider_competence(competence: str) -> bool:
    return any(competence in competences 
              for competences in COMPETENCES_REFERENTIEL.values())
```

## 🏗️ Architecture

```
backend/models/
├── __init__.py          # 📦 Exports du module
└── competences.json     # 📋 Données source (ne pas importer directement)
```

Le fichier `__init__.py` charge automatiquement `competences.json` et expose les données via des constantes pratiques.