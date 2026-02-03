"""API route aggregation."""

from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.bookings import router as bookings_router
from src.api.routes.doctors import router as doctors_router
from src.api.routes.health import router as health_router
from src.api.routes.patients import router as patients_router
from src.api.routes.slots import router as slots_router

router = APIRouter()

router.include_router(health_router, tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(patients_router, prefix="/patients", tags=["Patients"])
router.include_router(doctors_router, prefix="/doctors", tags=["Doctors"])
router.include_router(slots_router, prefix="/slots", tags=["Slots"])
router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
