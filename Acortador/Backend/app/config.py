import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env file."""

    app_name: str = Field(default="Acortador de Enlaces API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    # AWS & DynamoDB Configuration
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    dynamodb_table_name: str = Field(default="shortened-urls", alias="DYNAMODB_TABLE_NAME")
    dynamodb_endpoint_url: Optional[str] = Field(default=None, alias="DYNAMODB_ENDPOINT_URL")

    # Optional local AWS credentials (for local dev; in EC2 instance IAM role is used)
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = Field(default=None, alias="AWS_SESSION_TOKEN")

    # Public Base URL for generated short links (e.g. http://<ip-publica-ec2>:8000)
    base_url: Optional[str] = Field(default=None, alias="BASE_URL")

    # CORS configuration (comma-separated origins, e.g. "http://bucket.s3-website.amazonaws.com,*" or "*")
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins for CORS middleware."""
        if not self.allowed_origins or self.allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
