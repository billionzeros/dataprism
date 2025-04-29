import os
from dotenv import load_dotenv

load_dotenv()

def get_required_env(var_name: str) -> str:
    """
    Retrieves a required environment variable.

    Args:
        var_name: The name of the environment variable.

    Returns:
        The value of the environment variable as a string.

    Raises:
        ValueError: If the environment variable is not set.
    """
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set.")
    return value

def get_optional_env(var_name: str) -> str | None:
    """Retrieves an optional environment variable."""
    return os.getenv(var_name)

# Run Time Creds
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# API Creds
GEMINI_API_KEY: str = get_required_env("GEMINI_API_KEY")

# Database Creds
DATABASE_URL: str = get_required_env("DATABASE_URL")

# Axiom Logging Creds
AXIOM_ORG_ID: str = get_required_env("AXIOM_ORG_ID")
AXIOM_DATASET: str = get_required_env("AXIOM_DATASET")
AXIOM_TOKEN: str = get_required_env("AXIOM_TOKEN")

# AWS Creds
AWS_BUCKET_ENDPOINT: str = get_required_env("AWS_BUCKET_ENDPOINT")
AWS_BUCKET_ID: str = get_required_env("AWS_BUCKET_ID")
AWS_KEY_ID: str = get_required_env("AWS_KEY_ID")
AWS_SECRET_KEY: str = get_required_env("AWS_SECRET_KEY")
AWS_BUCKET_NAME: str = get_required_env("AWS_BUCKET_NAME")
AWS_BUCKET_REGION: str = get_required_env("AWS_BUCKET_REGION")
