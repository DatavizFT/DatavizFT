"""
Test de la nouvelle architecture backend
Vérifie que tous les imports et la structure fonctionnent
"""

def test_imports_data():
    """Test des imports du module data"""
    try:
        from backend.data import (
            COMPETENCES_REFERENTIEL,
            CATEGORIES_COMPETENCES,
            NB_CATEGORIES,
            NB_COMPETENCES_TOTAL,
            charger_competences_referentiel,
        )
        print("✅ Imports backend.data OK")
        print(f"   📊 {NB_CATEGORIES} catégories, {NB_COMPETENCES_TOTAL} compétences")
        return True
    except ImportError as e:
        print(f"❌ Erreur import backend.data: {e}")
        return False


def test_imports_models():
    """Test des imports des modèles Pydantic"""
    try:
        from backend.models import (
            OffreFranceTravail,
            OffreEmploiModel,
            CompetenceModel,
            CompetenceStats,
        )
        print("✅ Imports backend.models OK")
        print(f"   🎯 Modèles Pydantic disponibles")
        return True
    except ImportError as e:
        print(f"❌ Erreur import backend.models: {e}")
        return False


def test_imports_database():
    """Test des imports de la couche database"""
    try:
        from backend.database import (
            DatabaseConnection,
            get_database,
            OffresRepository,
            CompetencesRepository,
        )
        print("✅ Imports backend.database OK")
        print(f"   🗄️ Couche MongoDB disponible")
        return True
    except ImportError as e:
        print(f"❌ Erreur import backend.database: {e}")
        return False


def test_imports_backend_principal():
    """Test de l'import principal du backend"""
    try:
        from backend import (
            COMPETENCES_REFERENTIEL,
            FranceTravailAPIClient,
            PipelineM1805,
            run_pipelineFT,
            info_systeme,
        )
        print("✅ Imports backend principal OK")
        
        # Test de la fonction info système
        info = info_systeme()
        print(f"   ℹ️ Version: {info['version']}")
        print(f"   📊 {info['nb_categories_competences']} catégories")
        
        return True
    except ImportError as e:
        print(f"❌ Erreur import backend principal: {e}")
        return False


def test_creation_models():
    """Test de création d'instances des modèles"""
    try:
        from backend.models import CompetenceModel, CategorieCompetence
        from datetime import datetime
        
        # Test création compétence
        competence = CompetenceModel(
            nom="Python",
            categorie=CategorieCompetence.LANGAGES_PROGRAMMATION,
            synonymes=["python3", "py"],
            popularite=0.9
        )
        
        print("✅ Création modèles Pydantic OK")
        print(f"   🐍 Compétence créée: {competence.nom} ({competence.nom_normalise})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création modèles: {e}")
        return False


def main():
    """Lance tous les tests"""
    print("🧪 Test de la nouvelle architecture backend")
    print("=" * 50)
    
    tests = [
        test_imports_data,
        test_imports_models, 
        test_imports_database,
        test_imports_backend_principal,
        test_creation_models,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Résumé
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    print(f"🎯 Résultats: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 Architecture complètement fonctionnelle !")
        return True
    else:
        print("⚠️ Certains imports nécessitent des corrections")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)