from fastapi import FastAPI

from app.api.routes import chat, sessions

app = FastAPI(title="Lenny Growth Assistant API")

app.include_router(sessions.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
