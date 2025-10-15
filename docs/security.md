# 🔒 Sécurité dans DatavizFT

## 📋 **Pipeline de sécurité en place**

### **1. CodeQL (GitHub Advanced Security)**
- **🎯 Analyse statique avancée** du code source Python
- **🕵️ Détection automatique** de vulnérabilités (injections, XSS, etc.)
- **📅 Exécution** : À chaque push, PR et lundi à 2h30 (scan complet)
- **🏷️ Catégories** : CWE Top 25, OWASP Top 10, et plus
- **📊 Résultats** : Visible dans l'onglet "Security" de GitHub

### **2. Bandit (Sécurité Python spécialisée)**
- **🔍 Scanner AST** pour vulnérabilités Python communes
- **🎯 Détections** : Hardcoded passwords, SQL injection, shell injection
- **⚡ Exécution** : À chaque CI/CD dans le job `security`
- **📋 Format** : JSON avec détails des vulnérabilités

### **3. Safety (Vulnérabilités des dépendances)**
- **📦 Analyse des packages** pip installés
- **🗄️ Base de données** : PyUp.io Security Database
- **🚨 Alertes** : CVE et vulnérabilités connues
- **🔄 Mise à jour** : Continue avec la base SafetyDB

## 🛡️ **Configuration de sécurité**

### **Variables d'environnement sécurisées**
```bash
# .env (non versionné)
FRANCETRAVAIL_CLIENT_SECRET=********  # Secrets GitHub
TOKEN_URL=https://auth.francetravail.io  # URLs officielles uniquement
```

### **Pratiques de code sécurisé**
- ✅ **Validation d'entrée** avec Pydantic V2
- ✅ **Pas de secrets hardcodés** (variables d'environnement)
- ✅ **HTTPS uniquement** pour les API calls
- ✅ **Timeout des requêtes** (prévention DoS)
- ✅ **Gestion d'erreurs** sans leak d'informations

## 📊 **Monitoring sécuritaire**

### **Logs de sécurité structurés**
```python
logger.warning("Tentative d'accès non autorisé", extra={
    "source_ip": request.client.host,
    "endpoint": "/api/sensitive",
    "user_agent": request.headers.get("user-agent")
})
```

### **Métriques de sécurité**
- 🔒 **0 vulnérabilité critique** détectée
- 🛡️ **100% HTTPS** pour les API externes
- 📋 **Logs complets** avec rotation sécurisée
- 🔐 **Secrets isolés** du code source

## 🚨 **Alertes automatiques**

### **GitHub Security Advisories**
- **Notifications** automatiques des nouvelles CVE
- **Dependabot** pour les mises à jour de sécurité
- **Code scanning** alerts en temps réel

### **Actions sur détection**
1. **🚨 Alerte immédiate** dans GitHub Issues/Security
2. **🛑 Blocage PR** si vulnérabilité critique
3. **📧 Notification** des mainteneurs
4. **📋 Rapport détaillé** avec recommandations

## 🔧 **Tests de sécurité locaux**

```bash
# Scan sécurité complet local
bandit -r backend/ -f json
safety check --json
python -m pip audit  # Python 3.11+ built-in

# Vérification secrets
git-secrets --scan
truffleHog --regex --entropy=False .
```

## 📚 **Ressources sécurité**

- [OWASP Top 10](https://owasp.org/Top10/)
- [Python Security Guide](https://python-security.readthedocs.io/)
- [GitHub Security Lab](https://securitylab.github.com/)
- [CodeQL Documentation](https://codeql.github.com/docs/)

---

**🎯 Objectif** : Zero Trust, Defense in Depth, Security by Design