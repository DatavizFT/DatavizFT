# 🌟 Configuration MongoDB Atlas pour DatavizFT

## 📋 **Étapes rapides pour MongoDB Atlas**

### **1. Créer un compte MongoDB Atlas**
1. Allez sur [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Créez un compte gratuit
3. Cliquez sur "Build a Database"

### **2. Configurer le cluster gratuit**
1. Choisissez **M0 Sandbox** (GRATUIT)
2. Sélectionnez le fournisseur **AWS** 
3. Région recommandée : **Ireland (eu-west-1)** ou **Virginia (us-east-1)**
4. Nom du cluster : `datavizft-cluster`

### **3. Configurer la sécurité**
1. **Utilisateur de base** :
   - Nom d'utilisateur : `datavizft_user`
   - Mot de passe : `SecurePassword123!` (notez-le bien)
   
2. **Accès réseau** :
   - Ajoutez votre IP actuelle
   - **Pour le développement** : Ajoutez `0.0.0.0/0` (toutes les IP)

### **4. Récupérer la chaîne de connexion**
1. Cliquez sur "Connect"
2. Choisissez "Connect your application"
3. Driver : **Python** version **3.12 or later**
4. Copiez la chaîne de connexion (ressemble à) :
   ```
   mongodb+srv://datavizft_user:SecurePassword123!@datavizft-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### **5. Mise à jour du fichier .env**
Remplacez la ligne `MONGODB_URL` dans votre fichier `.env` par :
```properties
MONGODB_URL=mongodb+srv://datavizft_user:SecurePassword123!@datavizft-cluster.xxxxx.mongodb.net/dataviz_ft_dev?retryWrites=true&w=majority
```

### **6. Test de connexion**
Exécutez le script de test :
```bash
python scripts/test_mongodb.py
```

## 🎯 **Avantages de MongoDB Atlas**
- ✅ **Aucune installation locale** nécessaire
- ✅ **500 Mo gratuits** (largement suffisant pour DatavizFT)
- ✅ **Sauvegardes automatiques**
- ✅ **Interface web** pour visualiser les données
- ✅ **Disponible 24/7** sans maintenance
- ✅ **SSL/TLS** automatique (sécurisé)

## 📊 **Interface Web Atlas**
Une fois configuré, vous pouvez :
- Visualiser vos collections sur [cloud.mongodb.com](https://cloud.mongodb.com)
- Exécuter des requêtes directement dans le navigateur
- Surveiller les performances
- Gérer les index

## 🔄 **Migration future vers local**
Si vous voulez passer au local plus tard :
1. Exportez vos données Atlas : `mongodump`
2. Installez MongoDB localement
3. Importez vos données : `mongorestore`
4. Changez juste la `MONGODB_URL` dans `.env`