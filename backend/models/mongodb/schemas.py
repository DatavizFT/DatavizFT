"""
MongoDB Schemas - Définitions de validation MongoDB native
Schemas de validation JSON pour MongoDB (sans dépendance externe)
"""

from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


# Schema de validation pour la collection offres
OFFRE_SCHEMA = {
    "bsonType": "object",
    "required": ["source_id", "intitule", "date_creation"],
    "properties": {
        "source_id": {
            "bsonType": "string",
            "description": "Identifiant unique de l'offre dans le système source"
        },
        "intitule": {
            "bsonType": "string",
            "maxLength": 200,
            "description": "Titre du poste"
        },
        "description": {
            "bsonType": "string",
            "description": "Description complète de l'offre"
        },
        "date_creation": {
            "bsonType": "date",
            "description": "Date de création de l'offre"
        },
        "date_actualisation": {
            "bsonType": ["date", "null"],
            "description": "Date de dernière mise à jour"
        },
        "date_collecte": {
            "bsonType": "date", 
            "description": "Date de collecte par notre système"
        },
        "entreprise_nom": {
            "bsonType": ["string", "null"],
            "maxLength": 100
        },
        "secteur_activite": {
            "bsonType": ["string", "null"],
            "maxLength": 100
        },
        "localisation": {
            "bsonType": "object",
            "description": "Informations géographiques"
        },
        "competences_brutes": {
            "bsonType": ["string", "null"],
            "description": "Texte brut pour extraction de compétences"
        },
        "competences_extraites": {
            "bsonType": "array",
            "items": {
                "bsonType": "string",
                "maxLength": 50
            },
            "description": "Compétences détectées et normalisées"
        },
        "type_contrat": {
            "bsonType": ["string", "null"],
            "maxLength": 50
        },
        "salaire_min": {
            "bsonType": ["number", "null"],
            "minimum": 0,
            "description": "Salaire minimum en euros"
        },
        "salaire_max": {
            "bsonType": ["number", "null"], 
            "minimum": 0,
            "description": "Salaire maximum en euros"
        },
        "version_extraction": {
            "bsonType": "string",
            "description": "Version de l'algorithme d'extraction"
        },
        "qualite_score": {
            "bsonType": ["number", "null"],
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Score qualité de l'extraction"
        }
    }
}

# Schema pour la collection compétences
COMPETENCE_SCHEMA = {
    "bsonType": "object",
    "required": ["nom", "nom_normalise", "categorie"],
    "properties": {
        "nom": {
            "bsonType": "string",
            "maxLength": 100,
            "description": "Nom de la compétence"
        },
        "nom_normalise": {
            "bsonType": "string",
            "maxLength": 100,
            "description": "Nom normalisé (unique)"
        },
        "categorie": {
            "bsonType": "string",
            "enum": [
                "langages_programmation",
                "frameworks_libraries", 
                "bases_donnees",
                "cloud_devops",
                "outils_developpement",
                "systemes_os",
                "methodologies",
                "soft_skills"
            ]
        },
        "synonymes": {
            "bsonType": "array",
            "items": {
                "bsonType": "string",
                "maxLength": 100
            }
        },
        "popularite": {
            "bsonType": ["number", "null"],
            "minimum": 0.0,
            "maximum": 1.0
        },
        "difficulte": {
            "bsonType": ["int", "null"],
            "minimum": 1,
            "maximum": 5
        },
        "tags": {
            "bsonType": "array",
            "items": {
                "bsonType": "string",
                "maxLength": 30
            }
        }
    }
}

# Schema pour les statistiques
STATS_SCHEMA = {
    "bsonType": "object",
    "required": ["periode_analysee", "date_analyse", "nb_offres_analysees"],
    "properties": {
        "periode_analysee": {
            "bsonType": "string",
            "maxLength": 20,
            "description": "Période au format YYYY-MM ou YYYY-QN"
        },
        "date_analyse": {
            "bsonType": "date",
            "description": "Date de génération des statistiques"
        },
        "nb_offres_analysees": {
            "bsonType": "int",
            "minimum": 0
        },
        "competences_stats": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "required": ["competence", "nb_offres", "pourcentage"],
                "properties": {
                    "competence": {"bsonType": "string"},
                    "nb_offres": {"bsonType": "int", "minimum": 0},
                    "pourcentage": {"bsonType": "number", "minimum": 0, "maximum": 100},
                    "salaire_moyen": {"bsonType": ["number", "null"]}
                }
            }
        },
        "top_competences": {
            "bsonType": "array",
            "maxItems": 50,
            "items": {"bsonType": "string"}
        }
    }
}


async def create_collection_with_schema(
    database: AsyncIOMotorDatabase,
    collection_name: str,
    schema: Dict[str, Any]
) -> bool:
    """
    Crée une collection avec validation de schéma
    
    Args:
        database: Base de données MongoDB
        collection_name: Nom de la collection
        schema: Schéma de validation JSON
        
    Returns:
        True si création réussie
    """
    try:
        # Vérifier si la collection existe déjà
        collections = await database.list_collection_names()
        
        if collection_name in collections:
            print(f"⚠️ Collection '{collection_name}' existe déjà")
            return True
        
        # Créer la collection avec validation
        await database.create_collection(
            collection_name,
            validator={"$jsonSchema": schema}
        )
        
        print(f"✅ Collection '{collection_name}' créée avec validation")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création collection '{collection_name}': {e}")
        return False


async def setup_all_collections(database: AsyncIOMotorDatabase) -> bool:
    """
    Configure toutes les collections avec leurs schémas
    
    Args:
        database: Base de données MongoDB
        
    Returns:
        True si tout est configuré correctement
    """
    collections_config = [
        ("offres", OFFRE_SCHEMA),
        ("competences", COMPETENCE_SCHEMA),
        ("stats_competences", STATS_SCHEMA),
    ]
    
    success = True
    for collection_name, schema in collections_config:
        if not await create_collection_with_schema(database, collection_name, schema):
            success = False
    
    return success


def get_collection_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Retourne tous les schémas disponibles
    
    Returns:
        Dictionnaire des schémas par nom de collection
    """
    return {
        "offres": OFFRE_SCHEMA,
        "competences": COMPETENCE_SCHEMA,
        "stats_competences": STATS_SCHEMA,
    }


def validate_document(document: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Valide un document contre un schéma (validation basique)
    
    Args:
        document: Document à valider
        schema: Schéma de validation
        
    Returns:
        True si document valide (validation simplifiée)
    """
    try:
        required_fields = schema.get("required", [])
        
        # Vérifier les champs requis
        for field in required_fields:
            if field not in document:
                print(f"❌ Champ requis manquant: {field}")
                return False
        
        print("✅ Document passe la validation basique")
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False