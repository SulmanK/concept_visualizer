from fastapi import APIRouter
from .concept import router as concept_router
from .health import router as health_router
from .session import router as session_router
from .concept_storage import router as storage_router
from .svg_conversion import router as svg_router

router = APIRouter()
router.include_router(concept_router, tags=["Concept Generation"], prefix="/concept")
router.include_router(health_router, tags=["Health"], prefix="/health")
router.include_router(session_router, tags=["Session"], prefix="/session")
router.include_router(storage_router, tags=["Concept Storage"], prefix="/storage")
router.include_router(svg_router, tags=["SVG Conversion"], prefix="/svg") 