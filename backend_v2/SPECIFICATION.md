# Spécification Technique - Architecture Hexagonale DatavizFT

## 🎯 Vue d'Ensemble

Cette spécification détaille le contenu concret de l'architecture hexagonale pour le projet DatavizFT, démontrant une maîtrise des patterns avancés du développement logiciel.

---

## 🏛️ Domain Layer (Couche Domaine)

### `domain/entities/` - Entités Métier Riches

#### `job.py` - Entité Offre d'Emploi
**Données encapsulées :**
- Identifiants : ID, source_id
- Informations : titre, description, entreprise
- Conditions : salaire, type contrat, localisation
- Analyse : compétences extraites, score qualité

**Logique métier intégrée :**
- `is_remote_possible()` → Détecte possibilité télétravail
- `has_competitive_salary()` → Vérifie salaire > 40k€
- `get_age_days()` → Calcule ancienneté offre
- `add_competence(name)` → Ajoute compétence avec validation
- `validate()` → Applique règles métier (titre requis, salaire cohérent)
- `get_location_full()` → Formatage localisation complète

#### `competence.py` - Entité Compétence Professionnelle
**Données encapsulées :**
- Identité : nom, nom normalisé, catégorie
- Relations : synonymes, tags descriptifs
- Métriques : popularité, difficulté, nombre détections

**Logique métier intégrée :**
- `normalize_name(text)` → "React.js" devient "reactjs"
- `matches_name(input)` → Vérification avec synonymes
- `is_popular(threshold=0.7)` → Évaluation popularité
- `increment_detection()` → Mise à jour compteurs
- `get_difficulty_text()` → Traduction niveau français

#### `statistics.py` - Entité Statistiques & Métriques
**Données encapsulées :**
- Temporel : période, date analyse, nombre offres
- Compétences : top compétences, tendances émergentes
- Géographique : répartition départements
- Salaires : moyennes, médianes, évolutions

**Logique métier intégrée :**
- `get_top_competences(limit=10)` → Classement par demande
- `calculate_growth_rate()` → Croissance vs période précédente
- `get_salary_percentiles()` → Distribution salariale
- `get_emerging_competences()` → Compétences en forte croissance

### `domain/repositories/` - Interfaces Repository (Contrats)

#### `job_repository.py` - Contrat Accès Offres
**Opérations de base :**
```
save(job: Job) → Job
find_by_id(id: UUID) → Optional[Job]
find_by_source_id(source_id: str) → Optional[Job]
delete(id: UUID) → bool
```

**Requêtes métier :**
```
find_by_competence(competence: str) → List[Job]
find_recent(days: int = 30) → List[Job]
find_unprocessed() → List[Job]
count_by_department(dept_code: str) → int
```

**Analyses et statistiques :**
```
get_salary_statistics() → dict
get_competence_frequencies() → dict[str, int]
get_location_distribution() → dict[str, int]
```

#### `competence_repository.py` - Contrat Accès Compétences
**Gestion compétences :**
```
find_by_name(name: str) → Optional[Competence]
find_popular(min_score: float) → List[Competence]
search_by_text(query: str) → List[Competence]
update_popularity_scores(scores: dict) → int
```

---

## 🔄 Application Layer (Couche Application)

### `application/use_cases/` - Cas d'Usage Métier

#### `collect_jobs.py` - Collecte d'Offres France Travail
**Orchestration complète :**
1. **Authentification** API France Travail (OAuth2)
2. **Récupération** offres avec pagination automatique
3. **Transformation** données API → entités Job
4. **Déduplication** via vérification source_id existants
5. **Validation** règles métier avant sauvegarde
6. **Persistance** nouvelles offres uniquement
7. **Reporting** statistiques collecte (nouvelles/doublons/erreurs)

**Paramètres configurables :**
- Limite nombre offres (défaut: illimité)
- Filtrage par département
- Force refresh (ignore cache)

#### `analyze_competences.py` - Analyse et Extraction
**Traitement intelligent :**
1. **Sélection** offres non traitées (processed=false)
2. **Extraction** compétences via algorithmes NLP
3. **Normalisation** noms (casse, espaces, synonymes)
4. **Enrichissement** entités Job avec compétences trouvées
5. **Mise à jour** métriques compétences (compteurs, popularité)
6. **Marquage** offres comme traitées (processed=true)

