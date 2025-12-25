# =============================================================================
# Installation Docker Desktop pour DatavizFT MongoDB
# =============================================================================

Write-Host "🐳 Installation Docker Desktop pour DatavizFT" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Vérifier si Docker est déjà installé
try {
    $dockerVersion = & docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker déjà installé: $dockerVersion" -ForegroundColor Green
        
        # Vérifier si Docker est en cours d'exécution
        try {
            & docker info > $null 2>&1
            Write-Host "✅ Docker Engine fonctionne" -ForegroundColor Green
            
            Write-Host "`n🚀 Démarrage MongoDB avec persistance..." -ForegroundColor Yellow
            & docker compose up -d mongodb mongo-express
            
            Write-Host "✅ MongoDB démarré avec persistance!" -ForegroundColor Green
            Write-Host "📊 Interface: http://localhost:8081 (datavizft / admin123)" -ForegroundColor Cyan
            Write-Host "🔗 Connexion: mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin" -ForegroundColor Cyan
            
            exit 0
        }
        catch {
            Write-Host "⚠️  Docker installé mais Engine arrêté" -ForegroundColor Yellow
            Write-Host "   Démarrez Docker Desktop puis relancez ce script" -ForegroundColor Cyan
        }
    }
}
catch {
    Write-Host "📥 Docker non détecté, installation nécessaire..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Méthodes d'installation Docker:" -ForegroundColor Cyan
Write-Host "1. 🍫 Chocolatey (Automatique)" -ForegroundColor White
Write-Host "2. 📥 Téléchargement manuel Docker Desktop" -ForegroundColor White
Write-Host "3. 🏠 Installation MongoDB locale (sans Docker)" -ForegroundColor White

$choice = Read-Host "`nEntrez votre choix (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`n🍫 Installation Docker via Chocolatey..." -ForegroundColor Green
        
        # Vérifier Chocolatey
        try {
            & choco --version > $null 2>&1
            Write-Host "✅ Chocolatey détecté" -ForegroundColor Green
        }
        catch {
            Write-Host "📥 Installation de Chocolatey..." -ForegroundColor Yellow
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        }
        
        # Installer Docker Desktop
        Write-Host "🐳 Installation Docker Desktop..." -ForegroundColor Yellow
        & choco install docker-desktop -y
        
        Write-Host "⚠️  IMPORTANT:" -ForegroundColor Red
        Write-Host "   1. Redémarrez votre ordinateur" -ForegroundColor Cyan
        Write-Host "   2. Lancez Docker Desktop" -ForegroundColor Cyan
        Write-Host "   3. Relancez ce script" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host "`n📥 Installation manuelle Docker Desktop..." -ForegroundColor Green
        Write-Host "1. Allez sur: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
        Write-Host "2. Téléchargez Docker Desktop pour Windows" -ForegroundColor Cyan
        Write-Host "3. Installez et redémarrez votre ordinateur" -ForegroundColor Cyan
        Write-Host "4. Lancez Docker Desktop" -ForegroundColor Cyan
        Write-Host "5. Revenez ici et relancez ce script" -ForegroundColor Cyan
        
        Read-Host "`nAppuyez sur Entrée après l'installation..."
    }
    
    "3" {
        Write-Host "`n🏠 Installation MongoDB locale..." -ForegroundColor Green
        Write-Host "Lancement du script d'installation MongoDB..." -ForegroundColor Yellow
        & powershell -ExecutionPolicy Bypass -File scripts/install_mongodb.ps1
    }
    
    default {
        Write-Host "❌ Choix invalide. Relancez le script." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n📊 Comparaison des options de persistance:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "🐳 Docker Desktop:" -ForegroundColor Cyan
Write-Host "   ✅ Persistance garantie (volumes)" -ForegroundColor Green
Write-Host "   ✅ Isolation et reproductibilité" -ForegroundColor Green
Write-Host "   ✅ Interface Mongo Express incluse" -ForegroundColor Green
Write-Host "   ⚠️  Nécessite Docker Desktop" -ForegroundColor Yellow
Write-Host ""
Write-Host "🏠 MongoDB Local:" -ForegroundColor Cyan
Write-Host "   ✅ Persistance native sur disque" -ForegroundColor Green
Write-Host "   ✅ Performance maximale" -ForegroundColor Green
Write-Host "   ✅ Contrôle total" -ForegroundColor Green
Write-Host "   ⚠️  Configuration manuelle" -ForegroundColor Yellow
Write-Host ""
Write-Host "☁️  MongoDB Atlas:" -ForegroundColor Cyan
Write-Host "   ✅ Sauvegarde automatique cloud" -ForegroundColor Green
Write-Host "   ✅ Haute disponibilité" -ForegroundColor Green
Write-Host "   ✅ Pas d'installation" -ForegroundColor Green
Write-Host "   ⚠️  Limite 512MB gratuit" -ForegroundColor Yellow