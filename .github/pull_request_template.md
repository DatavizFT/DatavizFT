# 🚦 Guide des Templates de Pull Request

## 🆕 Template par défaut

### Titre de la PR
Utilisez le format : `[TYPE] Brève description`

Exemples :
- `[FEAT] Add MongoDB integration for job storage`
- `[FIX] Resolve Unicode encoding in text processing`  
- `[REFACTOR] Optimize API client connection pooling`

### Description
```markdown
## 📋 Résumé des changements
Brève description de ce qui a été modifié.

## 🎯 Motivation et contexte
Pourquoi ce changement est-il nécessaire ?
Quel problème résout-il ?

## 🧪 Comment tester
- [ ] Étapes pour reproduire/tester
- [ ] Cas de test spécifiques

## 📸 Captures d'écran (si applicable)
Avant / Après

## ✅ Checklist
- [ ] Mon code suit les standards du projet
- [ ] J'ai ajouté des tests pour mes changements
- [ ] Tous les tests passent localement
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] Mes commits suivent les conventions
```

## 🏷️ Labels automatiques

Le système ajoute automatiquement des labels selon :

### Par type de changement
- `enhancement` - Nouvelles fonctionnalités
- `bug` - Corrections de bugs
- `refactor` - Refactoring
- `documentation` - Docs uniquement
- `maintenance` - Outils, config, deps

### Par impact
- `breaking-change` - Changements incompatibles
- `minor` - Nouvelles fonctionnalités compatibles  
- `patch` - Corrections mineures

### Par statut
- `needs-review` - En attente de review
- `changes-requested` - Modifications demandées
- `approved` - Approuvé, prêt pour merge
- `work-in-progress` - Travail en cours

## 🔄 Processus de review

### 1. Review automatique (Bots)
- ✅ Checks de qualité (ruff, black, mypy)
- ✅ Tests et coverage
- ✅ Analyse de sécurité  
- ✅ Détection de code mort

### 2. Review humaine
- 🏗️ Architecture et design
- 📖 Lisibilité du code
- 🧪 Qualité des tests
- 📚 Documentation

### 3. Conditions de merge
- ✅ Au moins 1 approbation
- ✅ Tous les checks verts
- ✅ Pas de conflits
- ✅ Branche à jour

## 🚀 Auto-merge

Les PRs peuvent être auto-mergées si :
- Créées par des contributors autorisés
- Tous les checks passent
- Reviews approuvées
- Pas de `changes-requested`

## 📊 Métriques suivies

- ⏱️ Temps de review moyen
- 🔄 Nombre d'itérations
- ✅ Taux de succès des checks
- 📈 Couverture de tests
