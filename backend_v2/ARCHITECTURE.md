# Backend v2 - Architecture Hexagonale

## 🎯 Objectif

Démonstration d'une architecture hexagonale professionnelle pour le projet DatavizFT.

## 🏗️ Structure

```
backend_v2/
├── domain/                    # 🏛️ Cœur métier (logique pure)
│   ├── entities/             # Entités avec règles business
│   ├── repositories/         # Interfaces d'accès aux données
│   └── services/             # Services domaine
│
├── application/              # 🔄 Orchestration (Use Cases)
│   ├── use_cases/           # Cas d'usage métier
│   └── services/            # Services application
│
├── infrastructure/          # 🔧 Détails techniques
│   ├── database/           # Implémentations MongoDB
│   ├── external_apis/      # Clients API externes
│   └── config/            # Configuration
│
├── interface/              # 🌐 Points d'entrée
│   ├── api/               # REST API FastAPI
│   └── cli/               # Interface ligne de commande
│
├── shared/                # 🛠️ Utilitaires partagés
└── tests/                # 🧪 Tests par couche
```

## 🎓 Concepts Démontrés

- **Architecture Hexagonale** (Ports & Adapters)
- **Domain-Driven Design** (DDD)
- **Principes SOLID**
- **Dependency Injection**
- **Repository Pattern**
- **Use Case Pattern**

## 🚀 Prochaines Étapes

1. ✅ Structure créée
2. 🔄 Entités métier (en cours)
3. ⏳ Use Cases
4. ⏳ Infrastructure MongoDB
5. ⏳ API FastAPI
6. ⏳ Tests

## 📚 Documentation

La documentation détaillée de chaque couche se trouve dans les fichiers `__init__.py` de chaque module.