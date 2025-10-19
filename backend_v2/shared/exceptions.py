"""
Exceptions personnalisées DatavizFT Backend v2
==============================================

Système de gestion d'erreurs structuré pour l'architecture hexagonale.
Amélioration du système existant avec séparation par couches.

Hiérarchie des exceptions :
- DatavizFTException (base)
  ├── DomainException (erreurs métier)
  ├── ApplicationException (erreurs applicatives)  
  ├── InfrastructureException (erreurs techniques)
  └── InterfaceException (erreurs d'interface)

Basé sur backend/tools/error_handling.py avec améliorations pour
l'architecture hexagonale et les bonnes pratiques modernes.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCategory(str, Enum):
    """Catégories d'erreurs pour classification fine"""
    
    # Erreurs Domaine (logique métier)
    DOMAIN_VALIDATION = "domain_validation"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    ENTITY_NOT_FOUND = "entity_not_found"
    INVALID_OPERATION = "invalid_operation"
    
    # Erreurs Application (orchestration)
    USE_CASE_FAILED = "use_case_failed"
    SERVICE_UNAVAILABLE = "service_unavailable"
    WORKFLOW_ERROR = "workflow_error"
    TIMEOUT_ERROR = "timeout_error"
    
    # Erreurs Infrastructure (technique)
    DATABASE_ERROR = "database_error"
    EXTERNAL_API_ERROR = "external_api_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    
    # Erreurs Interface (points d'entrée)
    API_VALIDATION_ERROR = "api_validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    SERIALIZATION_ERROR = "serialization_error"
    
    # Erreurs Système
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(str, Enum):
    """Niveaux de sévérité avec impact business"""
    
    LOW = "low"           # Logs informatifs, pas d'impact utilisateur
    MEDIUM = "medium"     # Erreur gérable, utilisateur peut continuer
    HIGH = "high"         # Erreur bloquante, nécessite intervention
    CRITICAL = "critical" # Système compromis, alerte immédiate


class DatavizFTException(Exception):
    """
    Exception de base pour DatavizFT Backend v2
    
    Intègre toutes les informations nécessaires pour le debugging,
    le monitoring et la communication utilisateur.
    """
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        super().__init__(message)
        
        self.error_id = self._generate_error_id()
        self.category = category
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.user_message = user_message or self._get_default_user_message()
        self.correlation_id = correlation_id
        self.timestamp = datetime.utcnow()
    
    def _generate_error_id(self) -> str:
        """Génère un ID unique pour traçabilité"""
        return f"DVFT-{uuid.uuid4().hex[:8].upper()}"
    
    def _get_default_user_message(self) -> str:
        """Message utilisateur par défaut selon la catégorie"""
        user_messages = {
            ErrorCategory.DOMAIN_VALIDATION: "Les données fournies ne sont pas valides",
            ErrorCategory.BUSINESS_RULE_VIOLATION: "Cette opération n'est pas autorisée",
            ErrorCategory.ENTITY_NOT_FOUND: "L'élément demandé n'existe pas",
            ErrorCategory.USE_CASE_FAILED: "L'opération n'a pas pu être effectuée",
            ErrorCategory.DATABASE_ERROR: "Erreur de base de données temporaire",
            ErrorCategory.EXTERNAL_API_ERROR: "Service externe temporairement indisponible",
            ErrorCategory.API_VALIDATION_ERROR: "Les paramètres de la requête sont invalides",
            ErrorCategory.AUTHENTICATION_ERROR: "Authentification requise",
            ErrorCategory.AUTHORIZATION_ERROR: "Droits insuffisants",
        }
        return user_messages.get(self.category, "Une erreur technique est survenue")
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'exception pour logging/API"""
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "user_message": self.user_message,
            "details": self.details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"[{self.error_id}] {self.category.value}: {self.message}"


# =============================================================================
# EXCEPTIONS DOMAIN LAYER (Couche Domaine)
# =============================================================================

