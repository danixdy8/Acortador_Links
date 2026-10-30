import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from botocore.exceptions import ClientError
from fastapi import HTTPException, Request, status

from app.config import settings
from app.database import get_url_table

logger = logging.getLogger(__name__)


def build_short_url(short_code: str, request: Optional[Request] = None) -> str:
    """
    Constructs the full short URL.
    Uses BASE_URL environment variable if set, otherwise falls back
    to the incoming HTTP request host.
    """
    if settings.base_url:
        base = settings.base_url.rstrip("/")
    elif request is not None:
        base = str(request.base_url).rstrip("/")
    else:
        base = "http://localhost:8000"
    return f"{base}/{short_code}"


def create_short_url(original_url: str, request: Optional[Request] = None) -> dict:
    """
    Generates a UUID, stores the mapping in DynamoDB, and returns the shortened link data.
    """
    short_code = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    item = {
        "short_code": short_code,
        "original_url": original_url,
        "created_at": created_at
    }

    try:
        table = get_url_table()
        table.put_item(Item=item)
        logger.info("Successfully shortened URL %s to short_code %s", original_url, short_code)
    except ClientError as e:
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        logger.error("Failed to write to DynamoDB: %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar en DynamoDB: {error_msg}"
        )
    except Exception as e:
        logger.error("Unexpected error saving URL: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la solicitud."
        )

    short_url = build_short_url(short_code, request)
    return {
        "short_code": short_code,
        "original_url": original_url,
        "short_url": short_url,
        "created_at": created_at
    }


def get_url_record(short_code: str) -> dict:
    """
    Retrieves a URL record from DynamoDB by short_code (UUID).
    Raises HTTPException 404 if not found.
    """
    try:
        table = get_url_table()
        response = table.get_item(Key={"short_code": short_code})
    except ClientError as e:
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        logger.error("Failed to read from DynamoDB for short_code %s: %s", short_code, error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar DynamoDB: {error_msg}"
        )
    except Exception as e:
        logger.error("Unexpected error querying URL: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al consultar el enlace."
        )

    item = response.get("Item")
    if not item:
        logger.warning("Short code not found: %s", short_code)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El enlace corto con identificador '{short_code}' no existe."
        )

    return item
