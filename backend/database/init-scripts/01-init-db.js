// =============================================================================
// Script d'initialisation MongoDB pour DatavizFT
// Exécuté automatiquement lors du premier démarrage du conteneur
// =============================================================================

// Connexion à la base de développement
db = db.getSiblingDB('dataviz_ft_dev');

print('🚀 Initialisation de la base MongoDB DatavizFT...');

// -----------------------------------------------------------------------------
// 1. Création d'un utilisateur applicatif
// -----------------------------------------------------------------------------
print('👤 Création de l\'utilisateur applicatif...');

db.createUser({
  user: 'datavizft_app',
  pwd: 'secure_app_password',
  roles: [
    { role: 'readWrite', db: 'dataviz_ft_dev' },
    { role: 'dbAdmin', db: 'dataviz_ft_dev' }
  ]
});

print('✅ Utilisateur datavizft_app créé avec succès');

// -----------------------------------------------------------------------------
// 2. Création des collections avec validation des schémas
// -----------------------------------------------------------------------------
print('📋 Création des collections avec validation...');

// Collection offres d'emploi
db.createCollection('offres', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["source_id", "intitule", "date_creation"],
      properties: {
        source_id: { 
          bsonType: "string",
          description: "ID unique de l'offre dans le système source"
        },
        intitule: { 
          bsonType: "string", 
          maxLength: 200,
          description: "Intitulé du poste"
        },
        description: {
          bsonType: "string",
          maxLength: 10000,
          description: "Description complète de l'offre"
        },
        date_creation: { 
          bsonType: "date",
          description: "Date de création de l'offre"
        },
        date_mise_a_jour: {
          bsonType: "date",
          description: "Date de dernière mise à jour"
        },
        competences_extraites: {
          bsonType: "array",
          items: { bsonType: "string" },
          description: "Compétences extraites automatiquement"
        },
        localisation: {
          bsonType: "object",
          properties: {
            departement: { bsonType: "string" },
            region: { bsonType: "string" },
            ville: { bsonType: "string" },
            code_postal: { bsonType: "string" }
          }
        },
        entreprise: {
          bsonType: "object", 
          properties: {
            nom: { bsonType: "string" },
            secteur: { bsonType: "string" },
            taille: { bsonType: "string" }
          }
        },
        contrat: {
          bsonType: "object",
          properties: {
            type: { bsonType: "string" },
            duree: { bsonType: "string" },
            salaire: { bsonType: "string" }
          }
        }
      }
    }
  }
});

print('✅ Collection offres créée');

// Collection compétences normalisées
db.createCollection('competences', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nom", "nom_normalise", "categorie"],
      properties: {
        nom: { 
          bsonType: "string", 
          maxLength: 100,
          description: "Nom original de la compétence"
        },
        nom_normalise: { 
          bsonType: "string", 
          maxLength: 100,
          description: "Nom normalisé (lowercase, sans accents)"
        },
        categorie: { 
          bsonType: "string",
          enum: ["technique", "transversale", "metier", "outil", "langage", "framework", "autre"],
          description: "Catégorie de la compétence"
        },
        synonymes: {
          bsonType: "array",
          items: { bsonType: "string" },
          description: "Synonymes et variantes"
        },
        description: {
          bsonType: "string",
          maxLength: 500,
          description: "Description de la compétence"
        },
        niveau_demande: {
          bsonType: "string",
          enum: ["debutant", "confirme", "expert", "souhaitable", "obligatoire"],
          description: "Niveau généralement demandé"
        },
        frequence_detection: {
          bsonType: "int",
          minimum: 0,
          description: "Nombre de fois détectée"
        },
        derniere_detection: {
          bsonType: "date",
          description: "Dernière fois détectée dans une offre"
        }
      }
    }
  }
});

print('✅ Collection competences créée');

// Collection détections de compétences (logs)
db.createCollection('competences_detections', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["offre_id", "competence", "methode_detection", "date_detection"],
      properties: {
        offre_id: { 
          bsonType: "string",
          description: "ID de l'offre source"
        },
        competence: {
          bsonType: "string",
          description: "Compétence détectée"
        },
        methode_detection: {
          bsonType: "string",
          enum: ["regex", "nlp", "dictionnaire", "ia", "manuel"],
          description: "Méthode utilisée pour la détection"
        },
        confiance: {
          bsonType: "double",
          minimum: 0,
          maximum: 1,
          description: "Score de confiance (0-1)"
        },
        contexte: {
          bsonType: "string",
          maxLength: 500,
          description: "Contexte textuel de la détection"
        },
        date_detection: {
          bsonType: "date",
          description: "Date de la détection"
        }
      }
    }
  }
});

print('✅ Collection competences_detections créée');

// Collection statistiques et métriques
db.createCollection('stats_competences', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["periode_analysee", "date_analyse"],
      properties: {
        periode_analysee: { 
          bsonType: "string",
          description: "Période analysée (ex: 2025-10, 2025-Q3)"
        },
        date_analyse: { 
          bsonType: "date",
          description: "Date de l'analyse"
        },
        nb_offres_analysees: {
          bsonType: "int",
          minimum: 0
        },
        top_competences: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              competence: { bsonType: "string" },
              nb_occurrences: { bsonType: "int" },
              pourcentage: { bsonType: "double" }
            }
          }
        },
        evolution_temporelle: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              periode: { bsonType: "string" },
              nb_offres: { bsonType: "int" }
            }
          }
        },
        repartition_geographique: {
          bsonType: "object"
        }
      }
    }
  }
});

print('✅ Collection stats_competences créée');

