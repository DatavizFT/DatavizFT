"""
Configuration des stratégies de retry - DatavizFT Backend v2
===========================================================

Configuration centralisée pour la gestion des tentatives automatiques
en cas d'erreurs transitoires. Utilise le système d'exceptions de shared/.

Patterns supportés :
- Backoff exponentiel avec jitter
- Retry conditionnel par catégorie d'erreur
- Circuit breaker configurable
- Timeouts adaptatifs
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from backend_v2.shared.exceptions import ErrorCategory


@dataclass
class RetryStrategy:
    """Configuration d'une stratégie de retry"""
    
    max_retries: int
    base_delay: float
    max_delay: float
    backoff_type: str = "exponential"  # "exponential", "linear", "constant"
    jitter: bool = True
    timeout_multiplier: float = 1.0
    retryable_categories: List[ErrorCategory] = None
    
    def __post_init__(self):
        if self.retryable_categories is None:
            # Par défaut, toutes les catégories retryables
            self.retryable_categories = [
                ErrorCategory.DATABASE_ERROR,
                ErrorCategory.EXTERNAL_API_ERROR,
                ErrorCategory.NETWORK_ERROR,
                ErrorCategory.TIMEOUT_ERROR,
            ]


@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    half_open_max_calls: int = 1


# =============================================================================
# CONFIGURATIONS PAR COMPOSANT
# =============================================================================

# Configuration France Travail API
FRANCE_TRAVAIL_RETRY_CONFIG = RetryStrategy(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    backoff_type="exponential",
    jitter=True,
    timeout_multiplier=1.5,
    retryable_categories=[
        ErrorCategory.EXTERNAL_API_ERROR,
        ErrorCategory.NETWORK_ERROR,
        ErrorCategory.TIMEOUT_ERROR,
    ]
)

# Configuration MongoDB
MONGODB_RETRY_CONFIG = RetryStrategy(
    max_retries=5,
    base_delay=0.5,
    max_delay=30.0,
    backoff_type="exponential",
    jitter=True,
    timeout_multiplier=1.2,
    retryable_categories=[
        ErrorCategory.DATABASE_ERROR,
        ErrorCategory.NETWORK_ERROR,
    ]
)



# Configuration générique (fallback)
DEFAULT_RETRY_CONFIG = RetryStrategy(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    backoff_type="exponential",
    jitter=True,
    timeout_multiplier=1.0
)

# =============================================================================
# REGISTRY DES CONFIGURATIONS
# =============================================================================

RETRY_CONFIGS: Dict[str, RetryStrategy] = {
    # APIs externes
    "france_travail_api": FRANCE_TRAVAIL_RETRY_CONFIG,
    "external_api": FRANCE_TRAVAIL_RETRY_CONFIG,
    
    # Base de données
    "mongodb": MONGODB_RETRY_CONFIG,
    "database": MONGODB_RETRY_CONFIG,
    
    # Configuration par défaut
    "default": DEFAULT_RETRY_CONFIG,
}

# =============================================================================
# CONFIGURATIONS CIRCUIT BREAKER
# =============================================================================

CIRCUIT_BREAKER_CONFIGS: Dict[str, CircuitBreakerConfig] = {
    "france_travail_api": CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout_seconds=60,
        half_open_max_calls=1
    ),
    "mongodb": CircuitBreakerConfig(
        failure_threshold=10,
        success_threshold=5,
        timeout_seconds=30,
        half_open_max_calls=2
    ),
    "default": CircuitBreakerConfig()
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_retry_config(component: str) -> RetryStrategy:
    """Récupère la configuration de retry pour un composant"""
    return RETRY_CONFIGS.get(component, DEFAULT_RETRY_CONFIG)


def get_circuit_breaker_config(component: str) -> CircuitBreakerConfig:
    """Récupère la configuration de circuit breaker pour un composant"""
    return CIRCUIT_BREAKER_CONFIGS.get(component, CIRCUIT_BREAKER_CONFIGS["default"])


def is_retryable_for_component(exception, component: str) -> bool:
    """Vérifie si une exception est retryable pour un composant spécifique"""
    from backend_v2.shared.exceptions import DatavizFTException, is_retryable_error
    
    if not isinstance(exception, DatavizFTException):
        return False
    
    # Vérification générale
    if not is_retryable_error(exception):
        return False
    
    # Vérification spécifique au composant
    config = get_retry_config(component)
    return exception.category in config.retryable_categories


def calculate_delay(attempt: int, config: RetryStrategy) -> float:
    """Calcule le délai pour une tentative donnée"""
    import random
    import math
    
    if config.backoff_type == "exponential":
        delay = config.base_delay * (2 ** attempt)
    elif config.backoff_type == "linear":
        delay = config.base_delay * (attempt + 1)
    else:  # constant
        delay = config.base_delay
    
    # Limiter le délai maximum
    delay = min(delay, config.max_delay)
    
    # Ajouter du jitter pour éviter le thundering herd
    if config.jitter:
        jitter_amount = delay * 0.1  # 10% de jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    return max(0, delay)


# =============================================================================
# CONFIGURATION ENVIRONNEMENTALE
# =============================================================================

def get_environment_config() -> Dict[str, RetryStrategy]:
    """Configuration adaptée à l'environnement (dev/test/prod)"""
    import os
    
    env = os.getenv("DATAVIZ_ENV", "development").lower()
    
    if env == "production":
        # En production : retry plus agressif
        return {
            **RETRY_CONFIGS,
            "france_travail_api": RetryStrategy(
                max_retries=5,
                base_delay=2.0,
                max_delay=120.0,
                backoff_type="exponential",
                jitter=True,
                timeout_multiplier=2.0,
                retryable_categories=FRANCE_TRAVAIL_RETRY_CONFIG.retryable_categories
            )
        }
    elif env == "test":
        # En test : retry minimal pour la rapidité
        return {
            **RETRY_CONFIGS,
            "default": RetryStrategy(
                max_retries=1,
                base_delay=0.1,
                max_delay=1.0,
                backoff_type="constant",
                jitter=False,
                timeout_multiplier=1.0,
                retryable_categories=DEFAULT_RETRY_CONFIG.retryable_categories
            )
        }
    else:
        # Développement : configuration standard
        return RETRY_CONFIGS


# =============================================================================
# VALIDATION DE CONFIGURATION
# =============================================================================

def validate_retry_config(config: RetryStrategy) -> bool:
    """Valide une configuration de retry"""
    if config.max_retries < 0:
        return False
    if config.base_delay <= 0:
        return False
    if config.max_delay < config.base_delay:
        return False
    if config.backoff_type not in ["exponential", "linear", "constant"]:
        return False
    return True


def validate_all_configs() -> List[str]:
    """Valide toutes les configurations et retourne les erreurs"""
    errors = []
    
    for name, config in RETRY_CONFIGS.items():
        if not validate_retry_config(config):
            errors.append(f"Configuration invalide pour {name}")
    
    return errors


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Classes
    "RetryStrategy",
    "CircuitBreakerConfig",
    
    # Configurations principales
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