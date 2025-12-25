# =============================================================================
# Guide d'installation MongoDB sur Windows
# =============================================================================

# -----------------------------------------------------------------------------
# Option 1: Installation avec Chocolatey (Recommandée)
# -----------------------------------------------------------------------------

# 1. Installer Chocolatey si pas déjà fait (en PowerShell Admin)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# 2. Installer MongoDB
choco install mongodb

# 3. Démarrer le service MongoDB
net start MongoDB

# -----------------------------------------------------------------------------
# Option 2: Installation manuelle
# -----------------------------------------------------------------------------

# 1. Télécharger MongoDB Community Server 7.0 depuis:
#    https://www.mongodb.com/try/download/community

# 2. Installer avec les options par défaut

# 3. Créer les dossiers de données
md C:\data\db

# 4. Démarrer MongoDB manuellement
# "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db

# -----------------------------------------------------------------------------
# Option 3: MongoDB Atlas (Cloud - Plus simple)
# -----------------------------------------------------------------------------

# 1. Créer un compte gratuit sur https://cloud.mongodb.com
# 2. Créer un cluster gratuit (M0 Sandbox)
# 3. Configurer l'accès réseau (0.0.0.0/0 pour développement)
# 4. Créer un utilisateur DB
# 5. Récupérer la chaîne de connexion

# Exemple de chaîne Atlas:
# mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/dataviz_ft_dev?retryWrites=true&w=majority

# -----------------------------------------------------------------------------
# Vérification de l'installation
# -----------------------------------------------------------------------------

# Test de connexion
mongo --version

# Connexion au shell MongoDB
mongo

# Dans le shell MongoDB:
# use dataviz_ft_dev
# db.test.insertOne({message: "Hello MongoDB!"})
# db.test.find()