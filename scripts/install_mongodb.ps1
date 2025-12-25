# =============================================================================
# Script d'installation MongoDB pour DatavizFT (Windows)
# =============================================================================

Write-Host "🚀 Installation MongoDB pour DatavizFT" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Test si MongoDB est déjà installé
try {
    $mongoVersion = & mongo --version 2>$null
    if ($mongoVersion) {
        Write-Host "✅ MongoDB déjà installé: $mongoVersion" -ForegroundColor Green
        Write-Host "🔄 Tentative de démarrage du service..." -ForegroundColor Yellow
        
        # Démarrer le service MongoDB
        try {
            Start-Service -Name "MongoDB" -ErrorAction Stop
            Write-Host "✅ Service MongoDB démarré" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Impossible de démarrer le service MongoDB automatiquement" -ForegroundColor Yellow
            Write-Host "   Essayez: net start MongoDB" -ForegroundColor Cyan
        }
        
        exit 0
    }
}
catch {
    Write-Host "📥 MongoDB non détecté, installation nécessaire..." -ForegroundColor Yellow
}

# Options d'installation
Write-Host ""
Write-Host "Choisissez une méthode d'installation:" -ForegroundColor Cyan
Write-Host "1. 🍫 Chocolatey (Recommandé - automatique)" -ForegroundColor White
Write-Host "2. 📥 Téléchargement manuel" -ForegroundColor White  
Write-Host "3. ☁️  MongoDB Atlas (Cloud gratuit)" -ForegroundColor White
Write-Host "4. 🐳 Docker Desktop (si disponible)" -ForegroundColor White

$choice = Read-Host "`nEntrez votre choix (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🍫 Installation via Chocolatey..." -ForegroundColor Green
        
        # Vérifier si Chocolatey est installé
        try {
            $chocoVersion = & choco --version 2>$null
            Write-Host "✅ Chocolatey détecté: $chocoVersion" -ForegroundColor Green
        }
        catch {
            Write-Host "📥 Installation de Chocolatey..." -ForegroundColor Yellow
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        }
        
        # Installer MongoDB
        Write-Host "📦 Installation de MongoDB Community..." -ForegroundColor Yellow
        & choco install mongodb -y
        
        # Créer le dossier de données
        $dataPath = "C:\data\db"
        if (!(Test-Path $dataPath)) {
            New-Item -ItemType Directory -Path $dataPath -Force
            Write-Host "✅ Dossier de données créé: $dataPath" -ForegroundColor Green
        }
        
        # Démarrer le service
        Write-Host "🔄 Démarrage du service MongoDB..." -ForegroundColor Yellow
        Start-Service -Name "MongoDB"
        Write-Host "✅ MongoDB installé et démarré!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "`n📥 Installation manuelle..." -ForegroundColor Green
        Write-Host "1. Allez sur: https://www.mongodb.com/try/download/community" -ForegroundColor Cyan
        Write-Host "2. Téléchargez MongoDB Community Server 7.0 pour Windows" -ForegroundColor Cyan  
        Write-Host "3. Installez avec les options par défaut" -ForegroundColor Cyan
        Write-Host "4. Revenez ici et relancez ce script" -ForegroundColor Cyan
        
        Read-Host "`nAppuyez sur Entrée après l'installation..."
    }
    
    "3" {
        Write-Host "`n☁️  Configuration MongoDB Atlas..." -ForegroundColor Green
        Write-Host "1. Créez un compte sur: https://cloud.mongodb.com" -ForegroundColor Cyan
        Write-Host "2. Créez un cluster gratuit (M0 Sandbox)" -ForegroundColor Cyan
        Write-Host "3. Configurez l'accès réseau (ajoutez 0.0.0.0/0 pour dev)" -ForegroundColor Cyan
        Write-Host "4. Créez un utilisateur de base de données" -ForegroundColor Cyan
        Write-Host "5. Récupérez la chaîne de connexion" -ForegroundColor Cyan
        
        Write-Host "`nExemple de chaîne de connexion Atlas:" -ForegroundColor Yellow
        Write-Host "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/dataviz_ft_dev" -ForegroundColor White
        
        $atlasUrl = Read-Host "`nEntrez votre chaîne de connexion Atlas (optionnel)"
        if ($atlasUrl) {
            # Mettre à jour le fichier .env
            $envPath = ".env"
            if (Test-Path $envPath) {
                $envContent = Get-Content $envPath -Raw
                $newLine = "MONGODB_URL=" + $atlasUrl
                $envContent = $envContent -replace 'MONGODB_URL=.*', $newLine
                Set-Content -Path $envPath -Value $envContent
                Write-Host "✅ Fichier .env mis à jour avec Atlas" -ForegroundColor Green
            }
        }
        
        Write-Host "✅ Configuration Atlas terminée!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host "`n🐳 Vérification de Docker..." -ForegroundColor Green
        try {
            $dockerVersion = & docker --version 2>$null
            Write-Host "✅ Docker détecté: $dockerVersion" -ForegroundColor Green
            
            Write-Host "🔄 Démarrage de MongoDB avec Docker..." -ForegroundColor Yellow
            & docker run -d --name datavizft_mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=datavizft2025 mongo:7.0
            
            Write-Host "✅ MongoDB démarré dans Docker!" -ForegroundColor Green
            Write-Host "📊 Interface: docker exec -it datavizft_mongodb mongosh" -ForegroundColor Cyan
        }
        catch {
            Write-Host "❌ Docker non détecté. Installez Docker Desktop puis relancez." -ForegroundColor Red
            Write-Host "   Téléchargement: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
        }
    }
    
    default {
        Write-Host "❌ Choix invalide. Relancez le script." -ForegroundColor Red
        exit 1
    }
}

# Test de connexion final
Write-Host "`n🔍 Test de connexion à MongoDB..." -ForegroundColor Yellow
try {
    # Test avec mongosh (nouveau) ou mongo (ancien)
    try {
        & mongosh --eval "db.version()" --quiet 2>$null
        Write-Host "✅ Connexion MongoDB réussie avec mongosh!" -ForegroundColor Green
    }
    catch {
        & mongo --eval "db.version()" --quiet 2>$null  
        Write-Host "✅ Connexion MongoDB réussie avec mongo!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "🎉 MongoDB est prêt pour DatavizFT!" -ForegroundColor Green
    Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "   1. python scripts/test_mongodb.py" -ForegroundColor White
    Write-Host "   2. python backend/main.py --stats" -ForegroundColor White
    
}
catch {
    Write-Host "⚠️  Impossible de se connecter à MongoDB" -ForegroundColor Yellow
    Write-Host "   Vérifiez que le service est démarré:" -ForegroundColor Cyan
    Write-Host "   - Windows: net start MongoDB" -ForegroundColor White
    Write-Host "   - Docker: docker start datavizft_mongodb" -ForegroundColor White
}