import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, redirect, shorten

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app definition
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST desarrollada con FastAPI para acortar enlaces utilizando "
        "Amazon DynamoDB como almacén de datos, diseñada para ejecutarse en Amazon EC2 "
        "y ser consumida desde una interfaz web alojada en Amazon S3."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Allows requests from S3 static website hosting, CloudFront, or any client
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root information endpoint
@app.get("/", tags=["General"], summary="Información de la API")
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "shorten_url": "POST /shorten",
            "redirect": "GET /{short_code}",
            "get_url_info": "GET /urls/{short_code}",
            "health_check": "GET /health"
        }
    }

# Register routers in priority order
app.include_router(health.router)
app.include_router(shorten.router)
# The redirect router matches /{short_code} so it must be added last
app.include_router(redirect.router)