// -----------------------------------------------------------------------------
// 3. Création des index pour les performances
// -----------------------------------------------------------------------------
print('🔍 Création des index pour optimiser les performances...');

// Index pour la collection offres
db.offres.createIndex({ "source_id": 1 }, { unique: true });
db.offres.createIndex({ "date_creation": -1 });
db.offres.createIndex({ "competences_extraites": 1 });
db.offres.createIndex({ "localisation.departement": 1, "date_creation": -1 });
db.offres.createIndex({ "localisation.region": 1, "date_creation": -1 });
db.offres.createIndex({ "entreprise.nom": 1 });
db.offres.createIndex({ "contrat.type": 1 });

// Index texte pour recherche full-text
db.offres.createIndex({ 
  "intitule": "text", 
  "description": "text",
  "entreprise.nom": "text"
}, {
  weights: {
    "intitule": 10,
    "description": 5, 
    "entreprise.nom": 3
  },
  name: "offres_text_search"
});

print('✅ Index offres créés');

// Index pour la collection compétences
db.competences.createIndex({ "nom_normalise": 1 }, { unique: true });
db.competences.createIndex({ "categorie": 1 });
db.competences.createIndex({ "frequence_detection": -1 });
db.competences.createIndex({ "derniere_detection": -1 });

// Index texte pour recherche de compétences
db.competences.createIndex({ 
  "nom": "text", 
  "synonymes": "text",
  "description": "text"
}, { name: "competences_text_search" });

print('✅ Index compétences créés');

// Index pour les détections
db.competences_detections.createIndex({ "offre_id": 1, "competence": 1 });
db.competences_detections.createIndex({ "date_detection": -1 });
db.competences_detections.createIndex({ "methode_detection": 1 });
db.competences_detections.createIndex({ "confiance": -1 });

print('✅ Index détections créés');

// Index pour les statistiques
db.stats_competences.createIndex({ "periode_analysee": 1 }, { unique: true });
db.stats_competences.createIndex({ "date_analyse": -1 });

print('✅ Index statistiques créés');

// -----------------------------------------------------------------------------
// 4. Insertion de données de référence
// -----------------------------------------------------------------------------
print('📊 Insertion des données de référence...');

// Compétences de référence pour l'IT
const competences_reference = [
  {
    nom: "Python",
    nom_normalise: "python",
    categorie: "langage",
    synonymes: ["python3", "py"],
    description: "Langage de programmation polyvalent",
    niveau_demande: "confirme",
    frequence_detection: 0,
    derniere_detection: new Date()
  },
  {
    nom: "JavaScript",
    nom_normalise: "javascript",
    categorie: "langage", 
    synonymes: ["js", "node.js", "nodejs"],
    description: "Langage de programmation web",
    niveau_demande: "confirme",
    frequence_detection: 0,
    derniere_detection: new Date()
  },
  {
    nom: "MongoDB",
    nom_normalise: "mongodb",
    categorie: "outil",
    synonymes: ["mongo", "nosql"],
    description: "Base de données NoSQL orientée documents",
    niveau_demande: "confirme",
    frequence_detection: 0,
    derniere_detection: new Date()
  },
  {
    nom: "FastAPI",
    nom_normalise: "fastapi",
    categorie: "framework",
    synonymes: ["fast-api"],
    description: "Framework web Python moderne",
    niveau_demande: "confirme", 
    frequence_detection: 0,
    derniere_detection: new Date()
  },
  {
    nom: "Docker",
    nom_normalise: "docker",
    categorie: "outil",
    synonymes: ["containerization", "conteneurisation"],
    description: "Plateforme de conteneurisation",
    niveau_demande: "souhaitable",
    frequence_detection: 0,
    derniere_detection: new Date()
  }
];

db.competences.insertMany(competences_reference);
print(`✅ ${competences_reference.length} compétences de référence insérées`);

// -----------------------------------------------------------------------------
// 5. Configuration finale
// -----------------------------------------------------------------------------
print('⚙️  Configuration finale...');

// Statistiques initiales
const stats_initiales = {
  periode_analysee: "2025-10-init",
  date_analyse: new Date(),
  nb_offres_analysees: 0,
  top_competences: [],
  evolution_temporelle: [],
  repartition_geographique: {}
};

db.stats_competences.insertOne(stats_initiales);
print('✅ Statistiques initiales créées');

// -----------------------------------------------------------------------------
// 6. Vérification finale
// -----------------------------------------------------------------------------
print('🔍 Vérification de l\'initialisation...');

const nb_collections = db.runCommand("listCollections").cursor.firstBatch.length;
const nb_competences = db.competences.countDocuments();
const nb_index = db.offres.getIndexes().length;

print(`📊 Résumé de l'initialisation:`);
print(`   - Collections créées: ${nb_collections}`);
print(`   - Compétences de référence: ${nb_competences}`);
print(`   - Index créés (offres): ${nb_index}`);

print('');
print('🎉 Initialisation MongoDB DatavizFT terminée avec succès!');
print('');
print('📋 Collections disponibles:');
print('   - offres: Stockage des offres d\'emploi');
print('   - competences: Référentiel des compétences');
print('   - competences_detections: Logs des détections');
print('   - stats_competences: Statistiques et métriques');
print('');
print('🔐 Utilisateurs créés:');
print('   - admin: Administrateur MongoDB');
print('   - datavizft_app: Utilisateur applicatif (lecture/écriture)');
print('');
print('🌐 Accès Mongo Express: http://localhost:8081');
print('   - Identifiants: datavizft / admin123');
print('');