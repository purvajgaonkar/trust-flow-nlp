"""
FastAPI Application – Trust Flow main entry point.
"""

import sys
from pathlib import Path

# Ensure backend root is always in sys.path regardless of execution directory
_backend_root = str(Path(__file__).resolve().parent.parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.endpoints import router

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan (startup/shutdown)
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("═══════════════════════════════════════════")
    logger.info("  Trust Flow v%s starting up...", settings.APP_VERSION)
    logger.info("═══════════════════════════════════════════")

    # Pre-load models at startup
    try:
        from app.nlp.analyzer import nlp_analyzer
        logger.info("✓ NLP Analyzer ready (spaCy: %s)", "ok" if nlp_analyzer.nlp else "fallback")
    except Exception as e:
        logger.warning("✗ NLP Analyzer init warning: %s", e)

    try:
        from app.security.semantic import semantic_detector
        logger.info("✓ Semantic Detector ready (model: %s)", "ok" if semantic_detector.model else "mock")
    except Exception as e:
        logger.warning("✗ Semantic Detector init warning: %s", e)

    try:
        from app.security.transformer import transformer_classifier
        logger.info("✓ Transformer Classifier ready (mock: %s)", transformer_classifier.is_mock)
    except Exception as e:
        logger.warning("✗ Transformer Classifier init warning: %s", e)

    try:
        from app.knowledge_graph.graph import knowledge_graph
        logger.info("✓ Knowledge Graph loaded (%d nodes)", knowledge_graph.graph.number_of_nodes())
    except Exception as e:
        logger.warning("✗ Knowledge Graph init warning: %s", e)

    logger.info("Trust Flow ready. Environment: %s", settings.ENVIRONMENT)
    yield
    logger.info("Trust Flow shutting down.")


# ─────────────────────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Trust Flow API",
    description=(
        "Intelligent NLP Security & Reliability Framework for LLMs. "
        "Detects prompt injection, jailbreaks, obfuscation, and hallucinations."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method, request.url.path, response.status_code, elapsed,
    )
    return response


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "type": type(exc).__name__},
    )


# ── Include API router ────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "Trust Flow",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
