# =============================================================================
# Telechargement Docker Desktop - Architecture Intel AMD64
# =============================================================================

Write-Host "Telechargement Docker Desktop pour votre systeme" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

Write-Host ""
Write-Host "Votre configuration detectee:" -ForegroundColor Cyan
Write-Host "  Processeur: Intel(R) Core(TM) i9-14900KF" -ForegroundColor White
Write-Host "  Architecture: x64-based PC (AMD64)" -ForegroundColor White
Write-Host "  Version requise: Docker Desktop AMD64" -ForegroundColor Green

Write-Host ""
Write-Host "Liens de telechargement officiels:" -ForegroundColor Yellow

Write-Host ""
Write-Host "1. Site officiel Docker (Recommande):" -ForegroundColor Cyan
Write-Host "   https://www.docker.com/products/docker-desktop/windows/" -ForegroundColor White
Write-Host "   -> Cliquez sur 'Download for Windows (AMD64)'" -ForegroundColor Green

Write-Host ""
Write-Host "2. Lien direct AMD64:" -ForegroundColor Cyan
Write-Host "   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -ForegroundColor White

Write-Host ""
Write-Host "Specifications du fichier:" -ForegroundColor Yellow
Write-Host "  Nom: Docker Desktop Installer.exe" -ForegroundColor White
Write-Host "  Architecture: AMD64 (x64)" -ForegroundColor White
Write-Host "  Taille: ~500-600 MB" -ForegroundColor White
Write-Host "  Compatible: Windows 10/11 64-bit" -ForegroundColor White

Write-Host ""
Write-Host "Verification avant installation:" -ForegroundColor Red
Write-Host "  Version Windows minimale: Windows 10 Pro/Enterprise/Education (Build 19041+)" -ForegroundColor Yellow
Write-Host "  ou Windows 11 (toutes editions)" -ForegroundColor Yellow
Write-Host "  WSL2 sera installe automatiquement si necessaire" -ForegroundColor Yellow
Write-Host "  Virtualisation activee dans le BIOS" -ForegroundColor Yellow

Write-Host ""
$choice = Read-Host "Voulez-vous ouvrir le site de telechargement? (o/n)"

if ($choice -eq 'o' -or $choice -eq 'O' -or $choice -eq 'oui') {
    Write-Host "Ouverture du site Docker..." -ForegroundColor Green
    Start-Process "https://www.docker.com/products/docker-desktop/windows/"
    
    Write-Host ""
    Write-Host "Instructions d'installation:" -ForegroundColor Cyan
    Write-Host "1. Telechargez 'Docker Desktop for Windows (AMD64)'" -ForegroundColor White
    Write-Host "2. Executez le fichier en tant qu'Administrateur" -ForegroundColor White  
    Write-Host "3. Acceptez les parametres par defaut" -ForegroundColor White
    Write-Host "4. Redemarrez si demande" -ForegroundColor White
    Write-Host "5. Lancez Docker Desktop apres redemarrage" -ForegroundColor White
    Write-Host "6. Attendez que l'icone soit verte (Engine started)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Apres installation, testez avec:" -ForegroundColor Green
    Write-Host "  python scripts/check_docker.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Support en cas de probleme:" -ForegroundColor Yellow
Write-Host "  Documentation: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor White
Write-Host "  Troubleshooting: https://docs.docker.com/desktop/troubleshoot/overview/" -ForegroundColor White

Write-Host ""
Write-Host "Alternatives si Docker Desktop pose probleme:" -ForegroundColor Cyan
Write-Host "  1. MongoDB Atlas (cloud gratuit): docs/mongodb_atlas_setup.md" -ForegroundColor White
Write-Host "  2. Installation MongoDB locale: scripts/install_mongodb.ps1" -ForegroundColor White