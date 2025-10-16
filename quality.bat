@echo off
chcp 65001 >nul
REM ===============================================
REM Script de qualité locale pour DatavizFT
REM Exécute les mêmes vérifications que la CI/CD
REM ===============================================

echo [*] PIPELINE DE QUALITE LOCALE DatavizFT
echo ==========================================
echo.

REM Vérification que nous sommes dans le bon dossier
if not exist "backend\" (
    echo [X] Erreur: Ce script doit être exécuté depuis la racine du projet DatavizFT
    echo     Assurez-vous d'être dans le dossier contenant backend/
    pause
    exit /b 1
)

echo [1/5] - Formatage du code avec Black...
python -m black backend/
if %errorlevel% neq 0 (
    echo [X] Echec du formatage Black
    pause
    exit /b 1
)
echo [OK] Black: Code formate avec succes
echo.

echo [2/5] - Verification du formatage...
python -m black --check backend/
if %errorlevel% neq 0 (
    echo [X] Echec: Code non conforme au style Black
    pause
    exit /b 1
)
echo [OK] Black Check: Code conforme au style
echo.

echo [3/5] - Analyse avec Ruff...
python -m ruff check backend/
if %errorlevel% neq 0 (
    echo [X] Echec: Problemes detectes par Ruff
    pause
    exit /b 1
)
echo [OK] Ruff: Aucun probleme detecte
echo.

echo [4/5] - Type checking avec MyPy...
python -m mypy backend/ --ignore-missing-imports
if %errorlevel% neq 0 (
    echo [!] MyPy: Problemes de types detectes (non bloquant)
) else (
    echo [OK] MyPy: Types valides
)
echo.

echo [5/5] - Analyse securite avec Bandit...
python -m bandit -r backend/ -f txt
if %errorlevel% neq 0 (
    echo [!] Bandit: Problemes de securite detectes (verifiez manuellement)
) else (
    echo [OK] Bandit: Aucun probleme de securite critique
)
echo.

echo [*] PIPELINE DE QUALITE TERMINE
echo ================================
echo [OK] Votre code est pret pour le commit/push !
echo [i] Conseil: Executez ce script avant chaque commit
echo.

REM Pause seulement si pas en mode automatique
if not "%1"=="--auto" (
    pause
)