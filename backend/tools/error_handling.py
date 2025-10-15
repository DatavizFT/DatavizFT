"""
Gestionnaire d'erreurs centralisé pour DatavizFT
"""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime

from pydantic import BaseModel


class ErrorCategory(str, Enum):
    """Catégories d'erreurs pour classification"""

    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    SYSTEM_ERROR = "system_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"


class ErrorSeverity(str, Enum):
    """Niveaux de sévérité des erreurs"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DatavizError(BaseModel):
    """Modèle standardisé pour les erreurs"""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
    user_message: Optional[str] = None  # Message safe pour l'utilisateur

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class DatavizFTException(Exception):
    """Exception de base pour DatavizFT"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ):
        super().__init__(message)
        self.error = DatavizError(
            error_id=self._generate_error_id(),
            category=category,
            severity=severity,
            message=message,
            details=details or {},
            user_message=user_message or "Une erreur est survenue",
        )

    def _generate_error_id(self) -> str:
        """Génère un ID unique pour l'erreur"""
        from uuid import uuid4

        return f"DVFT-{uuid4().hex[:8].upper()}"


# Exceptions spécialisées
class FranceTravailAPIError(DatavizFTException):
    """Erreur API France Travail"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"Erreur API France Travail: {message}",
            category=ErrorCategory.EXTERNAL_SERVICE_ERROR,
            severity=ErrorSeverity.HIGH,
            details={"status_code": status_code},
            user_message="Service France Travail temporairement indisponible",
        )


class CompetenceAnalysisError(DatavizFTException):
    """Erreur lors de l'analyse des compétences"""

    def __init__(self, message: str, offre_id: Optional[str] = None):
        super().__init__(
            message=f"Erreur analyse compétences: {message}",
            category=ErrorCategory.BUSINESS_LOGIC_ERROR,
            severity=ErrorSeverity.MEDIUM,
            details={"offre_id": offre_id},
            user_message="Erreur lors de l'analyse des compétences",
        )


class DatabaseConnectionError(DatavizFTException):
    """Erreur de connexion base de données"""

    def __init__(self, message: str, db_type: str = "MongoDB"):
        super().__init__(
            message=f"Erreur connexion {db_type}: {message}",
            category=ErrorCategory.DATABASE_ERROR,
            severity=ErrorSeverity.CRITICAL,
            details={"db_type": db_type},
            user_message="Base de données temporairement indisponible",
        )


# Gestionnaire central d'erreurs
class ErrorManager:
    """Gestionnaire centralisé des erreurs"""

    @staticmethod
    def handle_error(
        error: Exception, logger: Any, context: Optional[Dict[str, Any]] = None
    ) -> DatavizError:
        """Traite une erreur de manière centralisée"""

        if isinstance(error, DatavizFTException):
            error_obj = error.error
        else:
            # Erreur non catégorisée
            error_obj = DatavizError(
                error_id=f"DVFT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message=str(error),
                details={"context": context, "type": type(error).__name__},
            )

        # Log structuré
        logger.error(
            "Error occurred",
            error_id=error_obj.error_id,
            category=error_obj.category,
            severity=error_obj.severity,
            message=error_obj.message,
            details=error_obj.details,
            context=context,
        )

        # Notification selon la sévérité
        if error_obj.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            ErrorManager._notify_critical_error(error_obj)

        return error_obj

    @staticmethod
    def _notify_critical_error(error: DatavizError) -> None:
        """Notifie les erreurs critiques (Slack, email, Sentry...)"""
        # TODO: Implémenter notifications
        print(f"🚨 CRITICAL ERROR: {error.error_id} - {error.message}")


# Décorateurs pour gestion automatique d'erreurs
def handle_exceptions(
    category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_message: str = "Une erreur est survenue",
):
    """Décorateur pour gestion automatique des exceptions"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DatavizFTException:
                raise  # Re-raise les erreurs déjà catégorisées
            except Exception as e:
                raise DatavizFTException(
                    message=f"Erreur dans {func.__name__}: {str(e)}",
                    category=category,
                    severity=severity,
                    user_message=user_message,
                ) from e

        return wrapper

    return decorator
