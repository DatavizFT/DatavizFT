# Système de Logging DatavizFT

## 📋 Vue d'ensemble

Le système de logging de DatavizFT utilise **structlog** pour des logs structurés et professionnels avec sauvegarde automatique dans des fichiers.

## 🎯 Fonctionnalités

### ✅ **Logs automatiquement sauvegardés**
- **Fichier principal** : `logs/dataviz-ft.log` (rotation 5MB, 5 fichiers)
- **Fichier erreurs** : `logs/dataviz-ft-errors.log` (rotation 5MB, 3 fichiers)
- **Format console** : Couleurs et formatage visuel  
- **Format fichier** : Texte propre sans codes ANSI

### 🔧 **Configuration**

```python
from backend.tools.logging_config import configure_logging, get_logger

# Configuration du logging (appelé automatiquement dans main.py)
configure_logging()

# Récupération d'un logger
logger = get_logger(__name__)
```

### 📝 **Utilisation**

```python
# Logs standards
logger.info("Message d'information", extra={"key": "value"})
logger.warning("Attention", extra={"component": "auth"})
logger.error("Erreur détectée", extra={"error_code": 500})
logger.critical("Erreur critique", exc_info=True)

# Log de succès personnalisé (avec ✅)
logger.success("Opération réussie", extra={"count": 42})
```

### 🎨 **Métadonnées enrichies**

Utilisation systématique du paramètre `extra={}` pour enrichir les logs :

```python
logger.info("Pipeline démarré", extra={
    "pipeline": "france_travail_m1805",
    "mode": "force", 
    "component": "main"
})
```

## 📁 **Exemples de logs dans les fichiers**

### Fichier principal (`logs/dataviz-ft.log`)
```
2025-10-15 07:02:55 [INFO] clean_test: Log propre sans couleurs | extra={'clean': True}
2025-10-15 07:02:55 [INFO] clean_test: ✅ Succès sans ANSI | extra={'formatted': True}
```

### Fichier erreurs (`logs/dataviz-ft-errors.log`)  
```json
{"asctime": "2025-10-15 07:01:25,310", "name": "test_fichier", "levelname": "ERROR", "message": "Test erreur pour fichier erreur"}
```

## 🔄 **Rotation automatique**

- **Taille maximum** : 5MB par fichier de log
- **Rétention** : 5 fichiers pour les logs généraux, 3 pour les erreurs
- **Archivage** : `.log.1`, `.log.2`, etc.

## 🚀 **Intégration dans le pipeline**

Remplacement complet des `print()` par des logs structurés dans :
- ✅ `backend/main.py` : Points d'entrée principaux
- 📋 TODO : Autres modules du pipeline

## ⚙️ **Configuration avancée**

### Variables d'environnement
- `ENVIRONMENT=production` : Active le format JSON complet
- Par défaut : Mode développement avec console colorée

### Personnalisation
Modifier `backend/tools/logging_config.py` pour :
- Changer les formats de sortie
- Ajuster la rotation des fichiers  
- Ajouter des handlers supplémentaires