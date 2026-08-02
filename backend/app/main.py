from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, sessions, settings
from app.database.session import init_db
from app.database import models  # Ensures models are registered with Base metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(title="Lenny Growth Assistant API", lifespan=lifespan)

# Add CORS middleware to support frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(sessions.router)
api_v1_router.include_router(sessions.artifacts_router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(settings.router)

app.include_router(api_v1_router)

# Root level compatibility routes
app.include_router(sessions.router)
app.include_router(sessions.artifacts_router)
app.include_router(chat.router)
app.include_router(settings.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Lenny Growth Assistant"}
