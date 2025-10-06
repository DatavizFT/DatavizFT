# Guide de contribution - DatavizFT

## 🚀 Workflow de développement

### 1. Créer une nouvelle branche

```bash
# Créer et passer sur une nouvelle branche
git checkout -b feat/mongodb-integration

# Ou pour un bugfix
git checkout -b fix/unicode-encoding-issue
```

### 2. Développer avec qualité

```bash
# Vérifier la qualité avant commit
make lint      # Vérification complète
make format    # Formatage automatique
make test      # Exécuter les tests
```

### 3. Commit et push

```bash
# Commit avec message conventionnel
git add .
git commit -m "feat: add MongoDB integration for job storage"

# Push vers origin
git push origin feat/mongodb-integration
```

### 4. Créer une Pull Request

- Aller sur GitHub
- Créer PR depuis votre branche vers `main`
- Les checks automatiques se lancent :
  - ✅ Code quality (ruff, black, mypy)
  - ✅ Tests & coverage
  - ✅ Security scan
  - ✅ Dead code analysis

### 5. Review et merge

- Attendre l'approbation d'un reviewer
- Tous les checks doivent être verts ✅
- Auto-merge possible si conditions respectées

## 📋 Types de commits

### Préfixes conventionnels
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `refactor:` - Refactoring sans changement fonctionnel
- `docs:` - Mise à jour documentation
- `chore:` - Maintenance, outils, config
- `test:` - Ajout/modification de tests

### Exemples de messages
```
feat: add MongoDB client for job data persistence
fix: resolve Unicode encoding issue in text processing
refactor: optimize API client connection pooling
docs: update setup guide with quality tools
chore: upgrade dependencies to latest versions
test: add integration tests for France Travail API
```

## 🔄 Auto-release

Le système génère automatiquement des versions selon les commits :

- `fix:` → **patch** (1.0.1)
- `feat:` → **minor** (1.1.0) 
- `BREAKING CHANGE:` → **major** (2.0.0)

## 📊 Badges de statut

![CI/CD](https://github.com/YOUR_USERNAME/DatavizFT/workflows/🚀%20CI/CD%20Pipeline%20-%20DatavizFT/badge.svg)
![PR Check](https://github.com/YOUR_USERNAME/DatavizFT/workflows/🔍%20PR%20Quality%20Check/badge.svg)

## 🛡️ Protection des branches

La branche `main` est protégée :
- ⚠️ Pas de push direct
- ✅ Pull Request obligatoire
- ✅ Review required (1 approbation)
- ✅ Tous les checks CI doivent passer
- ✅ Branche à jour avec main

## 🔍 Commandes utiles

```bash
# Analyser le code mort
make dead-code

# Vérifier seulement les fichiers modifiés
make lint-changed

# Tests avec coverage
make test-coverage

# Setup environnement complet
make setup-dev
```