"""
Configuration DatavizFT - Variables d'environnement
Centralise toutes les configurations de l'application
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration centralisée pour DatavizFT"""

    # -----------------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------------
    APP_NAME: str = os.getenv("APP_NAME", "DatavizFT")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # -----------------------------------------------------------------------------
    # API France Travail
    # -----------------------------------------------------------------------------
    FRANCETRAVAIL_CLIENT_ID: Optional[str] = os.getenv("FRANCETRAVAIL_CLIENT_ID")
    FRANCETRAVAIL_CLIENT_SECRET: Optional[str] = os.getenv("FRANCETRAVAIL_CLIENT_SECRET")
    TOKEN_URL: str = os.getenv("TOKEN_URL", "https://francetravail.io/connexion/oauth2/access_token?realm=%2Fpartenaire")
    API_BASE_URL: str = "https://api.francetravail.io/partenaire/offresdemploi/v2"

    # Limites API
    FRANCE_TRAVAIL_RATE_LIMIT: int = int(os.getenv("FRANCE_TRAVAIL_RATE_LIMIT", "200"))
    FRANCE_TRAVAIL_MAX_RESULTS: int = int(os.getenv("FRANCE_TRAVAIL_MAX_RESULTS", "1000"))
    FRANCE_TRAVAIL_TIMEOUT: int = int(os.getenv("FRANCE_TRAVAIL_TIMEOUT", "30"))

    # -----------------------------------------------------------------------------
    # MongoDB
    # -----------------------------------------------------------------------------
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL", 
        "mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin"
    )
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "dataviz_ft_dev")
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))

    # Authentification MongoDB
    MONGODB_ADMIN_USERNAME: str = os.getenv("MONGODB_ADMIN_USERNAME", "admin")
    MONGODB_ADMIN_PASSWORD: str = os.getenv("MONGODB_ADMIN_PASSWORD", "datavizft2025")
    MONGODB_APP_USERNAME: str = os.getenv("MONGODB_APP_USERNAME", "datavizft_app")
    MONGODB_APP_PASSWORD: str = os.getenv("MONGODB_APP_PASSWORD", "secure_app_password")

    # Configuration avancée MongoDB
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_CONNECT_TIMEOUT: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT", "10000"))
    MONGODB_SOCKET_TIMEOUT: int = int(os.getenv("MONGODB_SOCKET_TIMEOUT", "30000"))
    MONGODB_SERVER_SELECTION_TIMEOUT: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "5000"))

    # -----------------------------------------------------------------------------
    # Pipeline Configuration
    # -----------------------------------------------------------------------------
    PIPELINE_BATCH_SIZE: int = int(os.getenv("PIPELINE_BATCH_SIZE", "100"))
    PIPELINE_MAX_WORKERS: int = int(os.getenv("PIPELINE_MAX_WORKERS", "4"))
    PIPELINE_RETRY_COUNT: int = int(os.getenv("PIPELINE_RETRY_COUNT", "3"))
    PIPELINE_RETRY_DELAY: int = int(os.getenv("PIPELINE_RETRY_DELAY", "5"))

    # Nettoyage automatique
    AUTO_CLEANUP_ENABLED: bool = os.getenv("AUTO_CLEANUP_ENABLED", "true").lower() == "true"
    AUTO_CLEANUP_DAYS: int = int(os.getenv("AUTO_CLEANUP_DAYS", "365"))
    AUTO_CLEANUP_HOUR: int = int(os.getenv("AUTO_CLEANUP_HOUR", "2"))

    # Compétences
    COMPETENCES_MIN_LENGTH: int = int(os.getenv("COMPETENCES_MIN_LENGTH", "2"))
    COMPETENCES_MAX_LENGTH: int = int(os.getenv("COMPETENCES_MAX_LENGTH", "50"))
    COMPETENCES_BLACKLIST: list[str] = os.getenv(
        "COMPETENCES_BLACKLIST", 
        "a,le,la,les,de,du,des,et,ou,pour,avec"
    ).split(",")

    # -----------------------------------------------------------------------------
    # Security
    # -----------------------------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

    # -----------------------------------------------------------------------------
    # Performance & Monitoring
    # -----------------------------------------------------------------------------
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))

    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))

    # -----------------------------------------------------------------------------
    # Development Tools
    # -----------------------------------------------------------------------------
    MONGO_EXPRESS_ENABLED: bool = os.getenv("MONGO_EXPRESS_ENABLED", "true").lower() == "true"
    MONGO_EXPRESS_PORT: int = int(os.getenv("MONGO_EXPRESS_PORT", "8081"))
    MONGO_EXPRESS_USERNAME: str = os.getenv("MONGO_EXPRESS_USERNAME", "datavizft")
    MONGO_EXPRESS_PASSWORD: str = os.getenv("MONGO_EXPRESS_PASSWORD", "admin123")

    HOT_RELOAD: bool = os.getenv("HOT_RELOAD", "true").lower() == "true"
    WATCH_FILES: bool = os.getenv("WATCH_FILES", "true").lower() == "true"

    @classmethod
    def get_mongodb_url(cls) -> str:
        """
        Retourne l'URL MongoDB configurée
        
        Returns:
            URL de connexion MongoDB
        """
        return cls.MONGODB_URL

    @classmethod
    def is_development(cls) -> bool:
        """
        Vérifie si on est en mode développement
        
        Returns:
            True si développement
        """
        return cls.APP_ENV == "development"

    @classmethod
    def is_production(cls) -> bool:
        """
        Vérifie si on est en mode production
        
        Returns:
            True si production
        """
        return cls.APP_ENV == "production"

    @classmethod
    def get_log_config(cls) -> dict:
        """
        Configuration des logs
        
        Returns:
            Configuration de logging
        """
        return {
            "level": cls.LOG_LEVEL,
            "format": "json" if cls.is_production() else "console",
            "file": "logs/dataviz_ft.log" if cls.is_production() else None,
        }


# Instances pour compatibilité avec l'ancien code
FRANCETRAVAIL_CLIENT_ID = Config.FRANCETRAVAIL_CLIENT_ID
FRANCETRAVAIL_CLIENT_SECRET = Config.FRANCETRAVAIL_CLIENT_SECRET
TOKEN_URL = Config.TOKEN_URL
API_BASE_URL = Config.API_BASE_URL
