# DatavizFT

> Plateforme d'analyse et de visualisation des tendances du marché de l'emploi IT en France

DatavizFT collecte automatiquement les offres d'emploi depuis plusieurs sources (France Travail, Adzuna), extrait les compétences demandées, et visualise leur évolution dans le temps via un dashboard interactif.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Endpoints](#api-endpoints)
- [Structure du projet](#structure-du-projet)
- [Développement](#développement)
- [Tests](#tests)
- [Licence](#licence)

## Fonctionnalités

- **Collecte multi-sources** : France Travail API (codes ROME M1805, M1802, M1810) et Adzuna
- **Extraction automatique des compétences** : Analyse NLP avec référentiel de 250+ technologies
- **Déduplication intelligente** : Détection des doublons par source_id
- **Visualisation interactive** : Dashboard React avec graphiques ECharts
- **Filtrage avancé** : Par source, ville, période
- **Scheduler automatique** : Collecte périodique des nouvelles offres
- **API REST** : Endpoints FastAPI pour intégration externe

## Architecture

Le projet suit une **architecture hexagonale** (Ports & Adapters) avec séparation claire des responsabilités :

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERFACE LAYER                              │
│  ┌──────────────┐    ┌──────────────┐                               │
│  │  FastAPI     │    │  React       │                               │
│  │  REST API    │    │  Dashboard   │                               │
│  └──────┬───────┘    └──────┬───────┘                               │
└─────────┼───────────────────┼───────────────────────────────────────┘
          │                   │
┌─────────┼───────────────────┼───────────────────────────────────────┐
│         │     APPLICATION LAYER                                      │
│  ┌──────▼───────────────────▼──────┐                                │
│  │    CollectionService            │                                │
│  │    (Orchestration)              │                                │
│  └──────┬──────────────────────────┘                                │
└─────────┼───────────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────────┐
│         │         DOMAIN LAYER                                       │
│  ┌──────▼──────┐  ┌─────────────────┐  ┌────────────────┐           │
│  │  Job Entity │  │ CompetenceAnalyzer │  │ DeduplicationService │    │
│  └─────────────┘  └─────────────────┘  └────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────────┐
│         │      INFRASTRUCTURE LAYER                                  │
│  ┌──────▼──────┐  ┌─────────────────┐  ┌────────────────┐           │
│  │  MongoDB    │  │ France Travail   │  │  Adzuna API    │           │
│  │  Repository │  │ API Client       │  │  Client        │           │
│  └─────────────┘  └─────────────────┘  └────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

## Prérequis

- **Python** 3.11+
- **Node.js** 18+
- **Docker** & Docker Compose
- **MongoDB** 7.0 (via Docker)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-org/datavizft.git
cd datavizft
```

### 2. Démarrer MongoDB

```bash
docker-compose up -d mongodb mongo-express
```

MongoDB sera accessible sur `localhost:27017`, Mongo Express sur `localhost:8081`.

### 3. Installer le backend

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Installer le frontend

```bash
cd frontend
npm install
```

### 5. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos credentials API
```

## Configuration

### Variables d'environnement principales

| Variable | Description | Défaut |
|----------|-------------|--------|
| `FRANCETRAVAIL_CLIENT_ID` | Client ID France Travail API | - |
| `FRANCETRAVAIL_CLIENT_SECRET` | Client Secret France Travail API | - |
| `ADZUNA_APP_ID` | App ID Adzuna API | - |
| `ADZUNA_CLIENT_SECRET` | Client Secret Adzuna API | - |
| `MONGODB_URL` | URL de connexion MongoDB | `mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin` |
| `APP_ENV` | Environnement (`development`/`production`) | `development` |

### Obtenir les credentials API

1. **France Travail** : [Portail Emploi Store Dev](https://francetravail.io/data/api)
2. **Adzuna** : [Adzuna API](https://developer.adzuna.com/)

## Utilisation

### Démarrer le backend

```bash
# Depuis la racine du projet
python -m uvicorn backend_v2.interface.api.main:app --reload --port 8000
```

L'API sera disponible sur `http://localhost:8000`. Documentation Swagger : `http://localhost:8000/docs`.

### Démarrer le frontend

```bash
cd frontend
npm run dev
```

Le dashboard sera accessible sur `http://localhost:5173`.

### Lancer une collecte manuelle

```bash
# Via l'API (POST)
curl -X POST http://localhost:8000/api/collection/collect
```

## API Endpoints

### Skills (Compétences)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/skills/evolution` | Évolution des compétences dans le temps |

Paramètres : `source`, `city`, `start_date`, `end_date`, `top_n`

### Filtres

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/filters/cities` | Top villes par nombre d'offres |
| `GET` | `/api/filters/sources` | Sources de données disponibles |

### Collection

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/collection/collect` | Déclencher une collecte |
| `GET` | `/api/collection/status` | Statut de la collecte |

### Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/stats/latest` | Dernières statistiques générées |

## Structure du projet

```
datavizft/
├── backend_v2/                  # Backend (Architecture Hexagonale)
│   ├── domain/                  # Logique métier pure
│   │   ├── entities/           # Entités (Job)
│   │   ├── repositories/       # Interfaces (Ports)
│   │   └── services/           # Services domaine
│   ├── application/            # Orchestration (Use Cases)
│   │   └── services/          # CollectionService
│   ├── infrastructure/         # Implémentations techniques
│   │   ├── database/          # MongoDB
│   │   ├── clients/           # APIs externes
│   │   └── repositories/      # Implémentations MongoDB
│   ├── interface/             # Points d'entrée
│   │   └── api/               # FastAPI
│   ├── data/                  # Référentiels (competences.json)
│   └── tests/                 # Tests unitaires
│
├── frontend/                   # Dashboard React
│   ├── src/
│   │   ├── components/        # Composants React
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # Client API
│   │   └── types/             # Types TypeScript
│   └── package.json
│
├── docker-compose.yml          # Services Docker
├── pyproject.toml             # Configuration Python
└── requirements.txt           # Dépendances Python
```

## Développement

### Qualité de code

```bash
# Linting
make lint

# Formatage
make format

# Type checking
make typecheck

# Tout en un
make quality
```

### Ajouter une nouvelle source de données

1. Créer un client API dans `backend_v2/infrastructure/clients/`
2. Implémenter la méthode de collecte dans `CollectionService`
3. Ajouter la conversion vers le format `Job`

### Ajouter de nouvelles compétences

Éditer `backend_v2/data/competences.json` pour ajouter des technologies au référentiel.

## Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=backend_v2 --cov-report=html

# Tests spécifiques
pytest backend_v2/tests/test_competence_analyzer.py -v
```

## Stack technique

### Backend
- **FastAPI** - API REST async
- **Motor/PyMongo** - Driver MongoDB async/sync
- **Pydantic** - Validation des données
- **Structlog** - Logging structuré

### Frontend
- **React 19** + TypeScript
- **Vite** - Build tool
- **TanStack Query** - Data fetching
- **ECharts** - Visualisations
- **Tailwind CSS** - Styling

### Infrastructure
- **MongoDB 7.0** - Base de données
- **Docker Compose** - Orchestration
- **GitHub Actions** - CI/CD

## Licence

MIT License - voir [LICENSE](LICENSE)
