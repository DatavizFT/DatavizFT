# 🛠️ Configuration Qualité - DatavizFT

## Installation rapide (2 minutes)

```powershell
# 1. Installer les outils de qualité
pip install -r requirements-dev.txt

# 2. Installer les hooks Git (optionnel)
pre-commit install

# 3. Première vérification
ruff check backend/
black --check backend/
```

## Commandes quotidiennes

### 🪟 **Windows Batch (Recommandé)**
```cmd
# Utiliser le script Batch simple et robuste
.\quality.bat format      # Formater le code
.\quality.bat lint        # Vérifications
.\quality.bat quality     # Pipeline complet ⭐
.\quality.bat dead-code   # Analyser code mort
```

### 🐧 **Linux/Mac avec Makefile**
```bash
make format     # Formater le code
make lint       # Vérifications  
make quality    # Pipeline complet ⭐
make dead-code  # Analyser code mort
```

### 🔧 **Commandes manuelles (si besoin)**
```powershell
# Formatter automatiquement le code
black backend/

# Linter et corriger
ruff check --fix backend/  

# Vérification type
mypy backend/ --ignore-missing-imports

# Code mort
vulture backend/ --config vulture.toml
```

## Workflow recommandé

1. **Avant de coder** : `ruff check backend/`
2. **Pendant le dev** : VS Code avec extensions Ruff + Black
3. **Avant commit** : `make quality` ou hooks automatiques
4. **Avant PR** : Tous les checks verts

## Extensions VS Code recommandées

- `charliermarsh.ruff` - Linting en temps réel
- `ms-python.black-formatter` - Formatage automatique  
- `ms-python.mypy-type-checker` - Type checking
- `ms-python.python` - Support Python complet

## Avantages

✅ **Code cohérent** : Style uniforme automatique  
✅ **Bugs prévenus** : Détection erreurs avant runtime  
✅ **Performance** : Ruff 10-100x plus rapide que flake8  
✅ **Prêt MongoDB** : Base propre pour nouvelles features