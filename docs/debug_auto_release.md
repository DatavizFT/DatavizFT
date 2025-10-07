# 🔧 Diagnostic Auto Release - Guide de Résolution

## 🚨 **Problèmes Fréquents et Solutions**

### **❌ Erreur 1 : Workflow ne se déclenche pas**

**Symptômes :**
- CI/CD passe ✅ mais pas d'Auto Release
- Aucune execution visible dans Actions

**Causes possibles :**
```yaml
# AVANT (problème) :
if: github.event.workflow_run.conclusion == 'success' && !contains(github.event.head_commit.message, '[skip release]')

# APRÈS (corrigé) :
if: |
  github.event.workflow_run.conclusion == 'success' && 
  !contains(github.event.workflow_run.head_commit.message, '[skip release]')
```

**Solution :** ✅ Corrigé dans le commit `19c4739`

---

### **❌ Erreur 2 : Changelog vide ou malformé**

**Symptômes :**
- Release créée mais sans description
- Erreur "body_path file not found"

**Causes possibles :**
```bash
# Problème : Pas de tags existants + regex trop stricte
CHANGELOG=$(git log $LAST_TAG..HEAD --pretty=format:"- %s" --grep="feat\|fix\|perf\|refactor")
# Résultat : Chaîne vide si pas de correspondance
```

**Solution :** ✅ Corrigé avec fallback
```bash
# Nouveau code :
if [ -z "$CHANGELOG" ]; then
  CHANGELOG="- Initial release or no notable changes"
fi
```

---

### **❌ Erreur 3 : Permissions GitHub Token**

**Symptômes :**
- Erreur "Resource not accessible by integration"
- Status HTTP 403

**Vérification :**
```bash
# Le token GITHUB_TOKEN doit avoir :
- Contents: Write (pour créer tags)  
- Metadata: Read
- Pull requests: Write
```

**Solution :**
```yaml
permissions:
  contents: write
  packages: write
```

---

### **❌ Erreur 4 : Format de version invalide**

**Symptômes :**
- Erreur "Invalid tag name"
- Version avec caractères spéciaux

**Code corrigé :**
```bash
VERSION="v$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)"
# Génère : v2025.10.07-19c4739 (format valide)
```

---

## 🔍 **Comment Déboguer**

### **1. Workflow Debug Manuel**

Utilisez le workflow `debug-release.yml` créé :

```bash
# Sur GitHub → Actions → "Auto Release (Debug)" → Run workflow
```

**Ce qu'il fait :**
- ✅ Affiche infos détaillées
- ✅ Teste génération version/changelog  
- ✅ Crée release draft pour test
- ✅ Ne casse rien en prod

### **2. Vérification Locale**

```bash
# Reproduire la génération locale
cd DatavizFT

# Test génération version
VERSION="v$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)"
echo "Version: $VERSION"

# Test génération changelog
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
echo "Last tag: $LAST_TAG"

if [ -n "$LAST_TAG" ]; then
  CHANGELOG=$(git log $LAST_TAG..HEAD --pretty=format:"- %s" --no-merges)
else
  CHANGELOG=$(git log --pretty=format:"- %s" --no-merges -5)
fi

echo "Changelog:"
echo "$CHANGELOG"
```

### **3. Logs GitHub Actions**

```
GitHub → Actions → Release workflow → Click sur job failed → Voir logs
```

**Erreurs typiques :**
- `body_path: No such file` → Changelog vide
- `Invalid tag name` → Format version incorrect  
- `Resource not accessible` → Permissions token
- `Workflow run not found` → Trigger mal configuré

---

## 🎯 **Tests de Validation**

### **Test 1 : Release Manuelle**
```bash
# Créer tag manuellement pour tester
git tag v2025.10.07-test
git push origin v2025.10.07-test

# Vérifier sur GitHub → Releases
```

### **Test 2 : Commit avec Différents Types**
```bash
# Test différents préfixes
git commit -m "feat: nouvelle fonctionnalité" 
git commit -m "fix: correction bug"
git commit -m "chore: maintenance [skip release]"
```

### **Test 3 : Workflow Debug**
```bash
# Actions → Auto Release (Debug) → Run workflow
# Vérifier les logs sans risque
```

---

## 📊 **État Actuel (Post-Fix)**

### **✅ Corrections Appliquées :**
1. **Contexte workflow_run** : Accès correct aux métadonnées
2. **Changelog robuste** : Fallback si vide
3. **Debug verbeux** : Logs détaillés 
4. **Release options** : `generate_release_notes: true`
5. **Workflow debug** : Test séparé et sûr

### **🧪 Prochains Tests :**
1. **Push actuel** : Vérifier si release fonctionne maintenant
2. **Debug workflow** : Test manuel si besoin
3. **Monitoring** : Observer les prochains push

### **📈 Métriques de Succès :**
- ✅ Release créée automatiquement
- ✅ Version format `v2025.10.07-hash`
- ✅ Changelog avec commits récents  
- ✅ Tag Git et GitHub Release synchronisés

---

## 🚀 **Commandes Utiles**

```bash
# Vérifier tags locaux
git tag --list

# Voir derniers commits
git log --oneline -10

# Forcer sync tags
git fetch --tags

# Supprimer tag défaillant (si besoin)
git tag -d v2025.10.07-bad
git push origin :refs/tags/v2025.10.07-bad
```

Le système devrait maintenant fonctionner ! 🎉

Surveillez le workflow actuel pour confirmer que la release se crée correctement.