"""
Configuration Infrastructure - DatavizFT Backend v2
==================================================

Module centralisé pour toutes les configurations de l'infrastructure.
Expose les configurations de retry, database, APIs externes, etc.

Exports principaux :
- Configurations de retry par composant
- Paramètres de circuit breaker
- Helpers de gestion de configuration
"""

# Exports des configurations de retry
from .retry_config import (
    # Classes de configuration
    RetryStrategy,
    CircuitBreakerConfig,
    
    # Configurations spécialisées
    FRANCE_TRAVAIL_RETRY_CONFIG,
    MONGODB_RETRY_CONFIG,
    DEFAULT_RETRY_CONFIG,
    
    # Registries
    RETRY_CONFIGS,
    CIRCUIT_BREAKER_CONFIGS,
    
    # Helpers
    get_retry_config,
    get_circuit_breaker_config,
    is_retryable_for_component,
    calculate_delay,
    get_environment_config,
    validate_retry_config,
    validate_all_configs,
)

__all__ = [
    # Classes de configuration
    "RetryStrategy",
    "CircuitBreakerConfig",
    
    # Configurations spécialisées
    "FRANCE_TRAVAIL_RETRY_CONFIG",
    "MONGODB_RETRY_CONFIG",
    "DEFAULT_RETRY_CONFIG",
    
    # Registries
    "RETRY_CONFIGS",
    "CIRCUIT_BREAKER_CONFIGS",
    
    # Helpers
    "get_retry_config",
    "get_circuit_breaker_config",
    "is_retryable_for_component",
    "calculate_delay",
    "get_environment_config",
    "validate_retry_config",
    "validate_all_configs",
]