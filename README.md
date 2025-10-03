# Dataviz FT — Visualisation des offres développeur en France

**Dataviz FT** est une plateforme web open source permettant de visualiser les offres d’emploi développeur en France à travers des cartes interactives et des indicateurs temporels dynamiques. Elle s’appuie sur une consommation quotidienne de l’API FranceTravail, une base PostgreSQL/PostGIS, et une interface React moderne.

---

## Objectifs

- Visualiser et localiser les offres sur Nancy, stack, entreprise, salaire, expérience... et période de visibilité de l'offre
- Suivre l’évolution temporelle des offres et des technologies demandées
- Identifier les tendances géographiques et techniques du marché

---

## Architecture

| Composant     | Stack principale                          |
|---------------|--------------------------------------------|
| Backend       | Python, FastAPI, PostgreSQL + PostGIS, APScheduler |
| Frontend      | React + kepler.gl ou Recharts ou plotly.js      |
| DevOps        | Docker, GitHub Actions, CI/CD              |
| Test          | Jest, pytest, mypy, ruff/flake8, GitHub Actions, CI/CD  (à definir)             |

![Architecture DatavizFT](docs/archi.drawio.svg)

---

## Fonctionnalités

- Cartes choroplèthes interactives avec filtres temporels
- Indicateurs dynamiques (à définir)
- API REST
- CI/CD
- Tests unitaires et d’intégration (backend et frontend)
- Sécurité : validation des entrées, protection SQL, monitoring

---

## Planification des sprints

| Sprint | Objectifs clés | Livrables attendus |
|----------|----------------|---------------------|
| **Sprint 1** | Définition du périmètre, architecture technique, setup du mono-repo, accès à l’API France Travail | Cahier des charges, arborescence initiale, accès API fonctionnel |
| **Sprint 2** | Collecte exploratoire via API, enrichissement des données | Module de collecte, détection des stacks, géolocalisation, validation des champs |
| **Sprint 3** | Modélisation et stockage | Schéma SQL, base PostgreSQL/PostGIS opérationnelle, tests d’insertion |
| **Sprint 4** | Interface et visualisation | Squelette React, comparaison des librairies dataviz, premiers composants fonctionnels |
| **Sprint 5** | DevOps et automatisation | Docker Compose, CI/CD GitHub Actions, gestion des environnements, .env standardisé |
| **Sprint 6** | Tests et qualité | Couverture backend/frontend, tests E2E, monitoring, alerting automatisé |

---

### Intégration des tests

- **Sprint 1** : Configuration des outils (`pytest`, `Jest`, `MSW`, `httpx`)
- **Sprint 2–3** : Tests unitaires backend (collecte, enrichissement, modèles)
- **Sprint 4** : Tests React (composants, hooks, appels API mockés)
- **Sprint 5–6** : Tests d’intégration et end-to-end (Playwright ou Cypress)

---

## Licence

A définir
