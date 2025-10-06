# 🏗️ Architecture Backend - Structure Refactorisée

## 📁 Structure complète du backend

```text
backend/
├── __init__.py                   # 📦 API principale du backend
├── auth.py                       # 🔐 Authentification
├── config.py                     # ⚙️ Configuration
├── main.py                       # 🚀 Point d'entrée principal
├── pipelineFT.py                 # 📜 Ancien pipeline (legacy)
│
├── clients/                      # 🌐 CLIENTS API EXTERNES
│   ├── __init__.py              # 📦 Exports des clients
│   └── france_travail.py        # 🇫🇷 Client API France Travail
│
├── models/                       # 📋 MODÈLES DE DONNÉES
│   ├── __init__.py              # 📦 Exports des modèles
│   └── competences.json         # 📊 Référentiel de compétences
│
├── pipelines/                    # 🚀 PIPELINES DE TRAITEMENT
│   ├── __init__.py              # 📦 Exports des pipelines
│   └── france_travail_m1805.py  # 🎯 Pipeline M1805 (développement IT)
│
└── tools/                        # 🛠️ OUTILS UTILITAIRES
    ├── __init__.py              # 📦 Exports des outils
    ├── competence_analyzer.py   # 🔍 Analyseur de compétences
    ├── data_loader.py           # 📥 Chargeur de données
    ├── file_manager.py          # 💾 Gestionnaire de fichiers
    └── text_processor.py        # 📝 Processeur de texte
```

## 🎯 Réorganisation effectuée

### ✅ **Changements apportés :**

1. **🌐 Nouveau dossier `clients/`** : 
   - Logiquement séparé des outils génériques
   - Dédié aux connexions API externes
   - `api_client.py` → `clients/france_travail.py`

2. **📋 Séparation logique claire** :
   - `models/` : Structures de données et référentiels
   - `clients/` : Communication avec APIs externes  
   - `tools/` : Outils utilitaires réutilisables
   - `pipelines/` : Orchestration et logique métier

3. **🔄 Imports mis à jour** :
   - `backend.clients.france_travail` au lieu de `backend.tools.api_client`
   - Rétrocompatibilité maintenue via les `__init__.py`

## 🚀 Nouveaux imports recommandés

### **Import depuis clients (nouveau)** ✨
```python
from backend.clients import FranceTravailAPIClient

# Ou import direct
from backend.clients.france_travail import FranceTravailAPIClient
```

### **Import depuis backend principal** (fonctionne toujours) ✅
```python
from backend import FranceTravailAPIClient  # Via __init__.py
```

## 💡 Avantages de cette organisation

1. **🎯 Séparation des responsabilités** : 
   - Clients API ≠ Outils utilitaires
   - Plus facile d'ajouter d'autres clients (LinkedIn, etc.)

2. **📈 Évolutivité** :
   - Facilite l'ajout de nouveaux clients API
   - Structure claire pour les développeurs

3. **🧹 Clarté du code** :
   - `tools/` contient vraiment des outils génériques
   - `clients/` contient les connexions externes

4. **🔄 Rétrocompatibilité** :
   - Anciens imports continuent de fonctionner
   - Migration transparente

## 🔮 Extension future

Cette structure permet facilement d'ajouter :
- `clients/linkedin.py` pour LinkedIn API
- `clients/indeed.py` pour Indeed API  
- `clients/database.py` pour bases de données
- etc.

Chaque client reste autonome et testable indépendamment.