class DomainException(DatavizFTException):
    """Exception de base pour la couche domaine"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.DOMAIN_VALIDATION)
        super().__init__(message, **kwargs)


class InvalidJobDataException(DomainException):
    """Données d'offre d'emploi invalides"""
    
    def __init__(self, message: str, job_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Données offre invalides: {message}",
            category=ErrorCategory.DOMAIN_VALIDATION,
            details={"job_data": job_data},
            user_message="Les informations de l'offre d'emploi sont incorrectes"
        )


class CompetenceNotFoundException(DomainException):
    """Compétence non trouvée"""
    
    def __init__(self, competence_name: str):
        super().__init__(
            message=f"Compétence non trouvée: {competence_name}",
            category=ErrorCategory.ENTITY_NOT_FOUND,
            details={"competence_name": competence_name},
            user_message=f"La compétence '{competence_name}' n'existe pas"
        )


class CompetenceAnalysisException(DomainException):
    """Erreur lors de l'analyse des compétences"""
    
    def __init__(self, message: str, job_id: Optional[str] = None):
        super().__init__(
            message=f"Échec analyse compétences: {message}",
            category=ErrorCategory.BUSINESS_RULE_VIOLATION,
            details={"job_id": job_id},
            user_message="Erreur lors de l'analyse des compétences"
        )


class InvalidStatisticsException(DomainException):
    """Statistiques invalides ou incohérentes"""
    
    def __init__(self, message: str, stats_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Statistiques invalides: {message}",
            category=ErrorCategory.DOMAIN_VALIDATION,
            details={"stats_data": stats_data},
            user_message="Les données statistiques sont incohérentes"
        )


# =============================================================================
# EXCEPTIONS APPLICATION LAYER (Couche Application)
# =============================================================================

class ApplicationException(DatavizFTException):
    """Exception de base pour la couche application"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.USE_CASE_FAILED)
        super().__init__(message, **kwargs)


class JobCollectionException(ApplicationException):
    """Erreur lors de la collecte d'offres"""
    
    def __init__(self, message: str, source: str = "unknown"):
        super().__init__(
            message=f"Échec collecte offres ({source}): {message}",
            category=ErrorCategory.USE_CASE_FAILED,
            details={"source": source},
            user_message="La collecte d'offres d'emploi a échoué"
        )


class StatisticsCalculationException(ApplicationException):
    """Erreur lors du calcul de statistiques"""
    
    def __init__(self, message: str, stat_type: Optional[str] = None):
        super().__init__(
            message=f"Échec calcul statistiques: {message}",
            category=ErrorCategory.USE_CASE_FAILED,
            details={"stat_type": stat_type},
            user_message="Impossible de calculer les statistiques"
        )


class UseCaseTimeoutException(ApplicationException):
    """Timeout lors de l'exécution d'un use case"""
    
    def __init__(self, use_case_name: str, timeout_seconds: int):
        super().__init__(
            message=f"Timeout {use_case_name} après {timeout_seconds}s",
            category=ErrorCategory.TIMEOUT_ERROR,
            severity=ErrorSeverity.HIGH,
            details={"use_case": use_case_name, "timeout": timeout_seconds},
            user_message="L'opération a pris trop de temps"
        )


# =============================================================================
# EXCEPTIONS INFRASTRUCTURE LAYER (Couche Infrastructure)
# =============================================================================

class InfrastructureException(DatavizFTException):
    """Exception de base pour la couche infrastructure"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.DATABASE_ERROR)
        super().__init__(message, **kwargs)


class DatabaseConnectionException(InfrastructureException):
    """Erreur de connexion à la base de données"""
    
    def __init__(self, message: str, db_type: str = "MongoDB"):
        super().__init__(
            message=f"Connexion {db_type} échouée: {message}",
            category=ErrorCategory.DATABASE_ERROR,
            severity=ErrorSeverity.CRITICAL,
            details={"db_type": db_type},
            user_message="Base de données temporairement indisponible"
        )


class RepositoryException(InfrastructureException):
    """Erreur dans les opérations repository"""
    
    def __init__(self, message: str, operation: str, entity_type: str):
        super().__init__(
            message=f"Erreur repository {entity_type}.{operation}: {message}",
            category=ErrorCategory.DATABASE_ERROR,
            details={"operation": operation, "entity_type": entity_type},
            user_message="Erreur d'accès aux données"
        )


class ExternalAPIException(InfrastructureException):
    """Erreur d'API externe (France Travail, etc.)"""
    
    def __init__(self, message: str, api_name: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"API {api_name} erreur: {message}",
            category=ErrorCategory.EXTERNAL_API_ERROR,
            severity=ErrorSeverity.HIGH,
            details={"api_name": api_name, "status_code": status_code},
            user_message=f"Service {api_name} temporairement indisponible"
        )


