from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    """Payload to shorten a new URL."""
    original_url: str = Field(
        ...,
        description="Dirección web original que se desea acortar.",
        examples=["https://www.example.com/articulos/arquitectura-cloud"]
    )

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        clean_url = v.strip()
        if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            raise ValueError("La URL debe comenzar con http:// o https://")
        if len(clean_url) < 10:
            raise ValueError("La URL proporcionada es demasiado corta o inválida.")
        return clean_url


class ShortenResponse(BaseModel):
    """Response returned upon creating a short link."""
    short_code: str = Field(
        ...,
        description="Identificador único generado mediante UUID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    original_url: str = Field(
        ...,
        description="Dirección web original.",
        examples=["https://www.example.com/articulos/arquitectura-cloud"]
    )
    short_url: str = Field(
        ...,
        description="Enlace corto completo para redireccionar al usuario.",
        examples=["http://<ip-publica-ec2>:8000/550e8400-e29b-41d4-a716-446655440000"]
    )


class URLInfoResponse(BaseModel):
    """Information for an existing shortened URL."""
    short_code: str = Field(
        ...,
        description="Identificador UUID del enlace.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    original_url: str = Field(
        ...,
        description="Dirección web original.",
        examples=["https://www.example.com/articulos/arquitectura-cloud"]
    )
    created_at: str = Field(
        ...,
        description="Fecha y hora de creación del enlace (formato ISO 8601).",
        examples=["2026-10-29T23:59:00Z"]
    )
    short_url: Optional[str] = Field(
        default=None,
        description="Enlace corto completo generado."
    )


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    app: str
    version: str
    dynamodb_table: str
    dynamodb_status: str
