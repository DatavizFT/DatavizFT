# 🔐 Fix Permissions Release - Guide GitHub

## 🚨 **Erreur 403 : "Resource not accessible by integration"**

### **Problème Identifié**
```
⚠️ GitHub release failed with status: 403
{"message":"Resource not accessible by integration"}
```

Le `GITHUB_TOKEN` automatique n'a pas les permissions pour créer des releases.

---

## 🎯 **Solutions (3 Options)**

### **✅ Option 1 : Permissions Repository (RECOMMANDÉE)**

#### **Sur GitHub.com :**
```
1. Aller sur : https://github.com/DatavizFT/DatavizFT/settings/actions
2. Scroller vers "Workflow permissions" 
3. Sélectionner "Read and write permissions"
4. ✅ Cocher "Allow GitHub Actions to create and approve pull requests"
5. Cliquer "Save"
```

#### **Capture d'écran des options :**
```
○ Read repository contents and packages permissions (Default)
● Read and write permissions  ← Sélectionner celle-ci
  
☐ Allow GitHub Actions to create and approve pull requests
☑ Allow GitHub Actions to create and approve pull requests  ← Cocher
```

---

### **✅ Option 2 : Token Personnel (PAT)**

#### **Créer un Personal Access Token :**
```
1. GitHub → Settings (votre profil) → Developer settings
2. Personal access tokens → Tokens (classic)
3. "Generate new token (classic)"
4. Nom : "DatavizFT Release Token"  
5. Expiration : 90 days (ou plus)
6. Permissions requises :
   ✅ repo (Full control)
   ✅ write:packages
   ✅ read:packages
7. Generate token → COPIER le token
```

#### **Ajouter le Token aux Secrets :**
```
1. Repo → Settings → Secrets and variables → Actions
2. "New repository secret"
3. Nom : PAT_TOKEN
4. Valeur : [collez votre token généré]
5. Add secret
```

---

### **✅ Option 3 : Test Manuel Temporaire**

#### **Release Manuelle pour Test :**
```bash
# Créer release localement pour tester
git tag v2025.10.07-manual
git push origin v2025.10.07-manual

# Puis sur GitHub → Releases → Draft new release
# Tag : v2025.10.07-manual  
# Title : Test Release Manual
# Description : Test de création manuelle
```

---

## 🔍 **Vérification des Permissions Actuelles**

### **Vérifier Settings Repository :**
```
GitHub → DatavizFT repo → Settings → Actions → General

Chercher section "Workflow permissions" :
- Si "Read repository contents..." est sélectionné → Problème !
- Si "Read and write permissions" est sélectionné → OK !
```

### **Vérifier via API (optionnel) :**
```bash
# Tester permissions avec curl
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/DatavizFT/DatavizFT
     
# Si 200 OK → token fonctionne
# Si 403 → permissions insuffisantes
```

---

## 🎮 **Test des Corrections**

### **Test 1 : Push Simple**
```bash
# Après avoir configuré les permissions
git add .
git commit -m "test: vérification permissions release"
git push

# Observer : CI/CD → Auto Release devrait fonctionner
```

### **Test 2 : Workflow Debug**
```bash
# GitHub → Actions → "Auto Release (Debug)" → Run workflow
# Vérifier si release draft se crée sans erreur
```

### **Test 3 : Release Manuelle**
```bash
# GitHub → Releases → "Create a new release"  
# Tester manuellement pour valider permissions
```

---

## 📊 **État des Corrections**

### **✅ Code Modifié :**
1. **Permissions ajoutées** dans workflow :
   ```yaml
   permissions:
     contents: write
     packages: write
     actions: read
   ```

2. **Fallback PAT** configuré :
   ```yaml
   GITHUB_TOKEN: ${{ secrets.PAT_TOKEN || secrets.GITHUB_TOKEN }}
   ```

### **⚙️ Configuration GitHub Requise :**
- **Option 1** : Workflow permissions → "Read and write" ✅
- **Option 2** : PAT Token dans secrets (si Option 1 échoue)

---

## 🚀 **Action Immédiate**

### **1. Configurer Permissions (5 minutes)**
```
GitHub.com → DatavizFT → Settings → Actions → Workflow permissions
→ Sélectionner "Read and write permissions"
→ Cocher "Allow GitHub Actions to create and approve pull requests"  
→ Save
```

### **2. Tester**
```bash
git commit -m "test: permissions release configurées" --allow-empty
git push
# Observer le workflow dans Actions
```

### **3. Valider**
```
GitHub → Releases → Vérifier nouvelle release créée
Tag format : v2025.10.07-[hash]
```

---

## ⚡ **Résolution Rapide (1 minute)**

**Si vous voulez juste que ça marche MAINTENANT :**

```
1. https://github.com/DatavizFT/DatavizFT/settings/actions
2. Workflow permissions → "Read and write permissions" 
3. ✅ Allow GitHub Actions to create and approve pull requests
4. Save
5. git push (re-déclencher)
```

**C'est tout !** 🎉

La prochaine fois que le CI/CD finit, l'Auto Release devrait fonctionner parfaitement.