class ConfigurationException(InfrastructureException):
    """Erreur de configuration système"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=f"Configuration invalide: {message}",
            category=ErrorCategory.CONFIGURATION_ERROR,
            severity=ErrorSeverity.CRITICAL,
            details={"config_key": config_key},
            user_message="Erreur de configuration système"
        )


# =============================================================================
# EXCEPTIONS INTERFACE LAYER (Couche Interface)
# =============================================================================

class InterfaceException(DatavizFTException):
    """Exception de base pour la couche interface"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.API_VALIDATION_ERROR)
        super().__init__(message, **kwargs)


class APIValidationException(InterfaceException):
    """Erreur de validation des paramètres API"""
    
    def __init__(self, message: str, field_name: Optional[str] = None):
        super().__init__(
            message=f"Validation API échouée: {message}",
            category=ErrorCategory.API_VALIDATION_ERROR,
            details={"field_name": field_name},
            user_message="Paramètres de requête invalides"
        )


class AuthenticationException(InterfaceException):
    """Erreur d'authentification"""
    
    def __init__(self, message: str = "Authentification requise"):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION_ERROR,
            severity=ErrorSeverity.HIGH,
            user_message="Authentification requise"
        )


class AuthorizationException(InterfaceException):
    """Erreur d'autorisation"""
    
    def __init__(self, message: str, required_permission: Optional[str] = None):
        super().__init__(
            message=f"Autorisation refusée: {message}",
            category=ErrorCategory.AUTHORIZATION_ERROR,
            severity=ErrorSeverity.HIGH,
            details={"required_permission": required_permission},
            user_message="Droits insuffisants pour cette opération"
        )


class SerializationException(InterfaceException):
    """Erreur de sérialisation/désérialisation"""
    
    def __init__(self, message: str, data_type: Optional[str] = None):
        super().__init__(
            message=f"Erreur sérialisation: {message}",
            category=ErrorCategory.SERIALIZATION_ERROR,
            details={"data_type": data_type},
            user_message="Erreur de format des données"
        )


# =============================================================================
# UTILITAIRES ET HELPERS
# =============================================================================

def create_correlation_id() -> str:
    """Crée un ID de corrélation pour tracer les requêtes"""
    return f"CORR-{uuid.uuid4().hex[:12].upper()}"


def is_retryable_error(exception: DatavizFTException) -> bool:
    """Détermine si une erreur peut être retentée"""
    retryable_categories = {
        ErrorCategory.DATABASE_ERROR,
        ErrorCategory.EXTERNAL_API_ERROR,
        ErrorCategory.NETWORK_ERROR,
        ErrorCategory.TIMEOUT_ERROR,
    }
    return exception.category in retryable_categories


def get_user_safe_error(exception: Exception) -> Dict[str, Any]:
    """Retourne une version safe d'une erreur pour l'utilisateur"""
    if isinstance(exception, DatavizFTException):
        return {
            "error_id": exception.error_id,
            "message": exception.user_message,
            "category": "technical_error" if exception.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else "user_error"
        }
    else:
        # Erreur non catégorisée - message générique
        return {
            "error_id": f"DVFT-{uuid.uuid4().hex[:8].upper()}",
            "message": "Une erreur technique est survenue",
            "category": "technical_error"
        }


# =============================================================================
# COMPATIBILITÉ AVEC L'ANCIEN SYSTÈME
# =============================================================================

# Aliases pour compatibilité avec backend/tools/error_handling.py
FranceTravailAPIError = ExternalAPIException
DatabaseConnectionError = DatabaseConnectionException