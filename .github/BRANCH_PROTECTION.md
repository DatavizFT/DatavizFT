# 🛡️ Configuration GitHub - Protection des branches

## Protection de la branche `main`

Pour configurer la protection sur GitHub :

### 1. Aller dans Settings → Branches
```
https://github.com/YOUR_USERNAME/DatavizFT/settings/branches
```

### 2. Add rule pour `main` avec ces options :

#### ✅ **Require a pull request before merging**
- ✅ Require approvals: `1`
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Require review from code owners

#### ✅ **Require status checks to pass before merging**
- ✅ Require branches to be up to date before merging
- **Required status checks:**
  - `quality` (Code Quality)
  - `tests` (Tests & Coverage) 
  - `security` (Security Scan)
  - `pr-check` (PR Quality Gate)

#### ✅ **Require conversation resolution before merging**
#### ✅ **Require signed commits** (optionnel)
#### ✅ **Require linear history** (optionnel)
#### ✅ **Include administrators** (recommandé)

## Règles de nommage des branches

### Préfixes recommandés :
- `feat/` - Nouvelles fonctionnalités
- `fix/` - Corrections de bugs  
- `refactor/` - Refactoring
- `docs/` - Documentation
- `chore/` - Maintenance

### Exemples :
```bash
feat/mongodb-integration
fix/unicode-encoding-issue
refactor/api-client-optimization
docs/setup-guide-update
```

## Auto-merge conditions

Le code peut être mergé automatiquement si :
- ✅ Tous les checks CI passent
- ✅ Au moins 1 approbation
- ✅ Pas de conflits
- ✅ Branche à jour avec main

## Badges pour README

```markdown
![CI/CD](https://github.com/YOUR_USERNAME/DatavizFT/workflows/🚀%20CI/CD%20Pipeline%20-%20DatavizFT/badge.svg)
![PR Check](https://github.com/YOUR_USERNAME/DatavizFT/workflows/🔍%20PR%20Quality%20Check/badge.svg)
![Release](https://github.com/YOUR_USERNAME/DatavizFT/workflows/🚀%20Auto%20Release/badge.svg)
```