**Algorithmes supportés :**
- Matching mots-clés avancé
- Analyse contextuelle descriptions
- Détection compétences requises vs souhaitées

#### `generate_dataviz.py` - Génération Données Visualisation
**Préparation données Chart.js :**
1. **Agrégation** top 20 compétences avec pourcentages
2. **Calcul** répartition géographique (départements)
3. **Analyse** évolution salaires (tendances temporelles)
4. **Formatage** JSON optimisé pour frontend
5. **Cache** résultats pour performance

**Formats de sortie :**
- Histogrammes compétences (Chart.js)
- Cartes géographiques (coordonnées départements)
- Graphiques temporels salaires

### `application/services/` - Services Application

#### `dataviz_service.py` - Coordination DataViz
**Orchestration multi-use cases :**
- Coordination collecte + analyse + génération
- Gestion cache intelligent (TTL configurables)
- Mise à jour périodique automatique
- Génération rapports complets

---

## 🔧 Infrastructure Layer (Couche Infrastructure)

### `infrastructure/database/` - Implémentations MongoDB

#### `mongo_job_repository.py` - Repository Offres Concret
**Mappings entité ↔ document :**
```javascript
// Document MongoDB
{
  _id: ObjectId,
  source_id: "2679761",
  title: "Développeur Full Stack",
  competences_extraites: ["javascript", "react", "nodejs"],
  salary_min: 45000,
  location_department: "75",
  processed: true
}
```

**Requêtes optimisées :**
- Index sur source_id (unicité)
- Index sur competences_extraites (recherche)
- Index sur date_creation (tri chronologique)
- Agrégations MongoDB pour statistiques

#### `mongo_competence_repository.py` - Repository Compétences
**Fonctionnalités avancées :**
- Recherche textuelle avec scoring
- Index sur nom normalisé
- Agrégations popularité temps réel
- Gestion synonymes via tableaux

### `infrastructure/external_apis/` - Clients APIs Externes

#### `france_travail_client.py` - Client API France Travail
**Gestion complète API :**
- **Authentification** OAuth2 avec refresh automatique
- **Rate limiting** respect limites API (200 req/min)
- **Pagination** automatique pour gros volumes
- **Retry logic** avec backoff exponentiel
- **Transformation** réponses JSON → entités métier

**Endpoints utilisés :**
```
GET /offresdemploi/search → Recherche offres
GET /offresdemploi/{id} → Détail offre
GET /referentiel/metiers → Codes ROME
```

### `infrastructure/config/` - Configuration Système

#### `settings.py` - Configuration Centralisée
**Variables environnement :**
- MongoDB : URL, database, paramètres connexion
- France Travail : client_id, client_secret, endpoints
- Application : debug, logging, cache TTL
- Performance : pool sizes, timeouts

---

## 🌐 Interface Layer (Couche Interface)

### `interface/api/` - API REST FastAPI

#### Endpoints DataViz (Priorité 1)
```http
GET /api/v1/dataviz/competences
→ JSON pour graphique compétences Chart.js

GET /api/v1/dataviz/salaries?period=monthly
→ Évolution salaires sur N mois

GET /api/v1/dataviz/geographic
→ Répartition départements avec coordonnées

GET /api/v1/dataviz/trends?competence=javascript
→ Tendance compétence spécifique
```

#### Endpoints Gestion
```http
POST /api/v1/jobs/collect
→ Lance collecte asynchrone

GET /api/v1/jobs?competence=react&limit=50
→ Liste offres filtrées

GET /api/v1/competences/search?q=front
→ Recherche compétences

POST /api/v1/analysis/run
→ Lance analyse compétences
```

### `interface/cli/` - Interface Ligne de Commande

#### Commandes Opérationnelles
```bash
# Collecte
python -m backend_v2 collect --max-jobs 100 --department 75

# Analyse
python -m backend_v2 analyze --force --batch-size 50

# Statistiques  
python -m backend_v2 stats --period monthly --export json

# Maintenance
python -m backend_v2 cleanup --older-than 365
python -m backend_v2 migrate --version 2.1
```

---

## 🛠️ Shared (Utilitaires Partagés)

