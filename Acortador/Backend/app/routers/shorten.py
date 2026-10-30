from fastapi import APIRouter, Request, status
from app.models import ShortenRequest, ShortenResponse, URLInfoResponse
from app.services import build_short_url, create_short_url, get_url_record

router = APIRouter(tags=["Enlace Corto"])


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un enlace corto",
    description="Recibe una URL original, genera un identificador UUID único, guarda el registro en DynamoDB y devuelve el enlace corto."
)
async def shorten_url(payload: ShortenRequest, request: Request) -> ShortenResponse:
    """Crea un enlace corto asignando un UUID y registrándolo en DynamoDB."""
    result = create_short_url(original_url=payload.original_url, request=request)
    return ShortenResponse(
        short_code=result["short_code"],
        original_url=result["original_url"],
        short_url=result["short_url"]
    )


@router.get(
    "/urls/{short_code}",
    response_model=URLInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar información de un enlace",
    description="Consulta DynamoDB y devuelve los detalles de un enlace acortado por su identificador UUID."
)
async def get_url_info(short_code: str, request: Request) -> URLInfoResponse:
    """Recupera la metadata de un enlace corto desde DynamoDB."""
    record = get_url_record(short_code=short_code)
    short_url = build_short_url(short_code=short_code, request=request)

    return URLInfoResponse(
        short_code=record["short_code"],
        original_url=record["original_url"],
        created_at=record["created_at"],
        short_url=short_url
    )
