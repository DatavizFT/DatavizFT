# =============================================================================
# Guide d'installation manuelle Docker Desktop
# =============================================================================

Write-Host "Installation manuelle Docker Desktop" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

Write-Host ""
Write-Host "Etapes d'installation:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Telechargement Docker Desktop:" -ForegroundColor Yellow
Write-Host "   Allez sur: https://www.docker.com/products/docker-desktop/windows/" -ForegroundColor White
Write-Host "   Telechargez 'Docker Desktop for Windows'" -ForegroundColor White
Write-Host "   Fichier: ~500MB (Docker Desktop Installer.exe)" -ForegroundColor White

Write-Host ""
Write-Host "2. Installation:" -ForegroundColor Yellow
Write-Host "   Executez le fichier telecharge en tant qu'Administrateur" -ForegroundColor White
Write-Host "   Acceptez les parametres par defaut" -ForegroundColor White
Write-Host "   L'installation peut prendre 5-10 minutes" -ForegroundColor White

Write-Host ""
Write-Host "3. Redemarrage:" -ForegroundColor Yellow
Write-Host "   Redemarrez votre ordinateur quand demande" -ForegroundColor White
Write-Host "   Le redemarrage est necessaire pour WSL2" -ForegroundColor White

Write-Host ""
Write-Host "4. Premier demarrage:" -ForegroundColor Yellow
Write-Host "   Lancez Docker Desktop depuis le bureau" -ForegroundColor White
Write-Host "   Acceptez les conditions d'utilisation" -ForegroundColor White
Write-Host "   Attendez que l'Engine demarre (cercle vert)" -ForegroundColor White

Write-Host ""
Write-Host "5. Verification:" -ForegroundColor Yellow
Write-Host "   Revenez ici et tapez: docker --version" -ForegroundColor White
Write-Host "   Si ca fonctionne, continuez avec le script suivant" -ForegroundColor White

Write-Host ""
Write-Host "Si vous rencontrez des problemes:" -ForegroundColor Red
Write-Host "   WSL2 non installe: Windows Update puis relancer Docker" -ForegroundColor Yellow
Write-Host "   Virtualisation desactivee: Activer dans le BIOS" -ForegroundColor Yellow
Write-Host "   Hyper-V requis: Activer dans 'Fonctionnalites Windows'" -ForegroundColor Yellow

Write-Host ""
Write-Host "Une fois Docker Desktop installe et fonctionnel:" -ForegroundColor Green
Write-Host "   python scripts/setup_docker_persistence.py" -ForegroundColor Cyan

Write-Host ""
$input = Read-Host "Appuyez sur Entree pour ouvrir la page de telechargement..."

# Ouvrir la page de téléchargement
Start-Process "https://www.docker.com/products/docker-desktop/windows/"

Write-Host ""
Write-Host "Pendant l'installation, vous pouvez:" -ForegroundColor Cyan
Write-Host "   1. Lire la documentation MongoDB dans docs/" -ForegroundColor White
Write-Host "   2. Examiner les scripts dans scripts/" -ForegroundColor White  
Write-Host "   3. Personnaliser les variables dans .env" -ForegroundColor White

Write-Host ""
Write-Host "A bientot pour la configuration de la persistance!" -ForegroundColor Green