### `shared/exceptions.py` - Gestion Erreurs Métier
**Hiérarchie d'exceptions :**
```python
DatavizFTException
├── DomainException
│   ├── JobValidationError
│   ├── CompetenceNotFoundError
│   └── InvalidStatisticsError
├── ApplicationException
│   ├── CollectionFailedError
│   └── AnalysisTimeoutError
└── InfrastructureException
    ├── DatabaseConnectionError
    └── APIRateLimitError
```

### `shared/logging.py` - Logging Structuré
**Configuration logging :**
- Format JSON pour monitoring
- Niveaux : DEBUG, INFO, WARN, ERROR, CRITICAL
- Rotation automatique fichiers
- Corrélation IDs pour traçabilité

---

## 🧪 Tests (Structure par Couche)

### Tests Unitaires (`tests/unit/`)
```
domain/
├── test_job_entity.py       # Tests logique métier Job
├── test_competence_entity.py # Tests normalisation Competence  
└── test_statistics_entity.py # Tests calculs Statistics

application/
├── test_collect_use_case.py  # Tests orchestration collecte
└── test_analyze_use_case.py  # Tests analyse avec mocks

infrastructure/
├── test_mongo_repository.py  # Tests avec DB test
└── test_api_client.py        # Tests avec API mock
```

### Tests Intégration (`tests/integration/`)
```
database/
└── test_full_pipeline.py     # Tests bout-en-bout DB

api/
└── test_endpoints.py         # Tests API avec vraie DB
```

### Tests E2E (`tests/e2e/`)
```
scenarios/
├── test_complete_flow.py     # Collecte → Analyse → DataViz
└── test_api_dataviz.py       # Tests interface utilisateur
```

---

## 🎯 Bénéfices Business Concrets

### Pour DataViz Actuel
1. **API `/dataviz/competences`** → JSON prêt Chart.js (résout problème actuel)
2. **Collecte fiable** → Plus de plantages, gestion erreurs
3. **Performance** → Cache intelligent, requêtes optimisées
4. **Évolutivité** → Nouvelles sources données facilement

### Pour Portfolio Professionnel
1. **Architecture moderne** → Démontre vision technique senior
2. **Code quality** → Tests, documentation, patterns
3. **Scalabilité** → Prêt pour millions d'offres
4. **Maintenabilité** → Modifications localisées, refactoring sécurisé

---

## 📋 Roadmap Implémentation

### Phase 1 : Domain (Semaine 1)
- [ ] Entités Job, Competence, Statistics
- [ ] Interfaces Repository
- [ ] Tests unitaires domain

### Phase 2 : Application (Semaine 2)  
- [ ] Use cases collecte et analyse
- [ ] Use case génération DataViz
- [ ] Tests avec mocks

### Phase 3 : Infrastructure (Semaine 3)
- [ ] Repositories MongoDB
- [ ] Client France Travail
- [ ] Tests intégration

### Phase 4 : Interface (Semaine 4)
- [ ] API FastAPI
- [ ] Endpoints DataViz
- [ ] Tests E2E

---

*Cette architecture transforme le script DataViz actuel en système professionnel évolutif, démontrant une maîtrise complète des bonnes pratiques du développement logiciel moderne.*

📋 Planning Concret pour DatavizFT
Semaine 1 : Foundation + Domain
Jour 1 : shared/ (exceptions, utils, types)
Jour 2 : domain/value_objects.py + domain/events.py
Jour 3 : domain/entities/job.py avec tests
Jour 4 : domain/entities/competence.py avec tests
Jour 5 : domain/repositories/ (interfaces)
Semaine 2 : Application Layer
Jour 1 : application/use_cases/collect_jobs.py
Jour 2 : application/use_cases/analyze_competences.py
Jour 3 : application/use_cases/generate_dataviz.py
Jour 4 : application/services/dataviz_service.py
Jour 5 : Tests application avec mocks
Semaine 3 : Infrastructure
Jour 1 : infrastructure/config/settings.py
Jour 2 : infrastructure/database/mongo_job_repository.py
Jour 3 : infrastructure/database/mongo_competence_repository.py
Jour 4 : infrastructure/external_apis/france_travail_client.py
Jour 5 : Tests intégration
Semaine 4 : Interface + Polish
Jour 1 : interface/dependencies.py (DI)
Jour 2 : interface/api/routes/dataviz.py (endpoint principal)
Jour 3 : interface/api/routes/jobs.py
Jour 4 : interface/cli/commands.py
Jour 5 : Tests E2E + documentation