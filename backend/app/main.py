from fastapi import FastAPI

from app.api.routes import sessions

app = FastAPI(title="Lenny Growth Assistant API")

app.include_router(sessions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
