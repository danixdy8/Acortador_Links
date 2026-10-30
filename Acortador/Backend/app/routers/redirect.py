import logging
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from app.services import get_url_record

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Redirección"])


@router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redireccionar a la URL original",
    description="Recupera la URL original desde DynamoDB a partir del UUID y ejecuta una redirección HTTP 307 hacia el destino.",
    responses={
        307: {"description": "Redirección temporal a la URL original de destino."},
        404: {"description": "El identificador UUID no existe en DynamoDB."}
    }
)
async def redirect_to_original(short_code: str) -> RedirectResponse:
    """Busca el registro en DynamoDB y redirige el navegador al destino original."""
    record = get_url_record(short_code=short_code)
    destination = record["original_url"]
    logger.info("Redirecting %s -> %s", short_code, destination)
    return RedirectResponse(
        url=destination,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
