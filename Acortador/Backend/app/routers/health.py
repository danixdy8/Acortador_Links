from fastapi import APIRouter
from app.config import settings
from app.database import check_dynamodb_connection
from app.models import HealthResponse

router = APIRouter(tags=["Salud del Servicio"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar el estado del servicio y conexión a DynamoDB"
)
async def health_check() -> HealthResponse:
    """Verifica si la API y la conexión a DynamoDB están funcionando."""
    is_connected, status_msg = check_dynamodb_connection()

    return HealthResponse(
        status="healthy" if is_connected else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        dynamodb_table=settings.dynamodb_table_name,
        dynamodb_status=status_msg
    )
