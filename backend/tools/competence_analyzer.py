"""
Competence Analyzer - Analyse des compétences dans les offres d'emploi
Détection, comptage et statistiques des compétences
"""

from typing import Any

from .text_processor import extraire_texte_offre, rechercher_competence_dans_texte


class CompetenceAnalyzer:
    """Analyseur de compétences dans les offres d'emploi"""

    def __init__(self, competences_referentiel: dict[str, list[str]]):
        """
        Initialise l'analyseur avec le référentiel de compétences

        Args:
            competences_referentiel: Dictionnaire des compétences par catégorie
        """
        self.referentiel = competences_referentiel
        self.cache_resultats: dict[str, dict[str, Any]] = {}

    def analyser_offres(
        self, offres: list[dict[str, Any]], verbose: bool = True
    ) -> dict[str, Any]:
        """
        Analyse un ensemble d'offres pour extraire les statistiques de compétences

        Args:
            offres: Liste des offres à analyser
            verbose: Afficher les logs de progression

        Returns:
            Dictionnaire avec les résultats d'analyse par catégorie
        """
        if verbose:
            print("🔍 ANALYSE DES COMPÉTENCES")
            print("=" * 50)

        nb_offres_total = len(offres)
        resultats_par_categorie = {}

        # Analyse par catégorie
        for categorie, competences in self.referentiel.items():
            if verbose:
                print(
                    f"📊 Analyse catégorie: {categorie} ({len(competences)} compétences)"
                )

            resultats_competences = []

            for competence in competences:
                count = 0
                offres_avec_competence = []

                for i, offre in enumerate(offres):
                    texte_offre = extraire_texte_offre(offre)

                    if rechercher_competence_dans_texte(texte_offre, competence):
                        count += 1
                        offres_avec_competence.append(
                            {
                                "id": offre.get("id", f"offre_{i}"),
                                "intitule": offre.get("intitule", ""),
                                "entreprise": offre.get("entreprise", {}).get(
                                    "nom", ""
                                ),
                            }
                        )

                if count > 0:
                    pourcentage = (count / nb_offres_total) * 100
                    resultats_competences.append(
                        {
                            "competence": competence,
                            "occurrences": count,
                            "pourcentage": round(pourcentage, 1),
                            "offres": offres_avec_competence,  # TOUTES les offres, pas seulement 5
                        }
                    )

            # Tri par nombre d'occurrences décroissant
            from typing import cast

            resultats_competences.sort(
                key=lambda x: cast(int, x["occurrences"]), reverse=True
            )

            resultats_par_categorie[categorie] = {
                "competences": resultats_competences,
                "nb_competences_detectees": len(resultats_competences),
                "nb_competences_total": len(competences),
            }

            if verbose and resultats_competences:
                top_3 = resultats_competences[:3]
                for i, result in enumerate(top_3, 1):
                    print(
                        f"   {i}. {result['competence']}: {result['occurrences']} offres ({result['pourcentage']}%)"
                    )

        return {
            "resultats_par_categorie": resultats_par_categorie,
            "nb_offres_analysees": nb_offres_total,
        }

    def analyser_texte(self, texte: str) -> list[str]:
        """
        Analyse un texte pour détecter les compétences présentes

        Args:
            texte: Texte à analyser (intitulé + description d'offre)

        Returns:
            Liste des compétences détectées dans le texte
        """
        competences_detectees = []

        if not texte:
            return competences_detectees

        # Parcourir toutes les catégories et compétences du référentiel
        for _categorie, competences_liste in self.referentiel.items():
            for competence in competences_liste:
                if rechercher_competence_dans_texte(texte, competence):
                    if competence not in competences_detectees:
                        competences_detectees.append(competence)

        return competences_detectees


# Fonction utilitaire pour compatibilité
def analyser_competences_offres(
    offres: list[dict[str, Any]], competences_referentiel: dict[str, list[str]]
) -> dict[str, Any]:
    """
    Fonction utilitaire pour analyser les compétences dans les offres

    Args:
        offres: Liste des offres à analyser
        competences_referentiel: Référentiel de compétences

    Returns:
        Résultats de l'analyse
    """
    analyzer = CompetenceAnalyzer(competences_referentiel)
    return analyzer.analyser_offres(offres)
