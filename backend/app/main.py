import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base, SessionLocal
from app.routers import auth, resume, interview, dashboard, health
from app.config import settings
from app.logging_config import setup_logging
from app.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize structured logging
    setup_logging()
    logger.info("InterviewForge AI starting up (ENV=%s)", settings.ENV)

    # Database tables are managed by Alembic migrations (handled separately)
    
    # Seed question bank if empty
    db = SessionLocal()
    try:
        from app.seeds import seed_questions
        seed_questions(db)
        logger.info("Question bank seeding complete.")
    finally:
        db.close()
        
    yield
    logger.info("InterviewForge AI shutting down.")

app = FastAPI(
    title="InterviewForge AI API",
    description="Adaptive AI-powered interview preparation platform backend API.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware ---

# Rate limiting (slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(dashboard.router)
app.include_router(health.router)

@app.get("/")
def read_root():
    return {
        "app": "InterviewForge AI Backend API",
        "status": "online",
        "version": "1.0.0",
        "database": "sqlite (fallback)" if settings.get_db_url.startswith("sqlite") else "postgresql"
    }
