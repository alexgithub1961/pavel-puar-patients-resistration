"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router
from src.core.config import get_settings
from src.core.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup - create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Patient Appointment Management System with intelligent slot management",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
# Production origins - add your actual domains here
PRODUCTION_ORIGINS = [
    "https://d2wowd7dw25och.cloudfront.net",  # Patient PWA (CloudFront)
    "https://d24gl9ln0vt8cq.cloudfront.net",  # Doctor PWA (CloudFront)
    "https://patients.example.com",            # Future custom domain
    "https://doctors.example.com",             # Future custom domain
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else PRODUCTION_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled",
    }
