from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, AnyHttpUrl

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # --- Run Time ---
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    # --- API Credentials ---
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")

    # --- Database ---
    database_url: PostgresDsn = Field(alias="DATABASE_URL")

    # --- Axiom Logging ---
    enable_axiom: bool = Field(default=False, alias="ENABLE_AXIOM")
    axiom_org_id: str = Field(alias="AXIOM_ORG_ID")
    axiom_dataset: str = Field(alias="AXIOM_DATASET")
    axiom_token: str = Field(alias="AXIOM_TOKEN")

    # --- AWS S3 ---
    aws_bucket_endpoint: AnyHttpUrl = Field(alias="AWS_BUCKET_ENDPOINT")
    aws_bucket_id: str = Field(alias="AWS_BUCKET_ID")
    aws_key_id: str = Field(alias="AWS_KEY_ID")
    aws_secret_key: str = Field(alias="AWS_SECRET_KEY")
    aws_bucket_name: str = Field(alias="AWS_BUCKET_NAME")
    aws_bucket_region: str = Field(alias="AWS_BUCKET_REGION")


    model_config = SettingsConfigDict(
        env_file='.env',        
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'         
    )

settings = Settings() # type: ignore[call-arg]