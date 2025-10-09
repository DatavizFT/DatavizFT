# Analyse Architecture DatavizFT avec MongoDB
Date: 9 octobre 2025

## 🎯 Pourquoi MongoDB est Idéal

### Structure API France Travail = Document NoSQL
{
  "_id": "objectId",
  "intitule": "Développeur Full Stack",
  "entreprise": {
    "nom": "TechCorp",
    "secteurActivite": "Informatique"
  },
  "lieuTravail": {
    "libelle": "Paris 15e Arrondissement",
    "codePostal": "75015",
    "commune": "75115"
  },
  "competences": ["JavaScript", "React", "Node.js"],
  "salaire": { "min": 45000, "max": 55000 },
  "dateCreation": "2025-10-09T10:30:00Z"
}

### Avantages vs Relationnel
- ✅ Flexibilité : Structure offres variable (salaire optionnel, etc.)
- ✅ Performance : Requêtes géospatiales natives
- ✅ Agrégation : Pipeline MongoDB = analytics puissants
- ✅ Scalabilité : Horizontal scaling facile

## 📊 Analyses Statistiques Possibles

### 🗺️ Géographiques (Chloropleth Maps)
// Agrégation MongoDB native
db.offres.aggregate([
  {$match: {dateCreation: {$gte: new Date("2025-01-01")}}},
  {$group: {
    _id: "$lieuTravail.departement",
    nb_offres: {$sum: 1},
    competences_top: {$push: "$competences"},
    salaire_moyen: {$avg: "$salaire.min"}
  }}
])

Visualisations :
- Densité d'offres par département
- Compétences dominantes par région
- Fourchettes salariales géographiques
- Types de contrats (CDI/CDD/Freelance) par zone

### ⏱️ Temporelles (Évolution)
// Tendances temporelles
db.offres.aggregate([
  {$group: {
    _id: {
      year: {$year: "$dateCreation"},
      month: {$month: "$dateCreation"},
      competence: "$competences"
    },
    count: {$sum: 1}
  }},
  {$sort: {"_id.year": 1, "_id.month": 1}}
])

Analyses :
- Évolution mensuelle des compétences demandées
- Saisonnalité des recrutements (été vs rentrée)
- Émergence de nouvelles technologies
- Déclin de technologies obsolètes

## 🔍 Autres Données à Analyser

### 💼 Marché de l'Emploi
- Ratio offres/demandeurs par compétence
- Durée moyenne avant pourvoir un poste
- Types d'entreprises qui recrutent (startup vs grand groupe)
- Télétravail : évolution des offres remote/hybride

### 💰 Analyse Salariale
- Corrélation compétences/salaire (React vs Angular)
- Premium technologies (Rust, Go, Kotlin)
- Progression salariale junior → senior par stack
- Écarts salariaux Paris vs province

### 🎯 Profils Recherchés
- Combinaisons de compétences gagnantes
- Expérience requise par technologie
- Secteurs d'activité les plus demandeurs
- Taille d'équipe et méthodologies (Agile, DevOps)

### 🚀 Innovation & Tendances
- Vélocité d'adoption nouvelles techs (ex: IA, Web3)
- Corrélations technologiques (Docker → Kubernetes)
- Cycle de vie des frameworks
- Influence des événements (sorties React, conférences)

## 🏗️ Architecture MongoDB Recommandée

### Collections Structure
// Collection principale
offres: {
  _id: ObjectId,
  source_id: "france_travail_123456",
  intitule: "Dev Full Stack",
  competences_extraites: ["react", "nodejs", "mongodb"],
  competences_brutes: "React, Node.js, MongoDB, Git",
  localisation: {
    departement: "75",
    region: "11", // Île-de-France
    coordinates: [2.3522, 48.8566]
  },
  date_collecte: ISODate,
  date_creation_offre: ISODate,
  // ... autres champs
}

// Collection d'agrégation (cache)
stats_competences_quotidiennes: {
  _id: ObjectId,
  date: ISODate("2025-10-09"),
  competence: "react",
  departement: "75",
  nb_offres: 45,
  salaire_moyen: 52000
}

### Index pour Performance
// Géospatial
db.offres.createIndex({
  "localisation.coordinates": "2dsphere"
})

// Temporel + Compétences
db.offres.createIndex({
  "date_creation_offre": 1,
  "competences_extraites": 1
})

// Recherche textuelle
db.offres.createIndex({
  "intitule": "text",
  "description": "text"
})

## 📈 Dashboards Possibles

### 🎯 Dashboard Développeur
- Heatmap France : demande par compétence
- Timeline : évolution de "ma stack"
- Radar Chart : compétences complémentaires
- Salary Predictor : estimation basée sur profil

### 🏢 Dashboard Entreprise
- Concurrence : qui recrute sur ma stack ?
- Benchmark salarial par région
- Temps de recrutement estimé
- Compétences émergentes à anticiper

### 📊 Dashboard Marché
- Baromètre technologies (montante/descendante)
- Cartographie écosystème tech français
- Prédictions tendances (ML sur historique)
- Impact événements (COVID, sorties produits)

## 🚀 Pipeline de Données

### ETL Flow
France Travail API → Backend Pipeline → 
MongoDB Raw → Agrégation Pipeline → 
MongoDB Analytics → API REST → Frontend Viz

### Real-time Updates
Scheduler (24h) → Collecte → 
Change Streams MongoDB → 
WebSocket → Frontend Live Update

## 💡 Valeur Ajoutée Unique

### Vs Autres Solutions
- LinkedIn : Pas de données salariales précises
- Indeed : Pas d'API structurée
- Stack Overflow Survey : Annuel seulement
- Votre solution : **Temps réel + Géolocalisé + Gratuit**

### Use Cases Concrets
- Étudiant : "Quelle stack apprendre pour ma région ?"
- Dev Senior : "Quel salaire demander pour ma stack ?"
- Entreprise : "Combien coûte un dev React à Lyon ?"
- École : "Quels cours adapter aux tendances ?"

## 🎯 Recommandation

Votre approche est **excellente** ! MongoDB + géospatial + temporel = combinaison gagnante.

Next Steps :
1. Enrichir géolocalisation : API gouv pour codes INSEE → départements
2. Pipeline ML : détection automatique émergence/déclin
3. API publique : dataset ouvert pour la communauté dev
4. Alertes personnalisées : "React monte dans ta région"

C'est un projet avec un **vrai potentiel commercial** et **impact communautaire** ! 🚀