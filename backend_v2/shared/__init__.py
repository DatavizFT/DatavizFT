"""
Module Shared - DatavizFT Backend v2
===================================

Couche partagée contenant les utilitaires, exceptions et types communs
utilisés dans toutes les couches de l'architecture hexagonale.

Exports principaux :
- Système d'exceptions structuré par couches
- Utilitaires de corrélation et gestion d'erreurs
- Types et constantes communes
"""

# Exports du système d'exceptions
from .exceptions import (
    # Classes de base
    DatavizFTException,
    ErrorCategory,
    ErrorSeverity,
    
    # Exceptions par couche
    DomainException,
    ApplicationException,
    InfrastructureException,
    InterfaceException,
    
    # Exceptions spécialisées - Domain
    InvalidJobDataException,
    CompetenceNotFoundException,
    CompetenceAnalysisException,
    InvalidStatisticsException,
    
    # Exceptions spécialisées - Application
    JobCollectionException,
    StatisticsCalculationException,
    UseCaseTimeoutException,
    
    # Exceptions spécialisées - Infrastructure
    DatabaseConnectionException,
    RepositoryException,
    ExternalAPIException,
    ConfigurationException,
    
    # Exceptions spécialisées - Interface
    APIValidationException,
    AuthenticationException,
    AuthorizationException,
    SerializationException,
    
    # Utilitaires
    create_correlation_id,
    is_retryable_error,
    get_user_safe_error,
    
    # Compatibilité
    FranceTravailAPIError,
    DatabaseConnectionError,
)

# Exports du logger structuré
from .logging import (
    configure_logging,
    get_logger,
    LogExecutionTime,
)

# Logger structuré par défaut pour usage direct
logger = get_logger("datavizft")

__all__ = [
    # Classes de base
    "DatavizFTException",
    "ErrorCategory", 
    "ErrorSeverity",
    
    # Exceptions par couche
    "DomainException",
    "ApplicationException", 
    "InfrastructureException",
    "InterfaceException",
    
    # Exceptions spécialisées - Domain
    "InvalidJobDataException",
    "CompetenceNotFoundException", 
    "CompetenceAnalysisException",
    "InvalidStatisticsException",
    
    # Exceptions spécialisées - Application
    "JobCollectionException",
    "StatisticsCalculationException",
    "UseCaseTimeoutException",
    
    # Exceptions spécialisées - Infrastructure
    "DatabaseConnectionException",
    "RepositoryException",
    "ExternalAPIException", 
    "ConfigurationException",
    
    # Exceptions spécialisées - Interface
    "APIValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "SerializationException",
    
    # Utilitaires
    "create_correlation_id",
    "is_retryable_error", 
    "get_user_safe_error",
    
    # Compatibilité
    "FranceTravailAPIError",
    "DatabaseConnectionError",
    "configure_logging",
    "get_logger",
    "LogExecutionTime",
    "logger",
]