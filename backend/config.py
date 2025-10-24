# config.py
import os
import logging
import secrets
from dotenv import load_dotenv
from typing import List

load_dotenv()  # Load environment variables from .env file when present

logger = logging.getLogger(__name__)


class Config:
    """Application configuration.

    Attributes are loaded from environment variables. Call `Config.validate()` at
    application startup to ensure required variables are present and to generate
    safe temporary defaults for non-critical secrets in development.
    """

    GROUPME_ACCESS_TOKEN: str | None = os.getenv('GROUPME_ACCESS_TOKEN')
    SECRET_KEY: str | None = os.getenv('SECRET_KEY')
    # Accept EXECUTIVE_PASSWORD or fallback to REACT_APP_EXECUTIVE_PASSWORD for local dev compatibility
    EXECUTIVE_PASSWORD: str | None = os.getenv('EXECUTIVE_PASSWORD') or os.getenv('REACT_APP_EXECUTIVE_PASSWORD')
    # ADMIN_PASSWORD is kept for backward compatibility within the app
    ADMIN_PASSWORD: str | None = None
    MONGODB_URI: str | None = os.getenv('MONGODB_URI')
    # Environment selection: 'dev' or 'prod' (or other custom values)
    ENV: str = os.getenv('ENV') or os.getenv('BACKEND_ENV') or os.getenv('FLASK_ENV') or os.getenv('NODE_ENV') or 'dev'

    # MongoDB database names per environment. You can set one or both of these.
    # If not set, MONGODB_DB is still supported as a fallback.
    MONGODB_DB: str | None = os.getenv('MONGODB_DB')
    MONGODB_DB_DEV: str | None = os.getenv('MONGODB_DB_DEV')
    MONGODB_DB_PROD: str | None = os.getenv('MONGODB_DB_PROD')

    @classmethod
    def MONGODB_DB_NAME(cls) -> str:
        """Return the database name appropriate for the current ENV.

        Resolution order:
        - If ENV == 'dev' and MONGODB_DB_DEV set -> use it
        - If ENV == 'prod' and MONGODB_DB_PROD set -> use it
        - Else use MONGODB_DB if set
        - Else default to 'rhac_db' (backward compatibility)
        """
        env = (cls.ENV or 'dev').lower()
        if env == 'dev' and cls.MONGODB_DB_DEV:
            return cls.MONGODB_DB_DEV
        if env == 'prod' and cls.MONGODB_DB_PROD:
            return cls.MONGODB_DB_PROD
        if cls.MONGODB_DB:
            return cls.MONGODB_DB
        return 'rhac_db'

    @classmethod
    def validate(cls, *, fail_on_missing: bool = True) -> List[str]:
        """Validate environment configuration.

        - Ensures required variables are present (GROUPME_ACCESS_TOKEN, MONGODB_URI).
        - Generates secure temporary SECRET_KEY and EXECUTIVE_PASSWORD if missing
          and logs a warning. These temporaries are appropriate for development
          but should not be used in production.

        Returns a list of missing required variables.
        If `fail_on_missing` is True, a RuntimeError is raised when required vars
        are missing; otherwise missing variables are only logged.
        """

        missing = []
        required = ['GROUPME_ACCESS_TOKEN', 'MONGODB_URI']
        for var in required:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            msg = f"Missing required environment variables: {', '.join(missing)}"
            if fail_on_missing:
                logger.error(msg)
                raise RuntimeError(msg)
            else:
                logger.warning(msg)

        # SECRET_KEY: generate a secure temporary one if not set
        if not cls.SECRET_KEY:
            cls.SECRET_KEY = secrets.token_urlsafe(32)
            # Use INFO level to reduce alarming warnings during development reloads
            logger.info(
                "SECRET_KEY is not set. Generated a temporary SECRET_KEY for development. "
                "Set SECRET_KEY in the environment for production deployments."
            )

        # EXECUTIVE_PASSWORD / ADMIN_PASSWORD: generate temporary admin password if missing
        if not cls.EXECUTIVE_PASSWORD:
            temp_pw = secrets.token_urlsafe(16)
            cls.EXECUTIVE_PASSWORD = temp_pw
            logger.info(
                "EXECUTIVE_PASSWORD is not set. A temporary admin password has been generated. "
                "Set EXECUTIVE_PASSWORD in the environment to a stable value for production."
            )

        # Expose ADMIN_PASSWORD attribute used by the app
        cls.ADMIN_PASSWORD = cls.EXECUTIVE_PASSWORD

        return missing

