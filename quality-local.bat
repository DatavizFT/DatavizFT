@echo off
REM ===============================================
REM Script de qualité locale pour DatavizFT
REM Exécute les mêmes vérifications que la CI/CD
REM ===============================================

echo 🚀 PIPELINE DE QUALITE LOCALE DatavizFT
echo ==========================================
echo.

REM Vérification que nous sommes dans le bon dossier
if not exist "backend\" (
    echo ❌ Erreur: Ce script doit être exécuté depuis la racine du projet DatavizFT
    echo    Assurez-vous d'être dans le dossier contenant backend/
    pause
    exit /b 1
)

echo 📋 1/5 - Formatage du code avec Black...
python -m black backend/
if %errorlevel% neq 0 (
    echo ❌ Échec du formatage Black
    pause
    exit /b 1
)
echo ✅ Black: Code formaté avec succès
echo.

echo 📋 2/5 - Vérification du formatage...
python -m black --check backend/
if %errorlevel% neq 0 (
    echo ❌ Échec: Code non conforme au style Black
    pause
    exit /b 1
)
echo ✅ Black Check: Code conforme au style
echo.

echo 📋 3/5 - Analyse avec Ruff...
python -m ruff check backend/
if %errorlevel% neq 0 (
    echo ❌ Échec: Problèmes détectés par Ruff
    pause
    exit /b 1
)
echo ✅ Ruff: Aucun problème détecté
echo.

echo 📋 4/5 - Type checking avec MyPy...
python -m mypy backend/ --ignore-missing-imports
if %errorlevel% neq 0 (
    echo ⚠️  MyPy: Problèmes de types détectés (non bloquant)
) else (
    echo ✅ MyPy: Types valides
)
echo.

echo 📋 5/5 - Analyse sécurité avec Bandit...
python -m bandit -r backend/ -f txt
if %errorlevel% neq 0 (
    echo ⚠️  Bandit: Problèmes de sécurité détectés (vérifiez manuellement)
) else (
    echo ✅ Bandit: Aucun problème de sécurité critique
)
echo.

echo 🎉 PIPELINE DE QUALITE TERMINE
echo ================================
echo ✅ Votre code est prêt pour le commit/push !
echo 💡 Conseil: Exécutez ce script avant chaque commit
echo.
pause