# Configuration Persistance MongoDB - DatavizFT

## 🎯 Objectif

Configurer MongoDB avec **persistance garantie** pour que vos données DatavizFT survivent aux redémarrages, mises à jour et changements de configuration.

## 🗄️ Types de Persistance

### 1. **🐳 Docker Volumes (Recommandé)**

**Configuration actuelle dans `docker-compose.yml`** :
```yaml
services:
  mongodb:
    volumes:
      - mongodb_data:/data/db  # ← Persistance garantie
      
volumes:
  mongodb_data:
    name: datavizft_mongodb_data
```

**Avantages** :
- ✅ Persistance automatique sur votre disque
- ✅ Survit aux `docker-compose down`
- ✅ Indépendant des conteneurs
- ✅ Sauvegarde/restauration facile

**Emplacement des données** :
- Windows : `\\wsl$\docker-desktop-data\data\docker\volumes\datavizft_mongodb_data\`
- Linux/Mac : `/var/lib/docker/volumes/datavizft_mongodb_data/`

### 2. **💾 Bind Mounts (Alternative)**

```yaml
volumes:
  - ./data/mongodb:/data/db  # ← Dossier local
```

**Avantages** :
- ✅ Accès direct aux fichiers
- ✅ Sauvegarde simple (copie de dossier)

**Inconvénients** :
- ⚠️ Permissions complexes
- ⚠️ Performance moindre sur Windows

## 🔧 Vérification de la Persistance

### Test 1 : Vérifier le volume Docker

```bash
# Lister les volumes
docker volume ls

# Inspecter le volume DatavizFT
docker volume inspect datavizft_mongodb_data
```

### Test 2 : Test de persistance des données

```python
# Exécuter : python scripts/test_mongodb.py
# ✅ Insert → Stop → Start → Read doit fonctionner
```

### Test 3 : Redémarrage conteneur

```bash
# Arrêter MongoDB
docker compose stop mongodb

# Redémarrer MongoDB
docker compose start mongodb

# Vérifier que les données sont toujours là
docker exec -it datavizft_mongodb mongosh dataviz_ft_dev --eval "db.stats()"
```

## 🛠️ Commandes de Gestion

### Démarrage/Arrêt avec Persistance

```bash
# Démarrer avec persistance
docker compose up -d mongodb mongo-express

# Arrêter (données conservées)
docker compose stop

# Redémarrer
docker compose start

# Arrêter et supprimer conteneurs (données conservées)
docker compose down
```

### Sauvegarde des Données

```bash
# Export MongoDB
docker exec datavizft_mongodb mongodump --out /backup --db dataviz_ft_dev

# Copier la sauvegarde
docker cp datavizft_mongodb:/backup ./backup_$(date +%Y%m%d)
```

### Restauration des Données

```bash
# Copier sauvegarde vers conteneur
docker cp ./backup_20251015 datavizft_mongodb:/restore

# Restaurer MongoDB
docker exec datavizft_mongodb mongorestore --db dataviz_ft_dev /restore/dataviz_ft_dev
```

## ⚠️ Gestion des Volumes

### Lister tous les volumes

```bash
docker volume ls
```

### Supprimer UN volume (⚠️ PERTE DE DONNÉES)

```bash
# ATTENTION : Supprime toutes les données !
docker volume rm datavizft_mongodb_data
```

### Nettoyer les volumes inutilisés

```bash
# Supprimer volumes non utilisés
docker volume prune
```

### Sauvegarder un volume

```bash
# Créer archive du volume
docker run --rm -v datavizft_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb_backup_$(date +%Y%m%d).tar.gz -C /data .
```

### Restaurer un volume

```bash
# Restaurer depuis archive
docker run --rm -v datavizft_mongodb_data:/data -v $(pwd):/backup alpine tar xzf /backup/mongodb_backup_20251015.tar.gz -C /data
```

## 🔍 Surveillance de la Persistance

### Script de monitoring

```python
import subprocess
import json
from datetime import datetime

def check_mongodb_persistence():
    """Vérifie l'état de la persistance MongoDB"""
    
    # Vérifier le volume
    result = subprocess.run(
        ["docker", "volume", "inspect", "datavizft_mongodb_data"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        volume_info = json.loads(result.stdout)[0]
        print(f"✅ Volume persistant : {volume_info['Name']}")
        print(f"📂 Emplacement : {volume_info['Mountpoint']}")
    else:
        print("❌ Volume persistant manquant !")
        return False
    
    # Vérifier l'espace disque
    result = subprocess.run(
        ["docker", "system", "df", "-v"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("\n💾 Espace disque Docker:")
        print(result.stdout)
    
    return True

if __name__ == "__main__":
    check_mongodb_persistence()
```

## 🚨 Résolution de Problèmes

### Problème : Volume non monté

```bash
# Vérifier la configuration
docker compose config

# Recréer le volume si nécessaire
docker volume create datavizft_mongodb_data
```

### Problème : Permissions

```bash
# Fixer les permissions (Linux/Mac)
sudo chown -R 999:999 ./data/mongodb

# Windows : Redémarrer Docker Desktop
```

### Problème : Corruption de données

```bash
# Arrêter MongoDB proprement
docker compose stop mongodb

# Vérifier l'intégrité
docker run --rm -v datavizft_mongodb_data:/data mongo:7.0 mongod --dbpath /data --repair

# Redémarrer
docker compose start mongodb
```

## 📊 Bonnes Pratiques

### 1. Sauvegardes Régulières

- ✅ Export quotidien via cron/scheduled task
- ✅ Archive sur stockage externe (cloud, NAS)
- ✅ Test de restauration mensuel

### 2. Monitoring

- ✅ Surveillance espace disque
- ✅ Alertes sur erreurs MongoDB
- ✅ Logs de performance

### 3. Sécurité

- ✅ Chiffrement du volume (BitLocker, LUKS)
- ✅ Sauvegarde chiffrée
- ✅ Contrôle d'accès aux volumes

## 🎉 Résumé

Avec la configuration Docker actuelle :
- 💾 **Persistance** : Garantie par volumes Docker
- 🔄 **Redémarrages** : Données conservées
- 💽 **Espace** : Illimité (selon disque)
- 🛡️ **Sécurité** : Isolée dans Docker
- 📊 **Performance** : Optimale pour développement

Votre configuration Docker `docker-compose.yml` assure une **persistance complète** sans configuration supplémentaire ! 🚀