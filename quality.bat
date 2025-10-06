@echo off
REM Script batch simple pour Windows - DatavizFT

if "%1"=="format" (
    echo 🔧 Formatage du code...
    black backend/
    ruff check --fix backend/
    echo ✅ Code formate
    goto :eof
)

if "%1"=="lint" (
    echo 🔍 Verification avec Ruff...
    ruff check backend/
    echo 🔍 Verification des types avec MyPy...
    mypy backend/ --ignore-missing-imports
    echo ✅ Linting termine
    goto :eof
)

if "%1"=="quality" (
    echo 🚀 PIPELINE QUALITE COMPLET
    echo ========================

    echo 1/4 - Formatage...
    black backend/
    ruff check --fix backend/

    echo 2/4 - Linting...
    ruff check backend/
    if errorlevel 1 (
        echo ❌ Erreurs Ruff detectees
        exit /b 1
    )

    echo 3/4 - Types...
    mypy backend/ --ignore-missing-imports

    echo 4/4 - Code mort...
    vulture backend/ --config vulture.toml --min-confidence 80

    echo ✅ QUALITE VALIDEE - Code pret pour commit!
    goto :eof
)

if "%1"=="dead-code" (
    echo 🔍 Analyse du code mort...
    vulture backend/ --config vulture.toml --min-confidence 80
    echo ✅ Analyse terminee
    goto :eof
)

if "%1"=="clean" (
    echo 🧹 Nettoyage...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul
    if exist .coverage del .coverage
    if exist htmlcov rd /s /q htmlcov
    if exist .pytest_cache rd /s /q .pytest_cache
    echo ✅ Nettoyage termine
    goto :eof
)

echo Usage: quality.bat [format^|lint^|quality^|dead-code^|clean]
echo.
echo Commands:
echo   format     - Format code with black and ruff
echo   lint       - Run linting checks
echo   quality    - Full quality pipeline
echo   dead-code  - Analyze dead code
echo   clean      - Clean temporary files