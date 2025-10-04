# 📚 Guide des Paramètres API France Travail

## 🔗 **Ressources officielles**

1. **Documentation principale** : https://francetravail.io/data/documentation
2. **API Offres d'emploi** : https://francetravail.io/data/api/offres-emploi
3. **Interface Swagger** : https://api.francetravail.io/partenaire/offresdemploi/v2/ui/
4. **Portail développeur** : https://francetravail.io/data

## 🎯 **URL de l'API**
```
https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
```

## 📋 **Paramètres principaux disponibles**

### **🌍 Localisation**
- `lieuTravail` : Nom de la ville (ex: "Nancy", "Paris") - ✅ RECOMMANDÉ pour plus de résultats
- `distance` : Rayon en km (ex: 10, 20, 50)
- `departement` : Code département (ex: "54", "75") 
- `region` : Code région (ex: "44" pour Grand Est)
- `commune` : Code INSEE de la commune - ⚠️ Très restrictif (commune exacte uniquement)

### **💼 Métier et secteur**
- `codeROME` : Code métier ROME (ex: "M1805", "M1810")
- `domaine` : Domaine professionnel (ex: "M" pour informatique)
- `secteurActivite` : Code NAF du secteur (ex: "01", "10")
- `appellationLibelle` : Intitulé exact du poste

### **📝 Contrat**
- `typeContrat` : 
  - `CDI` : Contrat à durée indéterminée
  - `CDD` : Contrat à durée déterminée  
  - `MIS` : Mission intérimaire
  - `SAI` : Contrat saisonnier
  - `INT` : Contrat d'apprentissage/professionnalisation
- `natureContrat` : 
  - `E1` : Libéral
  - `E2` : Franchise
  - `NS` : Non spécifié
- `dureeHebdo` : Durée hebdomadaire (ex: 35, 39)

### **🎓 Qualification et expérience**
- `experienceExige` :
  - `D` : Débutant accepté
  - `S` : Expérience souhaitée
  - `E` : Expérience exigée
- `qualificationCode` : 
  - `1` : Manoeuvre
  - `2` : Ouvrier spécialisé
  - `3` : Ouvrier qualifié
  - `4` : Employé non qualifié
  - `5` : Employé qualifié
  - `6` : Technicien, agent de maîtrise
  - `7` : Cadre

### **⏰ Dates et temps**
- `minDateCreation` : Date min de création (format ISO: "2024-10-01T00:00:00Z")
- `maxDateCreation` : Date max de création
- `minDateModification` : Date min de modification
- `maxDateModification` : Date max de modification

### **🔄 Tri et pagination**
- `sort` : Type de tri
  - `0` : Par pertinence (défaut)
  - `1` : Par date de création
  - `2` : Par date de modification
- `range` : Pagination (ex: "0-19", "20-39", "0-149")

### **🏷️ Filtres spéciaux**
- `alternance` : true/false pour alternance uniquement
- `accessibleTH` : true pour postes accessibles aux travailleurs handicapés
- `entrepriseAdaptee` : true pour entreprises adaptées
- `offresManqueCandidats` : true pour offres en tension
- `origineOffre` : Source de l'offre (1=Pôle emploi, 2=Partenaires)

## 📊 **Champs de réponse principaux**
Chaque offre retournée contient :
- `id` : Identifiant unique
- `intitule` : Titre du poste
- `description` : Description complète
- `lieuTravail` : Localisation détaillée
- `entreprise` : Informations entreprise
- `typeContrat` : Type de contrat
- `salaire` : Informations salariales
- `competences` : Compétences requises
- `qualitesProfessionnelles` : Qualités recherchées

## 🔧 **Exemples d'utilisation**

### Recherche basique
```
GET /offres/search?codeROME=M1805&range=0-19
```

### Recherche géographique
```
GET /offres/search?lieuTravail=Nancy&distance=20&range=0-19
```

### Recherche par contrat
```
GET /offres/search?typeContrat=CDI&experienceExige=D&range=0-19
```

### Recherche complexe
```
GET /offres/search?codeROME=M1805&lieuTravail=Nancy&typeContrat=CDI&experienceExige=D&qualificationCode=5&range=0-19
```

## ⚠️ **Notes importantes**

1. **Authentification** : Bearer token obligatoire
2. **Pagination** : Maximum 150 résultats par requête
3. **Status 206** : Réponse normale pour contenu partiel
4. **Rate limiting** : Respecter les limites de l'API
5. **Encodage** : URL-encoder les paramètres spéciaux

## 🛠️ **Tests dans votre code**

Utilisez le script `explore_api_params.py` pour tester différentes combinaisons de paramètres.