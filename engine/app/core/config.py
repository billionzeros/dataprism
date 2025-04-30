from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # --- Project ---
    project_name: str = Field(default="Shooting Star", alias="PROJECT_NAME")

    # --- Run Time ---
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8080, alias="PORT")
    workers: int = Field(default=1, alias="WORKERS", ge=1)

    # --- API Credentials ---
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")

    # --- Database ---
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    db_pool_pre_ping: bool = Field(default=True, alias="DB_POOL_PRE_PING")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE", ge=1) # Default pool size
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW", ge=0) # How many extra connections allowed
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT", ge=1) # Seconds to wait for a connection
    db_pool_recycle: int = Field(default=1800, alias="DB_POOL_RECYCLE", ge=-1) # Recycle connections after 30 mins (-1 to disable)

    # --- Axiom Logging ---
    enable_axiom: bool = Field(default=False, alias="ENABLE_AXIOM")
    axiom_org_id: str = Field(alias="AXIOM_ORG_ID")
    axiom_dataset: str = Field(alias="AXIOM_DATASET")
    axiom_token: str = Field(alias="AXIOM_TOKEN")

    # --- Cloudflare R2 ---
    r2_account_id: str = Field(alias="R2_ACCOUNT_ID")
    r2_access_key_id: str = Field(alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: str = Field(alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = Field(alias="R2_BUCKET_NAME")
    r2_endpoint_url: str = Field(alias="R2_ENDPOINT_URL")


    model_config = SettingsConfigDict(
        env_file='.env',        
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'         
    )

settings = Settings() # type: ignore[call-arg]